"""
SchedulifyX API Client
"""

import requests
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urljoin, urlencode


class SchedulifyXError(Exception):
    """Exception raised for SchedulifyX API errors"""
    
    def __init__(self, message: str, code: str, status: int, details: Optional[Dict] = None):
        super().__init__(message)
        self.message = message
        self.code = code
        self.status = status
        self.details = details or {}
    
    def __str__(self):
        return f"SchedulifyXError({self.code}): {self.message}"


class PostsAPI:
    """Posts API methods"""
    
    def __init__(self, client: 'SchedulifyX'):
        self._client = client
    
    def list(
        self,
        status: Optional[str] = None,
        account_id: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> Dict[str, Any]:
        """List all posts with optional filters"""
        params = {}
        if status:
            params['status'] = status
        if account_id:
            params['accountId'] = account_id
        if limit:
            params['limit'] = limit
        if offset:
            params['offset'] = offset
        return self._client._request('GET', '/posts', params=params)
    
    def get(self, post_id: str) -> Dict[str, Any]:
        """Get a single post by ID"""
        return self._client._request('GET', f'/posts/{post_id}')
    
    def create(
        self,
        content: str,
        account_ids: List[str],
        publish_at: Optional[str] = None,
        publish_now: bool = False,
        media_urls: Optional[List[str]] = None,
        platform_overrides: Optional[Dict[str, Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """Create a new post"""
        data = {
            'content': content,
            'accountIds': account_ids,
        }
        if publish_at:
            data['publishAt'] = publish_at
        if publish_now:
            data['publishNow'] = True
        if media_urls:
            data['mediaUrls'] = media_urls
        if platform_overrides:
            data['platformOverrides'] = platform_overrides
        return self._client._request('POST', '/posts', json=data)
    
    def update(
        self,
        post_id: str,
        content: Optional[str] = None,
        publish_at: Optional[str] = None,
        media_urls: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Update an existing post"""
        data = {}
        if content is not None:
            data['content'] = content
        if publish_at is not None:
            data['publishAt'] = publish_at
        if media_urls is not None:
            data['mediaUrls'] = media_urls
        return self._client._request('PATCH', f'/posts/{post_id}', json=data)
    
    def delete(self, post_id: str) -> Dict[str, Any]:
        """Delete a post"""
        return self._client._request('DELETE', f'/posts/{post_id}')
    
    def publish(self, post_id: str) -> Dict[str, Any]:
        """Publish a post immediately"""
        return self._client._request('POST', f'/posts/{post_id}/publish')


class AccountsAPI:
    """Accounts API methods"""
    
    def __init__(self, client: 'SchedulifyX'):
        self._client = client
    
    def list(
        self,
        platform: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> Dict[str, Any]:
        """List all connected social accounts"""
        params = {}
        if platform:
            params['platform'] = platform
        if limit:
            params['limit'] = limit
        if offset:
            params['offset'] = offset
        return self._client._request('GET', '/accounts', params=params)
    
    def get(self, account_id: str) -> Dict[str, Any]:
        """Get a single account by ID"""
        return self._client._request('GET', f'/accounts/{account_id}')
    
    def get_pinterest_boards(self, account_id: str) -> Dict[str, Any]:
        """Get Pinterest boards for a Pinterest account"""
        return self._client._request('GET', f'/accounts/{account_id}/pinterest-boards')


class AnalyticsAPI:
    """Analytics API methods"""
    
    def __init__(self, client: 'SchedulifyX'):
        self._client = client
    
    def overview(self) -> Dict[str, Any]:
        """Get analytics overview"""
        return self._client._request('GET', '/analytics/overview')
    
    def for_account(self, account_id: str, days: Optional[int] = None) -> Dict[str, Any]:
        """Get analytics for a specific account"""
        params = {}
        if days:
            params['days'] = days
        return self._client._request('GET', f'/analytics/account/{account_id}', params=params)
    
    def list(
        self,
        account_id: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get all analytics data"""
        params = {}
        if account_id:
            params['accountId'] = account_id
        if start_date:
            params['startDate'] = start_date
        if end_date:
            params['endDate'] = end_date
        return self._client._request('GET', '/analytics', params=params)


class MediaAPI:
    """Media API methods"""
    
    def __init__(self, client: 'SchedulifyX'):
        self._client = client
    
    def get_upload_url(self, filename: str, content_type: str) -> Dict[str, Any]:
        """Get a presigned URL for uploading media"""
        return self._client._request('POST', '/media/upload-url', json={
            'filename': filename,
            'contentType': content_type
        })
    
    def upload(self, file_data: bytes, filename: str, content_type: str) -> str:
        """
        Upload a file and return the media URL.
        
        Args:
            file_data: The file content as bytes
            filename: The filename
            content_type: The MIME type (e.g., 'image/jpeg')
        
        Returns:
            The media URL to use in posts
        """
        response = self.get_upload_url(filename, content_type)
        upload_url = response['data']['uploadUrl']
        media_url = response['data']['mediaUrl']
        
        # Upload directly to presigned URL
        upload_response = requests.put(
            upload_url,
            data=file_data,
            headers={'Content-Type': content_type}
        )
        upload_response.raise_for_status()
        
        return media_url


class QueueAPI:
    """Queue API methods"""
    
    def __init__(self, client: 'SchedulifyX'):
        self._client = client
    
    def get_slots(self, profile_id: str) -> Dict[str, Any]:
        """Get queue schedule for a profile"""
        return self._client._request('GET', '/queue/slots', params={'profileId': profile_id})
    
    def set_slots(
        self,
        profile_id: str,
        timezone: str,
        slots: List[Dict[str, Any]],
        active: bool = True,
        reshuffle_existing: bool = False
    ) -> Dict[str, Any]:
        """Create or update queue schedule"""
        return self._client._request('PUT', '/queue/slots', json={
            'profileId': profile_id,
            'timezone': timezone,
            'slots': slots,
            'active': active,
            'reshuffleExisting': reshuffle_existing
        })
    
    def delete_slots(self, profile_id: str) -> Dict[str, Any]:
        """Delete queue schedule"""
        return self._client._request('DELETE', '/queue/slots', params={'profileId': profile_id})
    
    def get_next_slot(self, profile_id: str) -> Dict[str, Any]:
        """Get the next available slot"""
        return self._client._request('GET', '/queue/next-slot', params={'profileId': profile_id})
    
    def preview(self, profile_id: str, count: Optional[int] = None) -> Dict[str, Any]:
        """Preview upcoming slots"""
        params = {'profileId': profile_id}
        if count:
            params['count'] = count
        return self._client._request('GET', '/queue/preview', params=params)


class TenantsAPI:
    """Tenants API methods for multi-tenant integrations"""
    
    def __init__(self, client: 'SchedulifyX'):
        self._client = client
    
    def list(
        self,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        search: Optional[str] = None
    ) -> Dict[str, Any]:
        """List all tenants"""
        params = {}
        if limit:
            params['limit'] = limit
        if offset:
            params['offset'] = offset
        if search:
            params['search'] = search
        return self._client._request('GET', '/tenants', params=params)
    
    def get(self, tenant_id: str) -> Dict[str, Any]:
        """Get a single tenant"""
        return self._client._request('GET', f'/tenants/{tenant_id}')
    
    def create(
        self,
        external_id: str,
        email: Optional[str] = None,
        name: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create a new tenant"""
        data = {'externalId': external_id}
        if email:
            data['email'] = email
        if name:
            data['name'] = name
        if metadata:
            data['metadata'] = metadata
        return self._client._request('POST', '/tenants', json=data)
    
    def update(
        self,
        tenant_id: str,
        email: Optional[str] = None,
        name: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Update a tenant"""
        data = {}
        if email is not None:
            data['email'] = email
        if name is not None:
            data['name'] = name
        if metadata is not None:
            data['metadata'] = metadata
        return self._client._request('PATCH', f'/tenants/{tenant_id}', json=data)
    
    def delete(self, tenant_id: str) -> Dict[str, Any]:
        """Delete a tenant"""
        return self._client._request('DELETE', f'/tenants/{tenant_id}')
    
    def get_connect_url(self, tenant_id: str, platform: str) -> Dict[str, Any]:
        """Get OAuth URL for tenant to connect a platform"""
        return self._client._request('GET', f'/tenants/{tenant_id}/connect/{platform}')
    
    def list_accounts(self, tenant_id: str) -> Dict[str, Any]:
        """List tenant's connected accounts"""
        return self._client._request('GET', f'/tenants/{tenant_id}/accounts')
    
    def disconnect_account(self, tenant_id: str, account_id: str) -> Dict[str, Any]:
        """Disconnect a tenant's account"""
        return self._client._request('DELETE', f'/tenants/{tenant_id}/accounts/{account_id}')
    
    def connect_bluesky(
        self,
        tenant_id: str,
        identifier: str,
        app_password: str
    ) -> Dict[str, Any]:
        """Connect Bluesky account for tenant"""
        return self._client._request('POST', f'/tenants/{tenant_id}/connect/bluesky', json={
            'identifier': identifier,
            'appPassword': app_password
        })
    
    def connect_mastodon(
        self,
        tenant_id: str,
        instance: str,
        access_token: str
    ) -> Dict[str, Any]:
        """Connect Mastodon account for tenant"""
        return self._client._request('POST', f'/tenants/{tenant_id}/connect/mastodon', json={
            'instance': instance,
            'accessToken': access_token
        })


class SchedulifyX:
    """
    SchedulifyX API Client
    
    Usage:
        client = SchedulifyX('sk_live_YOUR_API_KEY')
        posts = client.posts.list()
    """
    
    def __init__(
        self,
        api_key: str,
        base_url: str = 'https://api.schedulifyx.com',
        timeout: int = 30
    ):
        """
        Initialize the SchedulifyX client.
        
        Args:
            api_key: Your SchedulifyX API key
            base_url: API base URL (default: https://api.schedulifyx.com)
            timeout: Request timeout in seconds (default: 30)
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        
        self._session = requests.Session()
        self._session.headers.update({
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
        })
        
        # Initialize API namespaces
        self.posts = PostsAPI(self)
        self.accounts = AccountsAPI(self)
        self.analytics = AnalyticsAPI(self)
        self.media = MediaAPI(self)
        self.queue = QueueAPI(self)
        self.tenants = TenantsAPI(self)
    
    def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None,
        json: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Make an API request"""
        url = f'{self.base_url}{endpoint}'
        
        try:
            response = self._session.request(
                method=method,
                url=url,
                params=params,
                json=json,
                timeout=self.timeout
            )
            
            if not response.ok:
                try:
                    error_data = response.json() if response.text else {}
                    if isinstance(error_data, dict):
                        error = error_data.get('error', {})
                        if isinstance(error, dict):
                            raise SchedulifyXError(
                                message=error.get('message', f'HTTP {response.status_code}'),
                                code=error.get('code', 'http_error'),
                                status=response.status_code,
                                details=error.get('details')
                            )
                except (ValueError, AttributeError):
                    pass
                raise SchedulifyXError(
                    message=f'HTTP {response.status_code}',
                    code='http_error',
                    status=response.status_code,
                    details=None
                )
            
            return response.json()
            
        except requests.exceptions.Timeout:
            raise SchedulifyXError('Request timeout', 'timeout', 408)
        except requests.exceptions.ConnectionError as e:
            raise SchedulifyXError(str(e), 'network_error', 0)
    
    def usage(self) -> Dict[str, Any]:
        """Get API usage statistics"""
        return self._request('GET', '/usage')
