"""
Main Alura client for tracking AI usage and costs
"""
import requests
from typing import Optional, List, Callable, Any, TypeVar, Union
from contextlib import contextmanager
from contextvars import ContextVar
from datetime import date
from .models import (
    Signal, Customer, Contact, Order, OrderLine, Address,
    EntitlementUsage, CostTrace, CostTracesResponse,
    UsageSummary, UsageSummariesResponse,
    Product, ProductType, ProductAttribute, ProductPricing,
    AgentPricePoint, AgentPricePointTiers,
)

# Context variable for current trace
_current_trace: ContextVar[Optional[dict]] = ContextVar('current_trace', default=None)

T = TypeVar('T')


class AluraError(Exception):
    """Base exception for Alura SDK"""
    pass


class AuthenticationError(AluraError):
    """Invalid API key"""
    pass


class APIError(AluraError):
    """API request failed"""
    def __init__(self, message: str, status_code: int = None, response: dict = None):
        super().__init__(message)
        self.status_code = status_code
        self.response = response


class Alura:
    """
    Main client for Alura AI usage tracking and billing.

    Usage (context manager style):
        from alura import Alura, AluraOpenAI
        from openai import OpenAI

        client = Alura(api_key="your-alura-api-key")
        openai_client = OpenAI(api_key="your-openai-key")
        alura_openai = AluraOpenAI(openai_client, client)

        with client.trace(customer_id="cust-123", agent_id="chatbot"):
            response = alura_openai.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": "Hello!"}]
            )

    Usage (Paid AI compatible):
        from alura import Alura, Signal

        client = Alura(token="your-key")

        # Create a customer (account)
        customer = client.customers.create(
            name="Acme Ltd",
            email="billing@acme.com",
            external_id="acme_123"
        )

        # Create a contact
        contact = client.contacts.create(
            customer_id=customer.id,
            first_name="John",
            last_name="Doe",
            email="john@acme.com"
        )

        # Create an order
        order = client.orders.create(
            customer_id=customer.id,
            agent_code="AG-001"
        )

        # Record usage
        client.usage.record_bulk(signals=[
            Signal(event_name="llm_call", agent_id="AG-001", customer_id="acme_123")
        ])
    """

    def __init__(
        self,
        api_key: str = None,
        token: str = None,  # Paid AI compatibility alias
        base_url: str = "https://aluraai.com",
    ):
        # Support both api_key and token (Paid AI uses token)
        self.api_key = api_key or token
        if not self.api_key:
            raise ValueError("api_key (or token) is required")

        self.base_url = base_url.rstrip('/')

        # Paid AI compatible namespaces
        self.usage = _UsageNamespace(self)
        self.customers = _CustomersNamespace(self)
        self.contacts = _ContactsNamespace(self)
        self.orders = _OrdersNamespace(self)
        self.products = _ProductsNamespace(self)

    def initialize_tracing(self):
        """
        Initialize tracing (Paid AI compatibility).
        In Alura, tracing is always active - this is a no-op for compatibility.
        """
        pass

    def _request(
        self,
        method: str,
        endpoint: str,
        json: dict = None,
    ) -> dict:
        """Make HTTP request to Alura API"""
        url = f"{self.base_url}{endpoint}"
        headers = {
            "Authorization": f"Api-Key {self.api_key}",
            "Content-Type": "application/json",
        }

        try:
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                json=json,
                timeout=30,
            )

            if response.status_code == 401:
                raise AuthenticationError("Invalid API key")

            if not response.ok:
                error_msg = "API request failed"
                try:
                    error_data = response.json()
                    if "error" in error_data:
                        error_msg = error_data["error"]
                except:
                    error_msg = response.text or f"HTTP {response.status_code}"
                raise APIError(error_msg, response.status_code, response.json() if response.text else None)

            return response.json()

        except requests.exceptions.RequestException as e:
            raise APIError(f"Request failed: {str(e)}")

    def trace(
        self,
        customer_id: str = None,
        agent_id: str = None,
        # Paid AI compatibility aliases
        external_customer_id: str = None,
        external_agent_id: str = None,
        fn: Callable[[], T] = None,
    ) -> T:
        """
        Trace AI calls with customer/agent context.

        Can be used as context manager OR with callback function (Paid AI style).

        Context manager usage:
            with client.trace(customer_id="cust-123", agent_id="chatbot"):
                response = alura_openai.chat.completions.create(...)

        Callback usage (Paid AI compatible):
            result = client.trace(
                external_customer_id="cust-123",
                external_agent_id="chatbot",
                fn=lambda: make_openai_call()
            )
        """
        # Support Paid AI parameter names
        customer_id = customer_id or external_customer_id
        agent_id = agent_id or external_agent_id

        # If fn is provided, use callback style (Paid AI compatible)
        if fn is not None:
            return self._trace_with_callback(customer_id, agent_id, fn)

        # Otherwise return context manager
        return self._trace_context(customer_id, agent_id)

    def _trace_with_callback(
        self,
        customer_id: str,
        agent_id: str,
        fn: Callable[[], T],
    ) -> T:
        """Execute function within trace context (Paid AI style)"""
        trace_context = {
            "customer_id": customer_id,
            "agent_id": agent_id,
        }
        token = _current_trace.set(trace_context)
        try:
            return fn()
        finally:
            _current_trace.reset(token)

    @contextmanager
    def _trace_context(
        self,
        customer_id: str,
        agent_id: str,
    ):
        """Context manager for tracing AI calls"""
        trace_context = {
            "customer_id": customer_id,
            "agent_id": agent_id,
        }
        token = _current_trace.set(trace_context)
        try:
            yield trace_context
        finally:
            _current_trace.reset(token)

    def action(
        self,
        event_name: str,
        agent_id: str = None,
        data: dict = None,
        customer_id: str = None,
    ) -> dict:
        """
        Record a single action/event.

        Args:
            event_name: Name of the event (e.g., "llm_call", "email_sent")
            agent_id: Agent code (uses trace context if not provided)
            data: Event-specific data
            customer_id: Customer ID (uses trace context if not provided)
        """
        # Get from trace context if not provided
        trace = _current_trace.get()
        if trace:
            agent_id = agent_id or trace.get("agent_id")
            customer_id = customer_id or trace.get("customer_id")

        if not agent_id:
            raise ValueError("agent_id is required (provide directly or use trace() context)")

        payload = {
            "agent_code": agent_id,
            "event_name": event_name,
            "data": data or {},
        }

        if customer_id:
            payload["data"]["customer_id"] = customer_id

        return self._request("POST", "/api/tracking/actions/", json=payload)

    def action_bulk(self, actions: List[Signal]) -> dict:
        """
        Record multiple actions in a single request.

        Args:
            actions: List of Signal objects (action data)
        """
        payload = {
            "signals": [s.to_dict() for s in actions]
        }
        return self._request("POST", "/api/tracking/actions/bulk_create/", json=payload)

    # Backward compatibility aliases
    def signal(
        self,
        event_name: str,
        agent_id: str = None,
        data: dict = None,
        customer_id: str = None,
    ) -> dict:
        """
        Record a single signal/event (deprecated, use action() instead).

        Args:
            event_name: Name of the event (e.g., "llm_call", "email_sent")
            agent_id: Agent code (uses trace context if not provided)
            data: Event-specific data
            customer_id: Customer ID (uses trace context if not provided)
        """
        return self.action(event_name, agent_id, data, customer_id)

    def signal_bulk(self, signals: List[Signal]) -> dict:
        """
        Record multiple signals in a single request (deprecated, use action_bulk() instead).

        Args:
            signals: List of Signal objects
        """
        return self.action_bulk(signals)

    # ==========================================
    # Agent Management
    # ==========================================

    def create_agent(
        self,
        name: str,
        code: str = None,
        description: str = "",
        external_id: str = None,
        status: str = "live",
    ) -> dict:
        """
        Create a new agent.

        Args:
            name: Human-readable name for the agent
            code: Unique code identifier (auto-generated if not provided)
            description: What this agent does
            external_id: Optional external identifier
            status: 'live', 'draft', or 'archived' (default: 'live')

        Returns:
            Agent dict with 'id', 'code', 'name', etc.
        """
        import secrets

        payload = {
            "name": name,
            "code": code or f"AG-{secrets.token_hex(4).upper()}",
            "description": description,
            "status": status,
        }
        if external_id:
            payload["external_id"] = external_id

        return self._request("POST", "/api/tracking/agents/", json=payload)

    def get_agents(self) -> List[dict]:
        """List all agents for this account."""
        response = self._request("GET", "/api/tracking/agents/")
        if isinstance(response, dict) and 'results' in response:
            return response['results']
        return response

    def get_agent(self, agent_code: str) -> dict:
        """Get a specific agent by code."""
        agents = self.get_agents()
        for agent in agents:
            if agent.get('code') == agent_code:
                return agent
        raise APIError(f"Agent not found: {agent_code}", 404)

    @staticmethod
    def get_current_trace() -> Optional[dict]:
        """Get the current trace context (used by wrappers)"""
        return _current_trace.get()


# ==========================================
# Namespaces (Paid AI Compatible)
# ==========================================

class _UsageNamespace:
    """Paid AI compatible usage namespace for client.usage.record_bulk()"""

    def __init__(self, client: Alura):
        self._client = client

    def record(
        self,
        event_name: str,
        agent_id: str = None,
        agent_code: str = None,
        customer_id: str = None,
        data: dict = None,
    ) -> dict:
        """
        Record a single usage event (Paid AI compatible).

        Args:
            event_name: Name of the event
            agent_id: Agent ID or code
            agent_code: Alias for agent_id
            customer_id: Customer/account ID
            data: Additional event data
        """
        payload = {
            "eventName": event_name,
            "data": data or {},
        }
        if agent_id or agent_code:
            payload["agentCode"] = agent_id or agent_code
        if customer_id:
            payload["customerId"] = customer_id

        return self._client._request("POST", "/api/v1/usage/record", json=payload)

    def record_bulk(self, signals: List[Signal]) -> dict:
        """
        Record multiple signals in a single request (Paid AI compatible).

        Args:
            signals: List of Signal objects
        """
        payload = {
            "signals": [
                {
                    "eventName": s.event_name,
                    "agentCode": s.agent_id,
                    "customerId": s.customer_id,
                    "data": s.data,
                    "externalId": s.external_id or "",
                }
                for s in signals
            ]
        }
        return self._client._request("POST", "/api/v1/usage/record_bulk", json=payload)


class _CustomersNamespace:
    """
    Paid AI compatible customers namespace.

    Alura uses "customers" while Paid.ai uses "accounts" - this provides both.
    """

    def __init__(self, client: Alura):
        self._client = client

    def create(
        self,
        name: str,
        phone: str = "",
        employee_count: int = None,
        annual_revenue: float = None,
        tax_exempt_status: str = "none",
        creation_source: str = "api",
        website: str = "",
        external_id: str = "",
        billing_address: dict = None,
        # Additional fields
        email: str = "",
        company_name: str = "",
        metadata: dict = None,
    ) -> Customer:
        """
        Create a new customer (account).

        Args:
            name: Customer/company name (required)
            phone: Optional phone number
            employee_count: Optional number of employees
            annual_revenue: Optional annual revenue
            tax_exempt_status: Optional tax exempt status ('none', 'exempt', 'reverse')
            creation_source: Optional source of creation ('manual', 'api', 'crm', 'other')
            website: Optional website URL
            external_id: Optional external identifier
            billing_address: Optional billing address dict with keys:
                line1, line2, city, state, zip_code, country
            email: Optional email address
            company_name: Optional company name
            metadata: Additional metadata

        Returns:
            Customer object

        Example:
            customer = client.customers.create(
                name="Acme Corporation",
                phone="+1-555-0123",
                employee_count=100,
                annual_revenue=1000000,
                tax_exempt_status="none",
                creation_source="api",
                website="https://acme.com",
                external_id="acme_123",
                billing_address={
                    "line1": "123 Business Ave",
                    "line2": "Suite 100",
                    "city": "San Francisco",
                    "state": "CA",
                    "zip_code": "94105",
                    "country": "USA"
                }
            )
        """
        payload = {
            "name": name,
            "phone": phone,
            "taxExemptStatus": tax_exempt_status,
            "creationSource": creation_source,
            "metadata": metadata or {},
        }

        if employee_count is not None:
            payload["employeeCount"] = employee_count
        if annual_revenue is not None:
            payload["annualRevenue"] = str(annual_revenue)
        if website:
            payload["website"] = website
        if external_id:
            payload["externalId"] = external_id
        if email:
            payload["email"] = email
        if company_name:
            payload["companyName"] = company_name

        if billing_address:
            payload["billingAddress"] = {
                "line1": billing_address.get("line1", billing_address.get("line_1", "")),
                "line2": billing_address.get("line2", billing_address.get("line_2", "")),
                "city": billing_address.get("city", ""),
                "state": billing_address.get("state", ""),
                "zipCode": billing_address.get("zip_code", billing_address.get("zipCode", "")),
                "country": billing_address.get("country", ""),
            }

        response = self._client._request("POST", "/api/v1/accounts/", json=payload)
        return Customer.from_dict(response)

    def get(self, customer_id: int) -> Customer:
        """Get a customer by ID."""
        response = self._client._request("GET", f"/api/v1/accounts/{customer_id}/")
        return Customer.from_dict(response)

    def get_by_external_id(self, external_id: str) -> Customer:
        """Get a customer by external ID."""
        response = self._client._request("GET", f"/api/v1/accounts/external/{external_id}/")
        return Customer.from_dict(response)

    def list(self) -> List[Customer]:
        """List all customers."""
        response = self._client._request("GET", "/api/v1/accounts/")
        if isinstance(response, dict) and 'results' in response:
            return [Customer.from_dict(c) for c in response['results']]
        return [Customer.from_dict(c) for c in response]

    def update(self, customer_id: int, **kwargs) -> Customer:
        """
        Update a customer by internal ID.

        Args:
            customer_id: Internal customer ID
            **kwargs: Fields to update (name, phone, employee_count, etc.)

        Returns:
            Updated Customer object
        """
        payload = self._build_update_payload(**kwargs)
        response = self._client._request("PUT", f"/api/v1/accounts/{customer_id}/", json=payload)
        return Customer.from_dict(response)

    def update_by_external_id(self, external_id: str, **kwargs) -> Customer:
        """
        Update a customer by external ID.

        Args:
            external_id: External customer ID
            **kwargs: Fields to update (name, phone, employee_count, etc.)

        Returns:
            Updated Customer object
        """
        payload = self._build_update_payload(**kwargs)
        response = self._client._request("PUT", f"/api/v1/accounts/external/{external_id}/", json=payload)
        return Customer.from_dict(response)

    def _build_update_payload(self, **kwargs) -> dict:
        """Build update payload from kwargs."""
        key_map = {
            "name": "name",
            "phone": "phone",
            "employee_count": "employeeCount",
            "annual_revenue": "annualRevenue",
            "tax_exempt_status": "taxExemptStatus",
            "creation_source": "creationSource",
            "website": "website",
            "external_id": "externalId",
            "email": "email",
            "company_name": "companyName",
            "metadata": "metadata",
        }
        payload = {}
        for key, value in kwargs.items():
            if key in key_map:
                payload[key_map[key]] = value
            elif key == "billing_address" and value:
                payload["billingAddress"] = {
                    "line1": value.get("line1", value.get("line_1", "")),
                    "line2": value.get("line2", value.get("line_2", "")),
                    "city": value.get("city", ""),
                    "state": value.get("state", ""),
                    "zipCode": value.get("zip_code", value.get("zipCode", "")),
                    "country": value.get("country", ""),
                }
        return payload

    def delete(self, customer_id: int) -> None:
        """Delete (soft) a customer by internal ID."""
        self._client._request("DELETE", f"/api/v1/accounts/{customer_id}/")

    def delete_by_external_id(self, external_id: str) -> None:
        """Delete (soft) a customer by external ID."""
        self._client._request("DELETE", f"/api/v1/accounts/external/{external_id}/")

    def get_entitlements(self, customer_id: int) -> List[EntitlementUsage]:
        """
        Get customer entitlements (credit bundles) by internal ID.

        Args:
            customer_id: Internal customer ID

        Returns:
            List of EntitlementUsage objects

        Example:
            entitlements = client.customers.get_entitlements(customer_id=123)
            for e in entitlements:
                print(f"{e.total} total, {e.available} available, {e.used} used")
        """
        response = self._client._request("GET", f"/api/v1/accounts/{customer_id}/credit-bundles/")
        if isinstance(response, list):
            return [EntitlementUsage.from_dict(e) for e in response]
        return []

    def get_costs_by_external_id(
        self,
        external_id: str,
        limit: int = 100,
        offset: int = 0,
        start_time: str = None,
        end_time: str = None,
    ) -> CostTracesResponse:
        """
        Fetch cost traces for a customer by external ID.

        Args:
            external_id: External customer ID
            limit: Maximum number of traces (1-1000, default 100)
            offset: Pagination offset (default 0)
            start_time: Filter traces from this time (ISO 8601 format)
            end_time: Filter traces up to this time (ISO 8601 format)

        Returns:
            CostTracesResponse with traces and pagination metadata

        Example:
            costs = client.customers.get_costs_by_external_id(
                external_id="acme-123",
                limit=50,
                start_time="2025-01-01T00:00:00Z"
            )
            for trace in costs.traces:
                print(f"{trace.model}: ${trace.total_cost}")
        """
        params = []
        if limit != 100:
            params.append(f"limit={limit}")
        if offset != 0:
            params.append(f"offset={offset}")
        if start_time:
            params.append(f"startTime={start_time}")
        if end_time:
            params.append(f"endTime={end_time}")

        query_string = f"?{'&'.join(params)}" if params else ""
        response = self._client._request(
            "GET",
            f"/api/v1/accounts/external/{external_id}/costs/{query_string}"
        )
        return CostTracesResponse.from_dict(response)

    def get_usage_by_external_id(
        self,
        external_id: str,
        limit: int = 100,
        offset: int = 0,
        start_time: str = None,
        end_time: str = None,
    ) -> UsageSummariesResponse:
        """
        Fetch usage summaries for a customer by external ID.

        Args:
            external_id: External customer ID
            limit: Maximum number of summaries (1-1000, default 100)
            offset: Pagination offset (default 0)
            start_time: Filter summaries from this time (ISO 8601 format)
            end_time: Filter summaries up to this time (ISO 8601 format)

        Returns:
            UsageSummariesResponse with data and pagination metadata

        Example:
            usage = client.customers.get_usage_by_external_id(
                external_id="acme-123",
                limit=50,
                start_time="2025-01-01T00:00:00Z"
            )
            for summary in usage.data:
                print(f"{summary.event_name}: {summary.events_quantity} events")
        """
        params = []
        if limit != 100:
            params.append(f"limit={limit}")
        if offset != 0:
            params.append(f"offset={offset}")
        if start_time:
            params.append(f"startTime={start_time}")
        if end_time:
            params.append(f"endTime={end_time}")

        query_string = f"?{'&'.join(params)}" if params else ""
        response = self._client._request(
            "GET",
            f"/api/v1/accounts/external/{external_id}/usage/{query_string}"
        )
        return UsageSummariesResponse.from_dict(response)


class _ContactsNamespace:
    """Paid AI compatible contacts namespace."""

    def __init__(self, client: Alura):
        self._client = client

    def create(
        self,
        customer_id: int = None,
        customer_external_id: str = None,
        salutation: str = "",
        first_name: str = "",
        last_name: str = "",
        email: str = "",
        phone: str = "",
        external_id: str = "",
        billing_street: str = "",
        billing_city: str = "",
        billing_state_province: str = "",
        billing_country: str = "",
        billing_postal_code: str = "",
        is_primary: bool = False,
        receives_invoices: bool = True,
        metadata: dict = None,
    ) -> Contact:
        """
        Create a new contact for a customer.

        Args:
            customer_id: Internal customer ID
            customer_external_id: External customer ID (alternative to customer_id)
            salutation: Mr., Ms., Dr., etc.
            first_name: First name
            last_name: Last name
            email: Email address
            phone: Phone number
            external_id: Your system's ID for this contact
            billing_*: Billing address fields
            is_primary: Whether this is the primary contact
            receives_invoices: Whether this contact receives invoices
            metadata: Additional metadata

        Returns:
            Contact object
        """
        payload = {
            "salutation": salutation,
            "firstName": first_name,
            "lastName": last_name,
            "email": email,
            "phone": phone,
            "externalId": external_id,
            "billingAddressLine1": billing_street,
            "billingCity": billing_city,
            "billingState": billing_state_province,
            "billingCountry": billing_country,
            "billingPostalCode": billing_postal_code,
            "isPrimary": is_primary,
            "receivesInvoices": receives_invoices,
            "metadata": metadata or {},
        }

        if customer_id:
            payload["accountId"] = customer_id
        elif customer_external_id:
            payload["accountExternalId"] = customer_external_id
        else:
            raise ValueError("Either customer_id or customer_external_id is required")

        response = self._client._request("POST", "/api/v1/contacts/", json=payload)
        return Contact.from_dict(response)

    def get(self, contact_id: int) -> Contact:
        """Get a contact by ID."""
        response = self._client._request("GET", f"/api/v1/contacts/{contact_id}/")
        return Contact.from_dict(response)

    def get_by_external_id(self, external_id: str) -> Contact:
        """Get a contact by external ID."""
        response = self._client._request("GET", f"/api/v1/contacts/external/{external_id}/")
        return Contact.from_dict(response)

    def list(self) -> List[Contact]:
        """List all contacts."""
        response = self._client._request("GET", "/api/v1/contacts/")
        if isinstance(response, dict) and 'results' in response:
            return [Contact.from_dict(c) for c in response['results']]
        return [Contact.from_dict(c) for c in response]

    def update(self, contact_id: int, **kwargs) -> Contact:
        """Update a contact."""
        key_map = {
            "salutation": "salutation",
            "first_name": "firstName",
            "last_name": "lastName",
            "email": "email",
            "phone": "phone",
            "external_id": "externalId",
            "billing_street": "billingAddressLine1",
            "billing_city": "billingCity",
            "billing_state_province": "billingState",
            "billing_country": "billingCountry",
            "billing_postal_code": "billingPostalCode",
            "is_primary": "isPrimary",
            "receives_invoices": "receivesInvoices",
            "metadata": "metadata",
        }
        payload = {}
        for key, value in kwargs.items():
            if key in key_map:
                payload[key_map[key]] = value

        response = self._client._request("PUT", f"/api/v1/contacts/{contact_id}/", json=payload)
        return Contact.from_dict(response)

    def delete(self, contact_id: int) -> None:
        """Delete (soft) a contact."""
        self._client._request("DELETE", f"/api/v1/contacts/{contact_id}/")


class _OrderLinesNamespace:
    """Paid AI compatible order lines sub-namespace for orders.lines operations."""

    def __init__(self, client: 'Alura'):
        self._client = client

    def update(
        self,
        order_id: Union[int, str],
        lines: List[dict] = None,
    ) -> List['OrderLine']:
        """
        Add/remove order lines for an existing order.

        Args:
            order_id: Order ID (internal ID)
            lines: List of order line configurations, each containing:
                - agent_id or agent_external_id: Agent reference
                - name: Name of the order line
                - description: Description of the order line

        Returns:
            List of OrderLine objects

        Example:
            order = client.orders.lines.update(order_id=id, lines=[
                {
                    "agent_external_id": "sdk-agent-3",
                    "name": "Analytics Dashboard Add-on",
                    "description": "Real-time analytics and reporting dashboard"
                }
            ])
        """
        from .models import OrderLine

        # Convert lines to camelCase for API
        formatted_lines = []
        for line in (lines or []):
            formatted_line = {}
            if line.get("agent_id"):
                formatted_line["agentId"] = line["agent_id"]
            if line.get("agent_external_id"):
                formatted_line["agentExternalId"] = line["agent_external_id"]
            if line.get("agent_code"):
                formatted_line["agentCode"] = line["agent_code"]
            if line.get("name"):
                formatted_line["name"] = line["name"]
            if line.get("description"):
                formatted_line["description"] = line["description"]
            if line.get("start_date"):
                start = line["start_date"]
                formatted_line["startDate"] = start.isoformat() if hasattr(start, 'isoformat') else start
            if line.get("end_date"):
                end = line["end_date"]
                formatted_line["endDate"] = end.isoformat() if hasattr(end, 'isoformat') else end
            formatted_lines.append(formatted_line)

        payload = {"lines": formatted_lines}
        response = self._client._request("POST", f"/api/v1/orders/{order_id}/lines/", json=payload)

        # Parse response - could be order or list of lines
        if isinstance(response, dict) and "order_lines" in response:
            return [OrderLine.from_dict(line) for line in response["order_lines"]]
        elif isinstance(response, dict) and "orderLines" in response:
            return [OrderLine.from_dict(line) for line in response["orderLines"]]
        elif isinstance(response, list):
            return [OrderLine.from_dict(line) for line in response]
        return []


class _OrdersNamespace:
    """Paid AI compatible orders namespace."""

    def __init__(self, client: 'Alura'):
        self._client = client
        self.lines = _OrderLinesNamespace(client)

    def create(
        self,
        customer_id: int = None,
        customer_external_id: str = None,
        agent_id: int = None,
        agent_code: str = None,
        agent_external_id: str = None,
        billing_contact_id: int = None,
        external_id: str = "",
        name: str = "",
        description: str = "",
        billing_frequency: str = "monthly",
        seat_count: int = 1,
        start_date: Union[date, str] = None,
        end_date: Union[date, str] = None,
        currency: str = "USD",
        order_lines: List[dict] = None,
        metadata: dict = None,
    ) -> Order:
        """
        Create a new order linking a customer to an agent.

        Args:
            customer_id: Internal customer ID
            customer_external_id: External customer ID (alternative)
            agent_id: Internal agent ID (for single-agent orders)
            agent_code: Agent code (alternative to agent_id)
            agent_external_id: External agent ID (alternative)
            billing_contact_id: Contact ID for billing
            external_id: Your system's ID for this order
            name: Order name/title
            description: Order description
            billing_frequency: one_time, monthly, quarterly, yearly, per_use
            seat_count: Number of seats
            start_date: Start date (date object or ISO string)
            end_date: End date (optional)
            currency: Currency code (default: USD)
            order_lines: List of order line configurations (Paid AI style)
                Each line can contain:
                - agent_id or agent_external_id: Agent reference
                - name: Name of the order line
                - description: Description of the order line
            metadata: Additional metadata

        Returns:
            Order object

        Example (Paid AI style with order_lines):
            order = client.orders.create(
                name="AI SDR - Pro plan",
                customer_id=customer_id,
                billing_contact_id=billing_contact_id,
                description="Annual subscription for AI SDR - Pro plan",
                start_date="2025-06-01",
                end_date="2026-05-31",
                currency="USD",
                order_lines=[
                    {
                        "agent_external_id": "ai_agent_123",
                        "name": "AI SDR",
                        "description": "AI SDR - agent"
                    }
                ]
            )
        """
        payload = {
            "externalId": external_id,
            "billingFrequency": billing_frequency,
            "seatCount": seat_count,
            "metadata": metadata or {},
        }

        if name:
            payload["name"] = name
        if description:
            payload["description"] = description

        if customer_id:
            payload["accountId"] = customer_id
        elif customer_external_id:
            payload["accountExternalId"] = customer_external_id
        else:
            raise ValueError("Either customer_id or customer_external_id is required")

        # Handle order_lines (Paid AI style) - if provided, use those
        if order_lines:
            formatted_lines = []
            for line in order_lines:
                formatted_line = {}
                if line.get("agent_id"):
                    formatted_line["agentId"] = line["agent_id"]
                if line.get("agent_external_id"):
                    formatted_line["agentExternalId"] = line["agent_external_id"]
                if line.get("agent_code"):
                    formatted_line["agentCode"] = line["agent_code"]
                if line.get("name"):
                    formatted_line["name"] = line["name"]
                if line.get("description"):
                    formatted_line["description"] = line["description"]
                formatted_lines.append(formatted_line)
            payload["orderLines"] = formatted_lines
        else:
            # Single agent order (legacy Alura style)
            if agent_id:
                payload["agentId"] = agent_id
            elif agent_code:
                payload["agentCode"] = agent_code
            elif agent_external_id:
                payload["agentExternalId"] = agent_external_id
            else:
                raise ValueError("Either agent_id, agent_code, agent_external_id, or order_lines is required")

        if billing_contact_id:
            payload["billingContactId"] = billing_contact_id

        if start_date:
            payload["startDate"] = start_date.isoformat() if isinstance(start_date, date) else start_date

        if end_date:
            payload["endDate"] = end_date.isoformat() if isinstance(end_date, date) else end_date

        if currency:
            payload["currency"] = currency

        response = self._client._request("POST", "/api/v1/orders/", json=payload)
        return Order.from_dict(response)

    def get(self, order_id: Union[int, str]) -> Order:
        """Get an order by ID."""
        response = self._client._request("GET", f"/api/v1/orders/{order_id}/")
        return Order.from_dict(response)

    def list(self) -> List[Order]:
        """List all orders."""
        response = self._client._request("GET", "/api/v1/orders/")
        if isinstance(response, dict) and 'results' in response:
            return [Order.from_dict(o) for o in response['results']]
        return [Order.from_dict(o) for o in response]

    def activate(self, order_id: Union[int, str]) -> Order:
        """Activate a draft order."""
        response = self._client._request("POST", f"/api/v1/orders/{order_id}/activate/")
        return Order.from_dict(response)

    def pause(self, order_id: Union[int, str]) -> Order:
        """Pause an active order."""
        response = self._client._request("POST", f"/api/v1/orders/{order_id}/pause/")
        return Order.from_dict(response)

    def cancel(self, order_id: Union[int, str]) -> Order:
        """Cancel an order."""
        response = self._client._request("POST", f"/api/v1/orders/{order_id}/cancel/")
        return Order.from_dict(response)

    def delete(self, order_id: Union[int, str]) -> None:
        """Delete an order."""
        self._client._request("DELETE", f"/api/v1/orders/{order_id}/")


class _ProductsNamespace:
    """
    Paid AI compatible products namespace.

    Products are billable items (formerly called agents) that customers purchase.
    """

    def __init__(self, client: 'Alura'):
        self._client = client

    def list(self) -> List[Product]:
        """
        List all products.

        Returns:
            List of Product objects

        Example:
            products = client.products.list()
            for product in products:
                print(f"{product.name}: {product.display_id}")
        """
        response = self._client._request("GET", "/api/v1/products/")
        if isinstance(response, dict) and 'results' in response:
            return [Product.from_dict(p) for p in response['results']]
        return [Product.from_dict(p) for p in response]

    def get(self, product_id: Union[int, str]) -> Product:
        """
        Get a product by ID.

        Args:
            product_id: Product ID

        Returns:
            Product object
        """
        response = self._client._request("GET", f"/api/v1/products/{product_id}/")
        return Product.from_dict(response)

    def get_by_external_id(self, external_id: str) -> Product:
        """
        Get a product by external ID.

        Args:
            external_id: External product ID

        Returns:
            Product object
        """
        response = self._client._request("GET", f"/api/v1/products/external/{external_id}/")
        return Product.from_dict(response)

    def create(
        self,
        name: str,
        description: str = "",
        type: str = "agent",
        external_id: str = "",
        product_code: str = "",
        metadata: dict = None,
    ) -> Product:
        """
        Create a new product.

        Args:
            name: Product name (required)
            description: Product description
            type: Product type ('agent', 'product', 'prepaidCreditBundle')
            external_id: External identifier
            product_code: Unique product code (auto-generated if not provided)
            metadata: Additional metadata

        Returns:
            Created Product object

        Example:
            product = client.products.create(
                name="AI SDR Agent",
                description="Sales development AI agent",
                type="agent",
                external_id="sdr-agent-1"
            )
        """
        payload = {
            "name": name,
            "description": description,
            "type": type,
            "metadata": metadata or {},
        }

        if external_id:
            payload["externalId"] = external_id
        if product_code:
            payload["productCode"] = product_code

        response = self._client._request("POST", "/api/v1/products/", json=payload)
        return Product.from_dict(response)

    def update(
        self,
        product_id: Union[int, str],
        name: str = None,
        description: str = None,
        type: str = None,
        external_id: str = None,
        active: bool = None,
        metadata: dict = None,
    ) -> Product:
        """
        Update a product by ID.

        Args:
            product_id: Product ID
            name: New product name
            description: New description
            type: New product type
            external_id: New external ID
            active: Whether product is active
            metadata: New metadata

        Returns:
            Updated Product object
        """
        payload = {}
        if name is not None:
            payload["name"] = name
        if description is not None:
            payload["description"] = description
        if type is not None:
            payload["type"] = type
        if external_id is not None:
            payload["externalId"] = external_id
        if active is not None:
            payload["active"] = active
        if metadata is not None:
            payload["metadata"] = metadata

        response = self._client._request("PUT", f"/api/v1/products/{product_id}/", json=payload)
        return Product.from_dict(response)

    def update_by_external_id(
        self,
        external_id: str,
        name: str = None,
        description: str = None,
        type: str = None,
        active: bool = None,
        metadata: dict = None,
    ) -> Product:
        """
        Update a product by external ID.

        Args:
            external_id: External product ID
            name: New product name
            description: New description
            type: New product type
            active: Whether product is active
            metadata: New metadata

        Returns:
            Updated Product object
        """
        payload = {}
        if name is not None:
            payload["name"] = name
        if description is not None:
            payload["description"] = description
        if type is not None:
            payload["type"] = type
        if active is not None:
            payload["active"] = active
        if metadata is not None:
            payload["metadata"] = metadata

        response = self._client._request("PUT", f"/api/v1/products/external/{external_id}/", json=payload)
        return Product.from_dict(response)

    def delete(self, product_id: Union[int, str]) -> None:
        """
        Delete (soft) a product by ID.

        Args:
            product_id: Product ID
        """
        self._client._request("DELETE", f"/api/v1/products/{product_id}/")

    def delete_by_external_id(self, external_id: str) -> None:
        """
        Delete (soft) a product by external ID.

        Args:
            external_id: External product ID
        """
        self._client._request("DELETE", f"/api/v1/products/external/{external_id}/")
