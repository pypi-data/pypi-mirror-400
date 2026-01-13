"""
Views for handling GPWebPay payment gateway callbacks.

This module provides views for processing user redirects and server-to-server
notifications from the GPWebPay payment gateway, including signature verification
and payment status updates.
"""
import logging
import urllib.parse
from decimal import Decimal

from django.contrib import messages
from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest
from django.shortcuts import redirect, get_object_or_404
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from pretix.base.models import Order, OrderPayment
from pretix.base.payment import PaymentException
from pretix.multidomain import subdomain_urlconf

logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name='dispatch')
class ReturnView(View):
    """
    Handle user redirect return from GPWebPay payment gateway.
    
    Processes the payment response when the customer is redirected back
    from the GPWebPay gateway after completing or canceling payment.
    """

    def get(self, request: HttpRequest, order: str, payment: int, hash: str):
        return self._handle_response(request, order, payment, hash)

    def post(self, request: HttpRequest, order: str, payment: int, hash: str):
        return self._handle_response(request, order, payment, hash)

    def _handle_response(self, request: HttpRequest, order: str, payment: int, hash: str):
        """
        Process GPWebPay return response.
        
        Verifies the payment signature, checks payment status codes,
        and updates the payment state accordingly.
        
        Args:
            request: HTTP request containing GPWebPay response parameters
            order: Order code
            payment: Payment ID
            hash: Order secret hash for validation
        """
        try:
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
            provider = event.get_payment_providers().get('gpwebpay')
            if not provider:
                logger.error('GPWebPay provider not found')
                messages.error(request, _('Payment provider not configured.'))
                return redirect(order_obj.get_abandon_url())

            # Get settings
            settings_dict = provider.settings
            public_key_data = settings_dict.get('public_key', '')

            operation = request.GET.get('OPERATION', '') or request.POST.get('OPERATION', '')
            ordernumber = request.GET.get('ORDERNUMBER', '') or request.POST.get('ORDERNUMBER', '')
            merchantnumber = request.GET.get('MERCHANTNUMBER', '') or request.POST.get('MERCHANTNUMBER', '')
            prcode = request.GET.get('PRCODE', '') or request.POST.get('PRCODE', '')
            srcode = request.GET.get('SRCODE', '') or request.POST.get('SRCODE', '')
            resulttext = request.GET.get('RESULTTEXT', '') or request.POST.get('RESULTTEXT', '')
            digest = request.GET.get('DIGEST', '') or request.POST.get('DIGEST', '')
            digest1 = request.GET.get('DIGEST1', '') or request.POST.get('DIGEST1', '')

            if digest1 and public_key_data:
                response_digest_parts = [
                    operation,
                    ordernumber,
                ]
                
                merordernum = request.GET.get('MERORDERNUM', '') or request.POST.get('MERORDERNUM', '')
                md = request.GET.get('MD', '') or request.POST.get('MD', '')
                details = request.GET.get('DETAILS', '') or request.POST.get('DETAILS', '')
                userparam1 = request.GET.get('USERPARAM1', '') or request.POST.get('USERPARAM1', '')
                addinfo = request.GET.get('ADDINFO', '') or request.POST.get('ADDINFO', '')
                
                if merordernum:
                    response_digest_parts.append(merordernum)
                if md:
                    response_digest_parts.append(md)
                response_digest_parts.extend([prcode, srcode, resulttext])
                if details:
                    response_digest_parts.append(details)
                if userparam1:
                    response_digest_parts.append(userparam1)
                if addinfo:
                    response_digest_parts.append(addinfo)
                response_digest_parts.append(merchantnumber)
                
                response_digest = '|'.join(response_digest_parts)

                if not provider._verify_signature(response_digest, digest1, public_key_data):
                    logger.error('GPWebPay signature verification failed')
                    messages.error(request, _('Payment verification failed.'))
                    return redirect(order_obj.get_abandon_url())
            elif digest1 and not public_key_data:
                logger.warning('GPWebPay signature provided but public key not configured - skipping verification (less secure)')

            if prcode == '0' and srcode == '0':
                if payment_obj.state == OrderPayment.PAYMENT_STATE_PENDING:
                    payment_obj.confirm()
                    logger.info(f'GPWebPay payment {payment} confirmed for order {order}')
                    messages.success(request, _('Payment successful!'))
                    return redirect(order_obj.get_absolute_url())
                else:
                    return redirect(order_obj.get_absolute_url())
            else:
                error_msg = resulttext or _('Payment failed.')
                if payment_obj.state == OrderPayment.PAYMENT_STATE_PENDING:
                    payment_obj.fail(info={'error': error_msg})
                    logger.warning(f'GPWebPay payment {payment} failed for order {order}: {error_msg}')
                messages.error(request, error_msg)
                return redirect(order_obj.get_abandon_url())

        except Exception as e:
            logger.error(f'Error processing GPWebPay return: {e}', exc_info=True)
            messages.error(request, _('An error occurred while processing your payment.'))
            try:
                return redirect(order_obj.get_abandon_url())
            except:
                return HttpResponseBadRequest('Error processing payment')


@method_decorator(csrf_exempt, name='dispatch')
class NotifyView(View):
    """
    Handle server-to-server notification (IPN) from GPWebPay payment gateway.
    
    Processes asynchronous payment notifications sent by GPWebPay to confirm
    payment status independently of user redirect.
    """

    def get(self, request: HttpRequest, order: str, payment: int, hash: str):
        return self._handle_notification(request, order, payment, hash)

    def post(self, request: HttpRequest, order: str, payment: int, hash: str):
        return self._handle_notification(request, order, payment, hash)

    def _handle_notification(self, request: HttpRequest, order: str, payment: int, hash: str):
        """
        Process GPWebPay server notification.
        
        Verifies the notification signature, checks payment status codes,
        and updates the payment state. Returns HTTP 200 OK on success.
        
        Args:
            request: HTTP request containing GPWebPay notification parameters
            order: Order code
            payment: Payment ID
            hash: Order secret hash for validation
        """
        try:
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
            provider = event.get_payment_providers().get('gpwebpay')
            if not provider:
                logger.error('GPWebPay provider not found')
                return HttpResponseBadRequest('Provider not configured')

            # Get settings
            settings_dict = provider.settings
            public_key_data = settings_dict.get('public_key', '')

            operation = request.GET.get('OPERATION', '') or request.POST.get('OPERATION', '')
            ordernumber = request.GET.get('ORDERNUMBER', '') or request.POST.get('ORDERNUMBER', '')
            merchantnumber = request.GET.get('MERCHANTNUMBER', '') or request.POST.get('MERCHANTNUMBER', '')
            prcode = request.GET.get('PRCODE', '') or request.POST.get('PRCODE', '')
            srcode = request.GET.get('SRCODE', '') or request.POST.get('SRCODE', '')
            resulttext = request.GET.get('RESULTTEXT', '') or request.POST.get('RESULTTEXT', '')
            digest1 = request.GET.get('DIGEST1', '') or request.POST.get('DIGEST1', '')

            if digest1 and public_key_data:
                response_digest_parts = [
                    operation,
                    ordernumber,
                ]
                
                merordernum = request.GET.get('MERORDERNUM', '') or request.POST.get('MERORDERNUM', '')
                md = request.GET.get('MD', '') or request.POST.get('MD', '')
                details = request.GET.get('DETAILS', '') or request.POST.get('DETAILS', '')
                userparam1 = request.GET.get('USERPARAM1', '') or request.POST.get('USERPARAM1', '')
                addinfo = request.GET.get('ADDINFO', '') or request.POST.get('ADDINFO', '')
                
                if merordernum:
                    response_digest_parts.append(merordernum)
                if md:
                    response_digest_parts.append(md)
                response_digest_parts.extend([prcode, srcode, resulttext])
                if details:
                    response_digest_parts.append(details)
                if userparam1:
                    response_digest_parts.append(userparam1)
                if addinfo:
                    response_digest_parts.append(addinfo)
                response_digest_parts.append(merchantnumber)
                
                response_digest = '|'.join(response_digest_parts)

                if not provider._verify_signature(response_digest, digest1, public_key_data):
                    logger.error('GPWebPay notification signature verification failed')
                    return HttpResponseBadRequest('Invalid signature')
            elif digest1 and not public_key_data:
                logger.warning('GPWebPay notification signature provided but public key not configured - skipping verification (less secure)')

            if prcode == '0' and srcode == '0':
                if payment_obj.state == OrderPayment.PAYMENT_STATE_PENDING:
                    payment_obj.confirm()
                    logger.info(f'GPWebPay payment {payment} confirmed via notification for order {order}')
            else:
                if payment_obj.state == OrderPayment.PAYMENT_STATE_PENDING:
                    payment_obj.fail(info={'error': resulttext or 'Payment failed'})
                    logger.warning(f'GPWebPay payment {payment} failed via notification for order {order}')

            return HttpResponse('OK')

        except Exception as e:
            logger.error(f'Error processing GPWebPay notification: {e}', exc_info=True)
            return HttpResponseBadRequest('Error processing notification')

