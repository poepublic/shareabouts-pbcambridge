from django.http import HttpRequest
from django.urls import reverse
import requests
from urllib.parse import urlparse

from django.conf import settings
from .config import get_shareabouts_config, _ShareaboutsConfig


def make_api_root(dataset_root):
    components = dataset_root.split('/')
    if dataset_root.endswith('/'):
        return '/'.join(components[:-4]) + '/'
    else:
        return '/'.join(components[:-3]) + '/'


def make_auth_root(dataset_root):
    return make_api_root(dataset_root) + 'users/'


def make_resource_uri(resource, root):
    resource = resource.lstrip('/')
    root = root.rstrip('/')
    uri = '%s/%s' % (root, resource)
    return uri


def get_api_sessionid(django_http_request):
    return django_http_request.COOKIES.get('sa-api-sessionid')


def make_api_session(dataset_root, api_sessionid):
    """
    Create a requests session for the Shareabouts API.
    """
    api_session = requests.Session()
    api_session.headers['Content-type'] = 'application/json'
    api_session.headers['Accept'] = 'application/json'

    if api_sessionid:
        api_session.cookies.set(
            'sessionid',
            api_sessionid,
            domain=urlparse(dataset_root).netloc,
        )

    return api_session


class ShareaboutsApiError (Exception):
    def __init__(self, msg, errors):
        super().__init__(msg)
        self.errors = errors


class ShareaboutsApi:
    def __init__(
        self,
        config: _ShareaboutsConfig,
        request: HttpRequest,
        dataset_root: str | None = None,
        sessionid: str | None = None
    ):
        if config is None:
            config = get_shareabouts_config(settings.SHAREABOUTS.get('CONFIG'))
            config.update(settings.SHAREABOUTS.get('CONTEXT', {}))

        if dataset_root is None:
            dataset_root = settings.SHAREABOUTS.get('DATASET_ROOT')

        if (dataset_root.startswith('file:')):
            if not request:
                raise ValueError('A request object is required to use a file-based dataset_root.')
            dataset_root = request.build_absolute_uri(reverse('api_proxy', args=('',)))

        if sessionid is None:
            if not request:
                raise ValueError('A request object is required to dynamically get the sessionid.')
            sessionid = get_api_sessionid(request)

        self.config = config
        self.dataset_root = dataset_root
        self.auth_root = make_auth_root(dataset_root)
        self.root = make_api_root(dataset_root)
        self.sessionid = sessionid
        self.session = make_api_session(dataset_root, sessionid)

    def get(self, resource, default=None, **kwargs):
        uri = make_resource_uri(resource, root=self.dataset_root)
        res = self.session.get(uri, params=kwargs)
        self.update_sessionid()
        return (res.text if res.status_code == 200 else default)

    def current_user(self, default=None, **kwargs):
        if not hasattr(self, '_cached_user'):
            uri = make_resource_uri('current', root=self.auth_root)
            res = self.session.get(uri, **kwargs)
            self.update_sessionid()

            self._cache_user(res.json() if res.status_code == 200 else default)
        return self._cached_user

    def login(self, username, password, **kwargs):
        payload = {
            'username': username,
            'password': password,
        }
        uri = make_resource_uri('current', root=self.auth_root)
        res = self.session.post(uri, json=payload, **kwargs)
        self.update_sessionid()

        if res.status_code == 200:
            self._cache_user(res.json())
            return True
        else:
            raise ShareaboutsApiError(res.text, res.json().get('errors'))

    def provider_login_complete(self, provider, **kwargs):
        uri = make_resource_uri('login/' + provider, root=self.auth_root)
        res = self.session.get(uri, **kwargs)
        self.update_sessionid()

        if res.status_code == 200:
            return True
        else:
            raise ShareaboutsApiError(res.text, res.json().get('errors'))

    def logout(self, **kwargs):
        uri = make_resource_uri('current', root=self.auth_root)
        res = self.session.delete(uri, **kwargs)
        self.update_sessionid()

        if res.status_code == 204:
            self._cache_user(None)
            return True
        else:
            raise ShareaboutsApiError(res.text, {})

    def update_sessionid(self):
        """
        Update the sessionid from the cookies in the session.
        """
        self.sessionid = self.session.cookies.get(
            'sessionid',
            domain=urlparse(self.dataset_root).netloc,
        )

    def _cache_user(self, user):
        self._cached_user = user

    def _invalidate_user(self):
        del self._cached_user

    def respond_with_sessionid(self, response):
        if self.sessionid:
            response.set_cookie('sa-api-sessionid', self.sessionid)
            print(f'Updating sessionid: {self.sessionid}')
        else:
            response.delete_cookie('sa-api-sessionid')
            print('Deleting sessionid')
        return response
