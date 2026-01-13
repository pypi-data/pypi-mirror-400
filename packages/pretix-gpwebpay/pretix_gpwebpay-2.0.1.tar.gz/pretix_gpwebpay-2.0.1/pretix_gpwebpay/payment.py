"""
GPWebPay payment provider for Pretix.

This module implements the GPWebPay payment gateway integration for Pretix,
providing secure payment processing with RSA-SHA256 signature verification
according to GPWebPay HTTP API specification v1.19.
"""
import hashlib
import logging
import urllib.parse
from decimal import Decimal
from typing import Dict, Optional

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from django import forms
from django.conf import settings
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from pretix.base.models import Order, OrderPayment, OrderRefund
from pretix.base.payment import BasePaymentProvider, PaymentException
from pretix.control.forms import ExtFileField

logger = logging.getLogger(__name__)


class GPWebPaySettingsForm(forms.Form):
    """
    Configuration form for GPWebPay payment provider settings.
    
    Collects merchant credentials, key files, and gateway configuration
    required for GPWebPay payment processing.
    """
    merchant_number = forms.CharField(
        label=_('Merchant Number'),
        help_text=_('Your GPWebPay merchant number'),
        required=True,
        max_length=20,
    )
    private_key = ExtFileField(
        label=_('Private Key File'),
        help_text=_('Upload your GPWebPay private key file (.key or .pem format)'),
        required=True,
        ext_whitelist=('.key', '.pem', '.txt'),
    )
    private_key_password = forms.CharField(
        label=_('Private Key Password'),
        help_text=_('Password for your private key file'),
        required=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
    )
    public_key = ExtFileField(
        label=_('GPWebPay Public Key File (Optional)'),
        help_text=_('Upload the GPWebPay public key file for signature verification. If not provided, signature verification will be skipped (less secure).'),
        required=False,
        ext_whitelist=('.key', '.pem', '.txt'),
    )
    gateway_url = forms.URLField(
        label=_('Gateway URL'),
        help_text=_('GPWebPay gateway URL (e.g., https://3dsecure.gpwebpay.com/pgw/order.do)'),
        required=True,
        initial='https://3dsecure.gpwebpay.com/pgw/order.do',
    )
    test_mode = forms.BooleanField(
        label=_('Test mode'),
        help_text=_('Enable test mode for development'),
        required=False,
        initial=False,
    )


class GPWebPay(BasePaymentProvider):
    """
    GPWebPay payment provider implementation for Pretix.
    
    Handles payment processing, signature generation, and verification
    according to GPWebPay HTTP API specification v1.19.
    """
    identifier = 'gpwebpay'
    verbose_name = _('GPWebPay')
    public_name = _('GPWebPay')
    abort_pending_allowed = True
    refunds_allowed = False

    @property
    def settings_form_fields(self):
        return GPWebPaySettingsForm.base_fields

    def settings_form_clean(self, cleaned_data, request):
        """
        Process file uploads and store them as strings.
        
        Pretix's ExtFileField returns a file object that needs to be
        converted to a string for storage in the settings.
        """
        if 'private_key' in cleaned_data and cleaned_data['private_key']:
            file = cleaned_data['private_key']
            if hasattr(file, 'read'):
                file.seek(0)
                try:
                    cleaned_data['private_key'] = file.read().decode('utf-8')
                except UnicodeDecodeError:
                    file.seek(0)
                    import base64
                    cleaned_data['private_key'] = base64.b64encode(file.read()).decode('utf-8')
                file.seek(0)

        if 'public_key' in cleaned_data and cleaned_data['public_key']:
            file = cleaned_data['public_key']
            if hasattr(file, 'read'):
                file.seek(0)
                try:
                    cleaned_data['public_key'] = file.read().decode('utf-8')
                except UnicodeDecodeError:
                    file.seek(0)
                    import base64
                    cleaned_data['public_key'] = base64.b64encode(file.read()).decode('utf-8')
                file.seek(0)

        return cleaned_data

    def settings_content_render(self, request):
        return """
        <p>Configure your GPWebPay payment gateway settings.</p>
        <p>You need to:</p>
        <ul>
            <li>Obtain your merchant number from GPWebPay</li>
            <li>Upload your private key file (used for signing requests)</li>
            <li>Upload GPWebPay's public key file (optional - used for verifying responses)</li>
            <li>Configure the gateway URL (use test URL for testing)</li>
        </ul>
        <p><strong>Note:</strong> If you don't have GPWebPay's public key, signature verification will be skipped. 
        This is less secure but payments will still work. It's recommended to obtain the public key from GPWebPay support.</p>
        """

    def payment_form_render(self, request) -> str:
        """
        Render payment form HTML.
        
        For GPWebPay, customers are redirected immediately to the gateway,
        so no form is displayed.
        """
        return ""

    def checkout_confirm_render(self, request) -> str:
        """
        Render checkout confirmation page HTML.
        
        Displays information about the GPWebPay payment method and
        informs customers they will be redirected to the gateway.
        """
        return """
        <div class="alert alert-info">
            <p><strong>GPWebPay Payment</strong></p>
            <p>You will be redirected to the GPWebPay secure payment gateway to complete your payment.</p>
        </div>
        """

    def payment_is_valid_session(self, request):
        """
        Validate payment session.
        
        Returns True as GPWebPay redirects immediately to the gateway
        without requiring session validation.
        """
        return True

    def execute_payment(self, request: HttpRequest, payment: OrderPayment) -> Optional[HttpResponse]:
        """
        Execute the payment by redirecting to GPWebPay gateway.
        """
        order = payment.order
        event = order.event

        settings_dict = self.settings
        merchant_number = settings_dict.get('merchant_number', '')
        gateway_url = settings_dict.get('gateway_url', 'https://3dsecure.gpwebpay.com/pgw/order.do')
        private_key_data = settings_dict.get('private_key', '')
        private_key_password = settings_dict.get('private_key_password', '')

        if not merchant_number or not private_key_data:
            raise PaymentException(_('GPWebPay is not configured properly.'))

        params = {
            'MERCHANTNUMBER': merchant_number,
            'OPERATION': 'CREATE_ORDER',
            'ORDERNUMBER': str(payment.id),
            'AMOUNT': str(int(payment.amount * 100)),
            'CURRENCY': self._get_currency_code(order.currency),
            'DEPOSITFLAG': '0',
            'URL': request.build_absolute_uri(
                reverse('plugins:pretix_gpwebpay:return', kwargs={
                    'order': order.code,
                    'payment': payment.id,
                    'hash': payment.order.secret
                })
            ),
            'DESCRIPTION': f'Order {order.code}',
            'MD': str(payment.id),
        }

        try:
            digest = self._generate_digest(params)
            signature = self._sign_message(digest, private_key_data, private_key_password)
            params['DIGEST'] = signature
        except Exception as e:
            logger.error(f'GPWebPay signing error: {e}', exc_info=True)
            raise PaymentException(_('Error preparing payment request.'))

        return HttpResponseRedirect(f"{gateway_url}?{urllib.parse.urlencode(params)}")

    def _get_currency_code(self, currency: str) -> str:
        """
        Convert ISO 4217 currency code to GPWebPay numeric format.
        
        Args:
            currency: ISO 4217 currency code (e.g., 'EUR', 'USD')
            
        Returns:
            GPWebPay numeric currency code (defaults to EUR if not found)
        """
        currency_map = {
            'CZK': '203',
            'EUR': '978',
            'USD': '840',
            'GBP': '826',
            'PLN': '985',
            'HUF': '348',
        }
        return currency_map.get(currency.upper(), '978')

    def _generate_digest(self, params: Dict[str, str]) -> str:
        """
        Generate digest string from parameters according to GPWebPay specification.
        
        The digest format is: MERCHANTNUMBER|OPERATION|ORDERNUMBER|AMOUNT|CURRENCY|
        DEPOSITFLAG|MERORDERNUM|URL|DESCRIPTION|MD
        
        Args:
            params: Dictionary of payment parameters
            
        Returns:
            Digest string with parameters joined by pipe character
        """
        digest_parts = [
            params.get('MERCHANTNUMBER', ''),
            params.get('OPERATION', ''),
            params.get('ORDERNUMBER', ''),
            params.get('AMOUNT', ''),
            params.get('CURRENCY', ''),
            params.get('DEPOSITFLAG', ''),
            params.get('MERORDERNUM', ''),
            params.get('URL', ''),
            params.get('DESCRIPTION', ''),
            params.get('MD', ''),
        ]
        return '|'.join(digest_parts)

    def _sign_message(self, message: str, private_key_data: str, password: Optional[str] = None) -> str:
        """
        Sign a message using RSA private key with SHA-256.
        
        Implements GPWebPay specification: RSA-SHA256 with PKCS1v15 padding.
        The private key must be in PEM format.
        
        Args:
            message: Message to sign
            private_key_data: Private key in PEM format (may be base64-encoded)
            password: Optional password for encrypted private key
            
        Returns:
            Base64-encoded signature
            
        Raises:
            Exception: If key loading or signing fails
        """
        import base64

        try:
            if private_key_data.startswith('-----BEGIN'):
                key_bytes = private_key_data.encode('utf-8')
            else:
                try:
                    key_bytes = base64.b64decode(private_key_data)
                    if not key_bytes.startswith(b'-----BEGIN'):
                        raise ValueError('Key is not in PEM format')
                except Exception:
                    key_bytes = private_key_data.encode('utf-8')

            password_bytes = password.encode('utf-8') if password else None
            private_key = serialization.load_pem_private_key(
                key_bytes,
                password=password_bytes,
                backend=default_backend()
            )

            signature = private_key.sign(
                message.encode('utf-8'),
                padding.PKCS1v15(),
                hashes.SHA256()
            )

            return base64.b64encode(signature).decode('utf-8')
        except Exception as e:
            logger.error(f'Error signing message: {e}', exc_info=True)
            raise

    def _verify_signature(self, message: str, signature: str, public_key_data: str) -> bool:
        """
        Verify a signature using RSA public key with SHA-256.
        
        Implements GPWebPay specification: RSA-SHA256 with PKCS1v15 padding.
        The public key must be in PEM format.
        
        Args:
            message: Original message that was signed
            signature: Base64-encoded signature to verify
            public_key_data: Public key in PEM format (may be base64-encoded)
            
        Returns:
            True if signature is valid, False otherwise
        """
        import base64

        try:
            if public_key_data.startswith('-----BEGIN'):
                key_bytes = public_key_data.encode('utf-8')
            else:
                try:
                    key_bytes = base64.b64decode(public_key_data)
                    if not key_bytes.startswith(b'-----BEGIN'):
                        raise ValueError('Key is not in PEM format')
                except Exception:
                    key_bytes = public_key_data.encode('utf-8')

            public_key = serialization.load_pem_public_key(
                key_bytes,
                backend=default_backend()
            )

            signature_bytes = base64.b64decode(signature)

            public_key.verify(
                signature_bytes,
                message.encode('utf-8'),
                padding.PKCS1v15(),
                hashes.SHA256()
            )
            return True
        except Exception as e:
            logger.error(f'Error verifying signature: {e}', exc_info=True)
            return False

    def payment_pending_render(self, request, payment: OrderPayment):
        """
        Render HTML for pending payment status.
        
        Args:
            request: HTTP request object
            payment: OrderPayment instance
            
        Returns:
            HTML string to display while payment is pending
        """
        return f"""
        <p>{_('Your payment is being processed.')}</p>
        <p>{_('Please wait...')}</p>
        """

    def payment_control_render(self, request, payment: OrderPayment):
        """
        Render payment information in the control panel.
        
        Args:
            request: HTTP request object
            payment: OrderPayment instance
            
        Returns:
            HTML string displaying payment details
        """
        return f"""
        <dl class="dl-horizontal">
            <dt>{_('Payment ID')}</dt>
            <dd>{payment.id}</dd>
            <dt>{_('Status')}</dt>
            <dd>{payment.state}</dd>
        </dl>
        """

