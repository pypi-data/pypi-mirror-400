import base64
import json
import requests
import urllib3
import os

from zoneinfo import ZoneInfo
from urllib.parse import urljoin
from datetime import datetime, timedelta

from trendminer_interface.constants import DEFAULT_USER_AGENT

from .response_hooks import raise_all
from .iterators import PageIterator, PageIteratorNoTotal, ContinuationIterator


class TrendMinerSession(requests.Session):
    """Low level client for TrendMiner API calls

    This class automates some boilerplate that are needed for TrendMiner appliance requests, or SDK development:
    - Handles Keycloak authentication by adding the access token to the headers, and refreshing expired token
    - Adds the appliance base url to every request, so that a relative url can be given
    - Provide easy access to decoded Keycloak token
    - Provides interfaces for automatically iterating over paginated responses
    - Globally set SSL verification, request timeout parameters, and user agent for all requests. Currently, only the
    turning off of SSL verification by the user (`verify=False`) is supported.

    The session is meant for internal use, but could also be used to send custom requests through the client instance
    (e.g. ``client.session.get("custom_endpoint/object")``)
    """

    def __init__(
            self,
            base_url,
            client_id,
            client_secret,
            username,
            password,
            refresh_token,
            access_token_getter,
            verify,
            timeout,
            proxies,
            user_agent=DEFAULT_USER_AGENT,
    ):
        super().__init__()

        self.base_url = base_url

        # Remove verification warnings if the user consciously set verify to False
        if not verify:
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        self.verify = verify

        self.timeout = timeout
        self.headers.update({
            "User-Agent": user_agent,
            "Accept": "application/json, text/plain, */*"
        })

        # For some reason, setting the base Session.proxies leads to errors
        self.client_proxies = proxies

        self.client_id = client_id
        self.__store_secret(client_secret)

        self.username = username

        # Custom access token getter function
        if access_token_getter:
            self._token_refresh = lambda: self.__custom_token_setter(access_token_getter)  # set custom function
            self._token_refresh()  # retrieve access token immediately

        # Direct refresh token input
        elif refresh_token:
            self.token = {"refresh_token": refresh_token}  # set refresh token directly
            self._token_refresh = self.__refresh_manual_token  # refresh with refresh token
            self._token_refresh() # get new access token immediately

        # User authentication
        elif username or password:
            self.__get_password_token(password)  # get refresh and access tokens
            self._token_refresh = self.__refresh_password_token  # refresh with refresh token

        # Client authentication; does not use refresh tokens
        else:
            self._token_refresh = self.__refresh_client_token
            self._token_refresh()  # get access token

    def __store_secret(self, client_secret):
        self.__k = os.urandom(16)
        if client_secret is None:
            self.__s = None
        else:
            self.__s = _xor_cipher(client_secret.encode(), self.__k)

    def __get_secret(self):
        if self.__s is None:
            return None
        return _xor_cipher(self.__s, self.__k).decode()

    def __custom_token_setter(self, getter):
        """Custom access token retrieval and setting based on user-provided function

        Sets the following properties
        - `TrendMinerSession.token` (dict) : the new keycloak JWT
        - `TrendMinerSession.headers` (dict) : authentication headers added to every request
        - `TrendMinerSession.token_expires` (datetime) : access token expiration time

        Parameters
        ----------
        getter : fun
            User-provided getter
        """
        self.token = {"access_token": getter()}
        self.headers.update({"Authorization": "Bearer " + self.token["access_token"]})
        self.token_expires = datetime.fromtimestamp(self.token_decoded["exp"], tz=ZoneInfo("UTC"))
        if self.token_expires <= datetime.now(tz=ZoneInfo("UTC")):
            raise ValueError("EXPIRED ACCESS TOKEN: provided access token getter function returned an expired token")

    def __request_token(self, data: dict):
        """Request a new token from the appliance and store it to the Session

        Sets the following properties
        - `TrendMinerSession.token` (dict) : the new keycloak JWT
        - `TrendMinerSession.headers` (dict) : authentication headers added to every request
        - `TrendMinerSession.token_expires` (datetime) : access token expiration time

        Parameters
        ----------
        data : dict
            Data for the authentication POST request
        """

        # Anchor to determine expiration time
        request_time = datetime.now(tz=ZoneInfo("UTC"))

        # Avoid checking expiration time on authentications calls
        self.token_expires = None

        response = self.post(
            url=f"/auth/realms/trendminer/protocol/openid-connect/token",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data=data,
        )
        self.token = response.json()
        self.headers.update({"Authorization": "Bearer " + self.token["access_token"]})
        self.token_expires = request_time + timedelta(seconds=self.token["expires_in"])

    def __refresh_client_token(self):
        self.__request_token({
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.__get_secret(),
        })

    def __get_password_token(self, password):
        self.__request_token({
            "grant_type": "password",
            "client_id": self.client_id,
            "client_secret": self.__get_secret(),
            "username": self.username,
            "password": password,
        })

    def __refresh_password_token(self):
        self.__request_token({
            "grant_type": "refresh_token",
            "client_id": self.client_id,
            "client_secret": self.__get_secret(),
            "refresh_token": self.token["refresh_token"],
        })

    def __refresh_manual_token(self):
        self.__request_token({
            "grant_type": "refresh_token",
            "client_id": "trendminer-ui",
            "refresh_token": self.token["refresh_token"]
        })

    @property
    def token_decoded(self):
        """Dictionary with info from decoded Keycloak token

        Returns
        -------
        dict
            Decoded Keycloak token
        """
        if self.token is None:
            return None

        _, data, _ = self.token["access_token"].split(".")

        # Add padding
        missing_padding = len(data) % 4
        if missing_padding:
            data += "=" * (4 - missing_padding)

        return json.loads(base64.urlsafe_b64decode(data).decode())

    def _join_base_url(self, url):
        """Adds base url so the relative path can be given in requests

        Parameters
        ----------
        url : str
            Relative url (does not include the appliance base url)

        Returns
        -------
        str
            Complete url, including the appliance base url, to be used in requests
        """
        return urljoin(self.base_url, url)

    def _set_kwargs(self, kwargs):
        """Prepare the request kwargs by inserting default parameters, if not already present."""

        # Default values
        kwargs.setdefault('timeout', self.timeout)
        kwargs.setdefault('verify', self.verify)
        kwargs.setdefault('proxies', self.client_proxies)
        kwargs.setdefault('hooks', {"response": [raise_all]})  # Raise all unsuccessful responses

        return kwargs

    def request(self, method, url, **kwargs):
        """Overrides requests.Session.request to add additional functionalities.

        Takes relative url, automatically updates keycloak token if needed, and sets instance values as defaults for
        timeout and verify.

        Because direct methods like Session.post(...) just call Session.request(method="POST", ...), we only need to
        overwrite this method to take care of all TrendMinerSession requests.

        Parameters
        ----------
        method : str
            GET, POST, PUT or DELETE
        url : str
            Relative url. The base url of the appliance is added automatically

        Returns
        -------
        requests.Response
            request response
        """

        # Updated expired token
        if self.token_expires is not None and (self.token_expires <= datetime.now(tz=ZoneInfo("UTC"))):
            self._token_refresh()

        # Perform base request with added session kwargs and using relative url
        return super().request(method=method, url=self._join_base_url(url), **self._set_kwargs(kwargs))

    def paginated(self, keys, total=True, json_params=False):
        """Creates an interface to iterate over paginated data

        The interface can iterate a request over multiple pages, and joins the main outputs together in a single list.

        Works for data that is literally paginated, i.e., where the current page and total numer of pages are returned
        as part of the response.

        Parameters
        ----------
        keys : list
            References to the data that needs to be extracted from the subsequent requests. All other data in the json
            response is discarded. For example, for ``keys=["content", "properties"]``, the iterator will return a list
            of ``response.json()["content"]["properties"]``.
        total : bool, default True
            Whether the total number of pages is returned by the endpoint. When this is not the case (at least one known
            example), we cannot go by the totalPages parameter and instead need to iterate until the size of the content
            is smaller than the get size. In this case we do need to pay attention that the max get size is actually
            attainable by the endpoint. Otherwise, only the first page will be returned.
        json_params : bool, default False,
            Whether the `size` and `page` parameters are given as part of the json payload to the post request rather
            than url parameters.

        Returns
        -------
        PageIterator
            An instance that can iterate over multiple requests until all data is returned, that extracts data from
            every response based on the given keys, giving a list of outputs.
        """
        if total:
            return PageIterator(session=self, keys=keys, json_params=json_params)
        return PageIteratorNoTotal(session=self, keys=keys, json_params=json_params)

    def continuation(self, keys):
        """Creates an interface to iterate over paginated data

        The interface can iterate a request over multiple pages, and joins the main outputs together in a single list.

        Works for data that is returned with a continuation token. Subsequent requests using the returned continuation
        tokens need to be done, until the response is empty.

        Parameters
        ----------
        keys : list
            References to the data that needs to be extracted from the subsequent requests. All other data in the json
            response is discarded. For example, for ``keys=["content", "properties"]``, the iterator will return a list
            of ``response.json()["content"]["properties"]``.

        Returns
        -------
        ContinuationIterator
            An instance that can iterate over multiple requests until all data is returned, that extracts data from
            every response based on the given keys, giving a list of outputs.
        """
        return ContinuationIterator(session=self, keys=keys)


def _xor_cipher(data, key):
    return bytes(a ^ b for a, b in zip(data, key * (len(data) // len(key) + 1)))
