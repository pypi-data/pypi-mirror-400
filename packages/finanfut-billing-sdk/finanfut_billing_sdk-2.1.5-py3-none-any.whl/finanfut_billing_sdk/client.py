"""Synchronous client for the Finanfut Billing External API."""

from __future__ import annotations

from typing import Any, Callable, Type, TypeVar, cast
from uuid import UUID, uuid4
import warnings

import requests
from pydantic import BaseModel

from .providers import ProvidersClient
from .errors import (
    FinanfutBillingAuthError,
    FinanfutBillingHTTPError,
    FinanfutBillingServiceError,
    FinanfutBillingValidationError,
)
from .models import (
    ExternalClientUpsertRequest,
    ExternalClientUpsertResponse,
    ExternalCheckoutCreateRequest,
    ExternalCheckoutCreateResponse,
    ExternalCheckoutSessionCreateRequest,
    ExternalCheckoutSessionResponse,
    ExternalConnectOnboardRequest,
    ExternalConnectOnboardResponse,
    ExternalInvoiceCreateRequest,
    ExternalInvoiceCreateResponse,
    ExternalInvoiceDetailResponse,
    ExternalInvoiceEmailRequest,
    ExternalInvoiceEmailResponse,
    ExternalPaymentCreateRequest,
    ExternalPaymentCreateResponse,
    ExternalProviderUpsertRequest,
    ExternalProviderUpsertResponse,
    ExternalServiceUpsertRequest,
    ExternalServiceUpsertResponse,
    ExternalTaxRateListResponse,
    ExternalPaymentSessionResponse,
    PartnerPaymentMethod,
    PartnerPaymentMethodCreate,
    Settlement,
    SettlementCreate,
    SettlementFinalizeOptions,
    SettlementPayoutCreate,
)

_ResponseModel = TypeVar("_ResponseModel", bound=BaseModel)


class FinanfutBillingClient:
    """Synchronous client for Finanfut Billing External API (v1)."""

    def __init__(
        self, base_url: str, api_key: str, timeout: float = 10.0, business_unit_id: UUID | str | None = None
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout
        self.business_unit_id = str(business_unit_id) if business_unit_id is not None else None
        self.settlements = SettlementsClient(self)
        self.partner_payment_methods = PartnerPaymentMethodsClient(self)
        self.providers = ProvidersClient(self)
        self.payments = PaymentsClient(self)

    # Public API methods -------------------------------------------------
    def upsert_client(self, payload: ExternalClientUpsertRequest) -> ExternalClientUpsertResponse:
        """Create or update a client by external reference."""

        return self._post(
            "/external/v1/clients/upsert",
            payload.model_dump(exclude_none=True, by_alias=True),
            ExternalClientUpsertResponse,
        )

    def upsert_service(
        self, payload: ExternalServiceUpsertRequest, *, business_unit_id: UUID | str | None = None
    ) -> ExternalServiceUpsertResponse:
        """Create or update a service/product scoped to a business unit."""

        effective_bu = self._resolve_business_unit_id(
            override=business_unit_id,
            payload_value=payload.business_unit_id,
            required=False,
            endpoint="services/upsert",
        )
        payload_with_bu = payload if effective_bu is None else payload.model_copy(update={"business_unit_id": effective_bu})

        return self._post(
            "/external/v1/services/upsert",
            payload_with_bu.model_dump(exclude_none=True, by_alias=True),
            ExternalServiceUpsertResponse,
        )

    def list_tax_rates(
        self,
        *,
        category: str | None = None,
        code: str | None = None,
    ) -> ExternalTaxRateListResponse:
        """Return active tax rates."""

        self._warn_if_business_unit_unused("tax-rates")
        params = {"category": category, "code": code}
        return self._get(
            "/external/v1/tax-rates",
            ExternalTaxRateListResponse,
            params={k: v for k, v in params.items() if v is not None},
        )

    def create_invoice(
        self, payload: ExternalInvoiceCreateRequest, *, business_unit_id: UUID | str | None = None
    ) -> ExternalInvoiceCreateResponse:
        """Create an invoice and return its identifiers."""

        effective_bu = self._resolve_business_unit_id(
            override=business_unit_id,
            payload_value=payload.business_unit_id,
            required=False,
            endpoint="invoices/create",
        )
        payload_with_bu = payload if effective_bu is None else payload.model_copy(update={"business_unit_id": effective_bu})

        return self._post(
            "/external/v1/invoices/create",
            payload_with_bu.model_dump(exclude_none=True, by_alias=True),
            ExternalInvoiceCreateResponse,
        )

    def get_invoice(self, invoice_id: UUID | str) -> ExternalInvoiceDetailResponse:
        """Retrieve invoice details by ID."""

        return self._get(
            f"/external/v1/invoices/{invoice_id}",
            ExternalInvoiceDetailResponse,
        )

    def send_invoice_email(
        self,
        invoice_id: UUID | str,
        payload: ExternalInvoiceEmailRequest,
    ) -> ExternalInvoiceEmailResponse:
        """Send an invoice PDF via email."""

        return self._post(
            f"/external/v1/invoices/{invoice_id}/send-email",
            payload.model_dump(exclude_none=True, by_alias=True),
            ExternalInvoiceEmailResponse,
        )

    def register_payment(
        self,
        invoice_id: UUID | str,
        payload: ExternalPaymentCreateRequest,
    ) -> ExternalPaymentCreateResponse:
        """Register a payment for an invoice."""

        return self._post(
            f"/external/v1/invoices/{invoice_id}/payments",
            payload.model_dump(exclude_none=True, by_alias=True),
            ExternalPaymentCreateResponse,
        )

    # Internal helpers ---------------------------------------------------
    def _headers(self, extra: dict[str, str] | None = None) -> dict[str, str]:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        if extra:
            headers.update(extra)
        return headers

    def _get(
        self,
        path: str,
        model: Type[_ResponseModel],
        *,
        params: dict[str, Any] | None = None,
        many: bool = False,
        headers: dict[str, str] | None = None,
    ) -> _ResponseModel | list[_ResponseModel]:
        return self._request(requests.get, path, model, params=params, many=many, headers=headers)

    def _post(
        self,
        path: str,
        data: dict[str, Any],
        model: Type[_ResponseModel],
        *,
        many: bool = False,
        headers: dict[str, str] | None = None,
    ) -> _ResponseModel | list[_ResponseModel]:
        return self._request(requests.post, path, model, json=data, many=many, headers=headers)

    def _request(
        self,
        method: Callable[..., requests.Response],
        path: str,
        model: Type[_ResponseModel],
        *,
        params: dict[str, Any] | None = None,
        many: bool = False,
        headers: dict[str, str] | None = None,
        **kwargs: Any,
    ) -> _ResponseModel | list[_ResponseModel]:
        url = f"{self.base_url}{path}"
        response = method(
            url,
            headers=self._headers(headers),
            timeout=self.timeout,
            params=params,
            **kwargs,
        )
        return self._handle_response(response, model, many=many)

    def _resolve_business_unit_id(
        self,
        *,
        override: UUID | str | None,
        payload_value: UUID | str | None,
        required: bool,
        endpoint: str,
    ) -> str | None:
        selected = override if override is not None else payload_value
        if selected is None:
            selected = self.business_unit_id

        if required and selected is None:
            raise FinanfutBillingValidationError(
                f"business_unit_id is required for {endpoint}", status_code=None, payload=None
            )

        if selected is None:
            return None
        return str(selected)

    def _warn_if_business_unit_unused(self, endpoint: str, override: UUID | str | None = None) -> None:
        business_unit = override if override is not None else self.business_unit_id
        if business_unit is None:
            return
        warnings.warn(
            f"business_unit_id is ignored for {endpoint}; the endpoint is company-scoped.",
            stacklevel=2,
        )

    def _handle_response(
        self,
        response: requests.Response,
        model: Type[_ResponseModel],
        *,
        many: bool = False,
    ) -> _ResponseModel | list[_ResponseModel]:
        content_type = response.headers.get("content-type", "")
        is_json = "application/json" in content_type
        payload: Any | None = response.json() if is_json else None

        if 200 <= response.status_code < 300:
            if payload is None:
                raise FinanfutBillingHTTPError("Expected JSON response", status_code=response.status_code)
            if many:
                if not isinstance(payload, list):
                    raise FinanfutBillingHTTPError(
                        "Expected list response", status_code=response.status_code, payload=payload
                    )
                return [model.model_validate(item) for item in payload]
            return model.model_validate(payload)

        if response.status_code in {401, 403}:
            raise FinanfutBillingAuthError("Authentication failed", status_code=response.status_code, payload=payload)

        if response.status_code == 422:
            raise FinanfutBillingValidationError(
                "Request validation failed",
                status_code=response.status_code,
                payload=payload,
            )

        if isinstance(payload, dict) and payload.get("error"):
            raise FinanfutBillingServiceError(
                payload.get("message", "Service error"),
                error=payload.get("error"),
                request_id=payload.get("request_id"),
                status_code=response.status_code,
                payload=payload,
            )

        raise FinanfutBillingHTTPError(
            f"Unexpected HTTP {response.status_code}",
            status_code=response.status_code,
            payload=payload,
        )


class SettlementsClient:
    """Client helper for settlement workflows."""

    def __init__(self, transport: FinanfutBillingClient) -> None:
        self._transport = transport

    def create_settlement(
        self,
        payload: SettlementCreate,
        *,
        business_unit_id: UUID | str | None = None,
        idempotency_key: str | None = None,
    ) -> Settlement:
        effective_bu = self._transport._resolve_business_unit_id(
            override=business_unit_id,
            payload_value=payload.business_unit_id,
            required=False,
            endpoint="settlements/create",
        )
        payload_with_bu = payload if effective_bu is None else payload.model_copy(update={"business_unit_id": effective_bu})
        headers = {"Idempotency-Key": idempotency_key or str(uuid4())}
        return cast(
            Settlement,
            self._transport._post(
                "/external/v1/settlements",
                payload_with_bu.model_dump(exclude_none=True, by_alias=True),
                Settlement,
                headers=headers,
            ),
        )

    def get_settlement(self, settlement_id: UUID | str) -> Settlement:
        return cast(
            Settlement,
            self._transport._get(f"/external/v1/settlements/{settlement_id}", Settlement),
        )

    def list_settlements(self, status: str | None = None) -> list[Settlement]:
        response = self._transport._get(
            "/external/v1/settlements", Settlement, params={"status": status} if status else None, many=True
        )
        return cast(list[Settlement], response)

    def finalize_settlement(
        self,
        settlement_id: UUID | str,
        payload: SettlementFinalizeOptions | None = None,
        *,
        idempotency_key: str | None = None,
    ) -> Settlement:
        headers = {"Idempotency-Key": idempotency_key or str(uuid4())}
        return cast(
            Settlement,
            self._transport._post(
                f"/external/v1/settlements/{settlement_id}/finalize",
                payload.model_dump(exclude_none=True, by_alias=True) if payload else {},
                Settlement,
                headers=headers,
            ),
        )

    def register_payout(
        self,
        settlement_id: UUID | str,
        payload: SettlementPayoutCreate,
        *,
        idempotency_key: str | None = None,
    ) -> Settlement:
        headers = {"Idempotency-Key": idempotency_key or str(uuid4())}
        return cast(
            Settlement,
            self._transport._post(
                f"/external/v1/settlements/{settlement_id}/payout",
                payload.model_dump(exclude_none=True, by_alias=True),
                Settlement,
                headers=headers,
            ),
        )


class PartnerPaymentMethodsClient:
    """Client helper for partner payment methods."""

    def __init__(self, transport: FinanfutBillingClient) -> None:
        self._transport = transport

    def create_partner_payment_method(self, payload: PartnerPaymentMethodCreate) -> PartnerPaymentMethod:
        self._transport._warn_if_business_unit_unused("partner-payment-methods")
        return cast(
            PartnerPaymentMethod,
            self._transport._post(
                "/external/v1/partner-payment-methods",
                payload.model_dump(exclude_none=True, by_alias=True),
                PartnerPaymentMethod,
            ),
        )

    def list_partner_payment_methods(
        self, client_id: UUID | str | None = None, provider_id: UUID | str | None = None
    ) -> list[PartnerPaymentMethod]:
        self._transport._warn_if_business_unit_unused("partner-payment-methods")
        response = self._transport._get(
            "/external/v1/partner-payment-methods",
            PartnerPaymentMethod,
            params={
                "client_id": str(client_id) if client_id else None,
                "provider_id": str(provider_id) if provider_id else None,
            },
            many=True,
        )
        return cast(list[PartnerPaymentMethod], response)

    def get_partner_payment_method(self, method_id: UUID | str) -> PartnerPaymentMethod:
        self._transport._warn_if_business_unit_unused("partner-payment-methods")
        return cast(
            PartnerPaymentMethod,
            self._transport._get(
                f"/external/v1/partner-payment-methods/{method_id}",
                PartnerPaymentMethod,
            ),
        )

    def set_default_partner_payment_method(self, method_id: UUID | str) -> PartnerPaymentMethod:
        self._transport._warn_if_business_unit_unused("partner-payment-methods")
        return cast(
            PartnerPaymentMethod,
            self._transport._post(
                f"/external/v1/partner-payment-methods/{method_id}/set-default",
                {},
                PartnerPaymentMethod,
            ),
        )

    def deactivate_partner_payment_method(self, method_id: UUID | str) -> PartnerPaymentMethod:
        self._transport._warn_if_business_unit_unused("partner-payment-methods")
        return cast(
            PartnerPaymentMethod,
            self._transport._request(
                requests.delete,
                f"/external/v1/partner-payment-methods/{method_id}",
                PartnerPaymentMethod,
            ),
        )


class PaymentsClient:
    """Client helper for external payment provider actions."""

    def __init__(self, transport: FinanfutBillingClient) -> None:
        self._transport = transport

    def create_checkout(
        self,
        provider: str,
        payload: ExternalCheckoutCreateRequest,
        *,
        business_unit_id: UUID | str | None = None,
        idempotency_key: str | None = None,
    ) -> ExternalCheckoutCreateResponse:
        effective_bu = self._transport._resolve_business_unit_id(
            override=business_unit_id,
            payload_value=payload.business_unit_id,
            required=False,
            endpoint="payments/create_checkout",
        )
        payload_with_bu = (
            payload if effective_bu is None else payload.model_copy(update={"business_unit_id": effective_bu})
        )
        return cast(
            ExternalCheckoutCreateResponse,
            self._transport._post(
                f"/external/v1/payments/{provider}/create_checkout",
                payload_with_bu.model_dump(exclude_none=True, by_alias=True),
                ExternalCheckoutCreateResponse,
                headers={"Idempotency-Key": idempotency_key or str(uuid4())},
            ),
        )

    def create_checkout_session(
        self,
        payload: ExternalCheckoutSessionCreateRequest,
        *,
        idempotency_key: str | None = None,
    ) -> ExternalCheckoutSessionResponse:
        return cast(
            ExternalCheckoutSessionResponse,
            self._transport._post(
                "/external/v1/payments/stripe/checkout-session",
                payload.model_dump(exclude_none=True, by_alias=True),
                ExternalCheckoutSessionResponse,
                headers={"Idempotency-Key": idempotency_key or str(uuid4())},
            ),
        )

    def expire_checkout_session(
        self,
        session_id: UUID | str,
        *,
        idempotency_key: str | None = None,
    ) -> ExternalPaymentSessionResponse:
        return cast(
            ExternalPaymentSessionResponse,
            self._transport._post(
                f"/external/v1/payments/stripe/checkout-session/{session_id}/expire",
                {},
                ExternalPaymentSessionResponse,
                headers={"Idempotency-Key": idempotency_key or str(uuid4())},
            ),
        )

    def list_payment_sessions(
        self,
        *,
        business_unit_id: UUID | str | None = None,
        reference_type: str | None = None,
        reference_id: str | None = None,
        status: str | None = None,
    ) -> list[ExternalPaymentSessionResponse]:
        params = {
            "business_unit_id": str(business_unit_id) if business_unit_id else None,
            "reference_type": reference_type,
            "reference_id": reference_id,
            "status": status,
        }
        response = self._transport._get(
            "/external/v1/payments/sessions",
            ExternalPaymentSessionResponse,
            params={k: v for k, v in params.items() if v is not None},
            many=True,
        )
        return cast(list[ExternalPaymentSessionResponse], response)

    def get_payment_session(self, session_id: UUID | str) -> ExternalPaymentSessionResponse:
        return cast(
            ExternalPaymentSessionResponse,
            self._transport._get(
                f"/external/v1/payments/sessions/{session_id}",
                ExternalPaymentSessionResponse,
            ),
        )

    def connect_onboard(
        self,
        provider: str,
        payload: ExternalConnectOnboardRequest,
        *,
        business_unit_id: UUID | str | None = None,
    ) -> ExternalConnectOnboardResponse:
        effective_bu = self._transport._resolve_business_unit_id(
            override=business_unit_id,
            payload_value=payload.business_unit_id,
            required=False,
            endpoint="payments/connect_onboard",
        )
        payload_with_bu = (
            payload if effective_bu is None else payload.model_copy(update={"business_unit_id": effective_bu})
        )
        return cast(
            ExternalConnectOnboardResponse,
            self._transport._post(
                f"/external/v1/{provider}/connect/onboard",
                payload_with_bu.model_dump(exclude_none=True, by_alias=True),
                ExternalConnectOnboardResponse,
            ),
        )
