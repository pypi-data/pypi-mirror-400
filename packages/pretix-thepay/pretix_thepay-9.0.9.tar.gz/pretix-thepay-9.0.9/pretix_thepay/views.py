"""
Views for handling The Pay payment gateway callbacks.

This module provides views for processing user redirects and server-to-server
notifications from the The Pay payment gateway, including signature verification
and payment status updates.
"""
import logging
from django.contrib import messages
from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse, NoReverseMatch
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django_scopes import scopes_disabled
from pretix.base.models import OrderPayment

logger = logging.getLogger(__name__)


def _order_redirect_url(request, order) -> str:
    if hasattr(order, 'get_absolute_url'):
        return order.get_absolute_url()
    if hasattr(order, 'get_detail_url'):
        return order.get_detail_url()
    if hasattr(order, 'get_url'):
        return order.get_url()
    if hasattr(order, 'get_presale_url'):
        return order.get_presale_url()
    try:
        patterns = [
            ('presale:event.order', {
                'organizer': order.event.organizer.slug,
                'event': order.event.slug,
                'code': order.code,
                'secret': order.secret,
            }),
            ('presale:event.order', {
                'event': order.event.slug,
                'code': order.code,
                'secret': order.secret,
            }),
            ('presale:event.order.by_code', {
                'organizer': order.event.organizer.slug,
                'event': order.event.slug,
                'code': order.code,
                'secret': order.secret,
            }),
            ('presale:event.order.by_code', {
                'event': order.event.slug,
                'code': order.code,
                'secret': order.secret,
            }),
        ]
        for name, kwargs in patterns:
            try:
                return reverse(name, kwargs=kwargs)
            except NoReverseMatch:
                continue
    except Exception:
        pass
    try:
        organizer = order.event.organizer.slug
        event = order.event.slug
        code = order.code
        secret = order.secret
        path = f'/{organizer}/{event}/order/{code}/{secret}/'
        return request.build_absolute_uri(path)
    except Exception:
        return '/'


@method_decorator(csrf_exempt, name='dispatch')
class ReturnView(View):
    """
    Handle user redirect return from The Pay payment gateway.
    
    Processes the payment response when the customer is redirected back
    from the The Pay gateway after completing or canceling payment.
    """

    def get(self, request: HttpRequest, order: str, payment: int, hash: str):
        return self._handle_response(request, order, payment, hash)

    def post(self, request: HttpRequest, order: str, payment: int, hash: str):
        return self._handle_response(request, order, payment, hash)

    def _handle_response(self, request: HttpRequest, order: str, payment: int, hash: str):
        """
        Process The Pay return response.
        
        Verifies the payment signature, checks payment status,
        and updates the payment state accordingly.
        
        Args:
            request: HTTP request containing The Pay response parameters
            order: Order code
            payment: Payment ID
            hash: Order secret hash for validation
        """
        try:
            with scopes_disabled():
                payment_obj = get_object_or_404(
                    OrderPayment,
                    id=payment,
                    order__code=order,
                    order__secret=hash
                )
            order_obj = payment_obj.order
            event = order_obj.event

            # Get payment provider
            from pretix.base.models import Event
            provider = event.get_payment_providers().get('thepay')
            if not provider:
                logger.error('The Pay provider not found')
                messages.error(request, _('Payment provider not configured.'))
                return redirect(order_obj.get_abandon_url())

            # Get settings
            settings_dict = provider.settings
            api_password = settings_dict.get('api_password', '')

            # Get response parameters
            # The Pay return URL includes payment_uid and project_id
            payment_uid = (
                request.GET.get('payment_uid', '') or request.POST.get('payment_uid', '') or
                request.GET.get('uid', '') or request.POST.get('uid', '')
            )
            signature = request.GET.get('signature', '') or request.POST.get('signature', '')

            # If no payment_uid from callback, extract from payment.info (stored during creation)
            if not payment_uid:
                payment_info = payment_obj.info_data or {}
                payment_uid = payment_info.get('payment_uid') or payment_info.get('uid')
                # Fallback: reconstruct from stored pattern
                if not payment_uid:
                    payment_uid = f'pretix-{payment_obj.id}-{order_obj.code}'

            # Verify signature if provided
            if signature and api_password:
                params = dict(request.GET.items()) if request.method == 'GET' else dict(request.POST.items())
                params.pop('signature', None)  # Remove signature from params for verification
                
                if not provider._verify_signature(params, signature, api_password):
                    logger.error('The Pay signature verification failed')
                    messages.error(request, _('Payment verification failed.'))
                    return redirect(order_obj.get_abandon_url())

            # Always query payment status via API (per The Pay spec)
            payment_state = None
            if payment_uid:
                merchant_id = settings_dict.get('merchant_id', '')
                project_id = settings_dict.get('project_id', '')
                test_mode = settings_dict.get('test_mode', False)
                api_url = provider._get_api_url(test_mode).rstrip('/')
                payment_state = provider._get_payment_status(
                    payment_uid, merchant_id, project_id, api_password, api_url
                )
                logger.info('The Pay return status for payment %s (uid=%s): %s', payment, payment_uid, payment_state)

            # Check payment status
            # The Pay payment states: 'paid', 'waiting_for_payment', 'expired', 'error', etc.
            # According to OpenAPI spec: Enum_PaymentState
            if payment_state == 'paid':
                allowed_states = {OrderPayment.PAYMENT_STATE_PENDING}
                created_state = getattr(OrderPayment, 'PAYMENT_STATE_CREATED', None)
                if created_state:
                    allowed_states.add(created_state)
                if payment_obj.state in allowed_states:
                    logger.info('The Pay payment %s state before confirm: %s', payment, payment_obj.state)
                    payment_obj.confirm()
                    logger.info('The Pay payment %s confirmed for order %s', payment, order)
                    messages.success(request, _('Payment successful!'))
                else:
                    logger.info('The Pay payment %s already in state %s; skipping confirm', payment, payment_obj.state)
                return redirect(_order_redirect_url(request, order_obj))
            elif payment_state in ('expired', 'error', 'preauth_cancelled', 'preauth_expired'):
                error_msg = _('Payment failed or expired.')
                if payment_obj.state == OrderPayment.PAYMENT_STATE_PENDING:
                    payment_obj.fail(info={'error': f'Payment state: {payment_state}'})
                    logger.warning(f'The Pay payment {payment} failed for order {order}: {payment_state}')
                messages.error(request, error_msg)
                return redirect(order_obj.get_abandon_url())
            elif payment_state in ('waiting_for_payment', 'waiting_for_confirmation', 'preauthorized'):
                # Payment is still processing
                logger.info(f'The Pay payment {payment} is still processing: {payment_state}')
                return redirect(_order_redirect_url(request, order_obj))
            else:
                # Unknown status or no status - keep pending
                if payment_state:
                    logger.warning(f'The Pay payment {payment} returned unknown status: {payment_state}')
                else:
                    logger.warning(f'The Pay payment {payment} - no status in callback and API query failed')
                return redirect(_order_redirect_url(request, order_obj))

        except Exception as e:
            logger.error(f'Error processing The Pay return: {e}', exc_info=True)
            messages.error(request, _('An error occurred while processing your payment.'))
            try:
                return redirect(order_obj.get_abandon_url())
            except:
                return HttpResponseBadRequest('Error processing payment')


@method_decorator(csrf_exempt, name='dispatch')
class NotifyView(View):
    """
    Handle server-to-server notification (IPN) from The Pay payment gateway.
    
    Processes asynchronous payment notifications sent by The Pay to confirm
    payment status independently of user redirect.
    """

    def get(self, request: HttpRequest, order: str, payment: int, hash: str):
        return self._handle_notification(request, order, payment, hash)

    def post(self, request: HttpRequest, order: str, payment: int, hash: str):
        return self._handle_notification(request, order, payment, hash)

    def _handle_notification(self, request: HttpRequest, order: str, payment: int, hash: str):
        """
        Process The Pay server notification.
        
        Verifies the notification signature, checks payment status,
        and updates the payment state. Returns HTTP 200 OK on success.
        
        Args:
            request: HTTP request containing The Pay notification parameters
            order: Order code
            payment: Payment ID
            hash: Order secret hash for validation
        """
        try:
            with scopes_disabled():
                payment_obj = get_object_or_404(
                    OrderPayment,
                    id=payment,
                    order__code=order,
                    order__secret=hash
                )
            order_obj = payment_obj.order
            event = order_obj.event

            # Get payment provider
            from pretix.base.models import Event
            provider = event.get_payment_providers().get('thepay')
            if not provider:
                logger.error('The Pay provider not found')
                return HttpResponseBadRequest('Provider not configured')

            # Get settings
            settings_dict = provider.settings
            api_password = settings_dict.get('api_password', '')

            # Get notification parameters
            # The Pay notifications include: payment_uid, project_id, type
            payment_uid = (
                request.GET.get('payment_uid', '') or request.POST.get('payment_uid', '') or
                request.GET.get('uid', '') or request.POST.get('uid', '')
            )
            signature = request.GET.get('signature', '') or request.POST.get('signature', '')

            # If no payment_uid from notification, extract from payment.info (stored during creation)
            if not payment_uid:
                payment_info = payment_obj.info_data or {}
                payment_uid = payment_info.get('payment_uid') or payment_info.get('uid')
                # Fallback: reconstruct from stored pattern
                if not payment_uid:
                    payment_uid = f'pretix-{payment_obj.id}-{order_obj.code}'

            # Verify signature if provided
            if signature and api_password:
                params = dict(request.GET.items()) if request.method == 'GET' else dict(request.POST.items())
                params.pop('signature', None)
                
                if not provider._verify_signature(params, signature, api_password):
                    logger.error('The Pay notification signature verification failed')
                    return HttpResponseBadRequest('Invalid signature')

            # Always query payment status via API (per The Pay spec)
            payment_state = None
            if payment_uid:
                merchant_id = settings_dict.get('merchant_id', '')
                project_id = settings_dict.get('project_id', '')
                test_mode = settings_dict.get('test_mode', False)
                api_url = provider._get_api_url(test_mode).rstrip('/')
                payment_state = provider._get_payment_status(
                    payment_uid, merchant_id, project_id, api_password, api_url
                )
                logger.info('The Pay notify status for payment %s (uid=%s): %s', payment, payment_uid, payment_state)

            # Process payment status
            # The Pay payment states: 'paid', 'waiting_for_payment', 'expired', 'error', etc.
            # Notification type 'state_changed' indicates payment state has changed
            if payment_state == 'paid':
                allowed_states = {OrderPayment.PAYMENT_STATE_PENDING}
                created_state = getattr(OrderPayment, 'PAYMENT_STATE_CREATED', None)
                if created_state:
                    allowed_states.add(created_state)
                if payment_obj.state in allowed_states:
                    logger.info('The Pay payment %s state before confirm (notify): %s', payment, payment_obj.state)
                    payment_obj.confirm()
                    logger.info('The Pay payment %s confirmed via notification for order %s', payment, order)
                else:
                    logger.info('The Pay payment %s already in state %s; skipping confirm', payment, payment_obj.state)
            elif payment_state in ('expired', 'error', 'preauth_cancelled', 'preauth_expired'):
                if payment_obj.state == OrderPayment.PAYMENT_STATE_PENDING:
                    payment_obj.fail(info={'error': f'Payment state: {payment_state}'})
                    logger.warning(f'The Pay payment {payment} failed via notification for order {order}: {payment_state}')

            return HttpResponse('OK')

        except Exception as e:
            logger.error(f'Error processing The Pay notification: {e}', exc_info=True)
            return HttpResponseBadRequest('Error processing notification')
