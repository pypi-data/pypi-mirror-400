import time
import requests
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass


@dataclass
class Domain:
    id: str
    domain: str
    status: str
    state: str
    verified_at: Optional[str]
    warmup_day: int
    minute_cap: int
    daily_cap: int
    pause_reason: Optional[str]
    spf_record: Optional[str]
    dkim_record: Optional[str]
    dmarc_record: Optional[str]
    created_at: str
    updated_at: str


@dataclass
class Email:
    id: str
    from_address: str
    to_addresses: List[str]
    subject: Optional[str]
    html: Optional[str]
    text: Optional[str]
    status: str
    provider_message_id: Optional[str]
    created_at: str
    updated_at: str


@dataclass
class InboundEmail:
    id: str
    message_id: str
    from_address: str
    to_addresses: List[str]
    cc_addresses: Optional[List[str]]
    subject: Optional[str]
    text_content: Optional[str]
    html_content: Optional[str]
    attachments: Optional[List[Dict[str, Any]]]
    received_at: Optional[str]
    created_at: str


@dataclass
class InboundAttachment:
    id: str
    filename: str
    content_type: Optional[str]
    size_bytes: Optional[int]
    download_url: str


@dataclass
class Event:
    id: str
    type: str
    email_id: Optional[str]
    message_id: Optional[str]
    payload: Optional[Dict[str, Any]]
    created_at: str


@dataclass
class Suppression:
    id: str
    recipient_email: str
    reason: str
    created_at: str


class SendflowError(Exception):
    """Exception raised for Sendflow API errors."""
    
    def __init__(self, message: str, code: str, details: Dict[str, Any] = None, status_code: int = None):
        self.message = message
        self.code = code
        self.details = details or {}
        self.status_code = status_code
        super().__init__(self.message)


class SendflowClient:
    """Official Sendflow SDK for Python."""
    
    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.sendflow.dev/functions/v1",
        timeout: int = 30,
        max_retries: int = 3,
        retry_delay: float = 1.0,
    ):
        """
        Initialize Sendflow client.
        
        Args:
            api_key: Your Sendflow API key
            base_url: Base URL for the API (optional)
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
            retry_delay: Delay between retries in seconds
        """
        if not api_key:
            raise ValueError("API key is required")
        
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
            'User-Agent': 'sendflowdev/1.0.0',
        })
        
        # Initialize API namespaces
        self.domains = DomainsAPI(self)
        self.emails = EmailsAPI(self)
        self.inbound_emails = InboundEmailsAPI(self)
        self.events = EventsAPI(self)
        self.suppressions = SuppressionsAPI(self)
    
    def _request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Make a request with retry logic."""
        url = f"{self.base_url}{endpoint}"
        
        def _make_request():
            response = self.session.request(
                method=method,
                url=url,
                json=data,
                params=params,
                timeout=self.timeout,
            )
            
            if response.status_code >= 400:
                try:
                    error_data = response.json()
                    if 'error' in error_data:
                        error = error_data['error']
                        raise SendflowError(
                            message=error.get('message', 'An error occurred'),
                            code=error.get('code', 'UNKNOWN_ERROR'),
                            details=error.get('details', {}),
                            status_code=response.status_code,
                        )
                except ValueError:
                    pass
                response.raise_for_status()
            
            return response.json() if response.content else {}
        
        # Retry logic
        last_exception = None
        for attempt in range(self.max_retries + 1):
            try:
                return _make_request()
            except (requests.exceptions.RequestException, SendflowError) as e:
                last_exception = e
                
                # Check if error is retryable (429 or 5xx)
                should_retry = False
                if isinstance(e, requests.exceptions.HTTPError):
                    should_retry = e.response.status_code == 429 or e.response.status_code >= 500
                elif isinstance(e, SendflowError):
                    should_retry = e.status_code == 429 or (e.status_code and e.status_code >= 500)
                elif isinstance(e, (requests.exceptions.ConnectionError, requests.exceptions.Timeout)):
                    should_retry = True
                
                if attempt < self.max_retries and should_retry:
                    time.sleep(self.retry_delay * (2 ** attempt))  # Exponential backoff
                    continue
                else:
                    break
        
        raise last_exception


class DomainsAPI:
    """Domains API interface."""
    
    def __init__(self, client: SendflowClient):
        self.client = client
    
    def verify(self, domain_id: str) -> Domain:
        """Verify a domain by checking DNS records."""
        response = self.client._request('POST', f'/domains/{domain_id}/verify')
        return Domain(**response)
    
    def get(self, domain_id: str) -> Domain:
        """Get domain details and DNS records."""
        response = self.client._request('GET', f'/domains/{domain_id}')
        return Domain(**response)
    
    def list(self) -> List[Domain]:
        """List all domains."""
        response = self.client._request('GET', '/domains')
        return [Domain(**domain) for domain in response.get('domains', [])]
    
    def add(self, domain: str) -> Domain:
        """Add a new domain."""
        response = self.client._request('POST', '/domains', {'domain': domain})
        return Domain(**response)


class EmailsAPI:
    """Emails API interface."""
    
    def __init__(self, client: SendflowClient):
        self.client = client
    
    def send(
        self,
        from_email: str,
        to: List[str],
        subject: Optional[str] = None,
        html: Optional[str] = None,
        text: Optional[str] = None,
        template_id: Optional[str] = None,
        variables: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, str]:
        """
        Send an email.
        
        Args:
            from_email: Sender email address (must be verified)
            to: List of recipient email addresses
            subject: Email subject (optional if using template_id)
            html: HTML content (optional if using template_id)
            text: Plain text content (optional if using template_id)
            template_id: UUID of the template to use
            variables: Key-value pairs to substitute in the template
        """
        data = {
            'from': from_email,
            'to': to,
        }
        if subject:
            data['subject'] = subject
        if html:
            data['html'] = html
        if text:
            data['text'] = text
        if template_id:
            data['template_id'] = template_id
        if variables:
            data['variables'] = variables
        
        return self.client._request('POST', '/emails', data)
    
    def get(self, email_id: str) -> Email:
        """Get email status."""
        response = self.client._request('GET', f'/emails/{email_id}')
        return Email(**response)


class InboundEmailsAPI:
    """Inbound Emails API interface."""
    
    def __init__(self, client: SendflowClient):
        self.client = client
    
    def list(
        self,
        domain_id: Optional[str] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> Dict[str, Any]:
        """
        List inbound emails with optional filtering.
        
        Args:
            domain_id: Filter by domain ID
            limit: Maximum number of results (default 20, max 100)
            offset: Number of results to skip
            
        Returns:
            Dictionary with 'emails' list and 'pagination' info
        """
        params = {'limit': limit, 'offset': offset}
        if domain_id:
            params['domain_id'] = domain_id
        
        return self.client._request('GET', '/inbound-emails', params=params)
    
    def get(self, email_id: str) -> InboundEmail:
        """Get a specific inbound email with full content."""
        response = self.client._request('GET', f'/inbound-emails/{email_id}')
        return InboundEmail(**response)
    
    def get_attachment(self, email_id: str, attachment_id: str) -> InboundAttachment:
        """
        Get a signed download URL for an attachment.
        
        Args:
            email_id: The inbound email ID
            attachment_id: The attachment ID
            
        Returns:
            InboundAttachment with download_url (expires in 1 hour)
        """
        response = self.client._request('GET', f'/inbound-emails/{email_id}/attachments/{attachment_id}')
        return InboundAttachment(**response)


class EventsAPI:
    """Events API interface."""
    
    def __init__(self, client: SendflowClient):
        self.client = client
    
    def list(
        self,
        event_type: Optional[str] = None,
        message_id: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Event]:
        """List email events."""
        params = {'limit': limit, 'offset': offset}
        if event_type:
            params['type'] = event_type
        if message_id:
            params['messageId'] = message_id
        
        response = self.client._request('GET', '/events', params=params)
        return [Event(**event) for event in response.get('events', [])]


class SuppressionsAPI:
    """Suppressions API interface."""
    
    def __init__(self, client: SendflowClient):
        self.client = client
    
    def list(self) -> List[Suppression]:
        """List suppressed email addresses."""
        response = self.client._request('GET', '/suppressions')
        return [Suppression(**suppression) for suppression in response.get('suppressions', [])]
    
    def add(self, email: str, reason: str) -> None:
        """Add an email to the suppression list."""
        self.client._request('POST', '/suppressions', {'email': email, 'reason': reason})
    
    def remove(self, email: str) -> None:
        """Remove an email from the suppression list."""
        self.client._request('DELETE', '/suppressions', {'email': email})


# Convenience alias
Sendflow = SendflowClient
