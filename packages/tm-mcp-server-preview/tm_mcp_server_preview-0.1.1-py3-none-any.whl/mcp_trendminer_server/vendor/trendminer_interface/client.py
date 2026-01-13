import functools
import warnings
import pandas as pd

from datetime import datetime
from zoneinfo import ZoneInfo

from .constants import SUPPORTED_VERSIONS
from .exceptions import VersionMismatchWarning
from .authentication import BaseClient
from .context import ContextClient
from .user import UserClient
from .tag.tag import TagClient
from .datasource import DatasourceClient
from .folder import FolderClient
from .trendhub import TrendHubClient
from .asset import AssetClient
from .search import SearchClient
from .monitor import MonitorClient
from .tagbuilder import FormulaClient, AggregationClient
from .dashhub import DashHubClient
from .io import IOClient
from .filter import FilterClient
from .fingerprint import FingerprintClient

class TrendMinerClient(
    BaseClient,
    ContextClient,
    UserClient,
    TagClient,
    DatasourceClient,
    FolderClient,
    TrendHubClient,
    AssetClient,
    SearchClient,
    MonitorClient,
    FormulaClient,
    DashHubClient,
    AggregationClient,
    IOClient,
    FilterClient,
    FingerprintClient,
):
    """Handles requests to the appliance. All methods are implemented as properties of this client.

    Parameters
    ----------
    url : str
        TrendMiner appliance url
    client_id: str, optional
        Valid client id for the given appliance. Required unless using direct token authentication.
        Learn to create client: https://trendminer.elevio.help/en/articles/143-confighub-security
    client_secret: str, optional
        Client secret matching the given client id. Required unless using direct token authentication.
    username: str
        Setting username provides access to the resources of this user (e.g., saved items).
    password: str, optional
        Password matching the given username.
    refresh_token: str, optional
        Valid long-lived Keycloak refresh token. When setting the refresh token, not other credentials need to be set.
        A valid access token will be generated from the refresh token.
    access_token_getter : fun, optional
        Function for retrieving a valid short-lived Keycloak access token. When setting this function no other
        credentials need to be set. For use in embedded applications. E.g., in MLHub notebooks, use
        `access_token_getter=lambda: os.environ["KERNEL_USER_TOKEN"]`
    verify: bool or str, default False
        Sets verify parameter for the requests to appliance. Setting to False prevents SSLError in case
        appliance SSL certificates are not valid. More info:
        https://requests.readthedocs.io/en/latest/user/advanced/#ssl-cert-verification
    proxies: dict, optional
        Proxy configuration (https://requests.readthedocs.io/en/latest/user/advanced/#proxies)
    timeout: float or tuple, default (10, 120)
        Timeout settings for requests (https://requests.readthedocs.io/en/latest/user/advanced/#timeouts)
    tz: str or ZoneInfo, default UTC
        Client timezone. All time outputs given in client timezone. All inputs without explicit timezone are
        considered to be in the client timezone.
    """

    def __init__(
            self,
            url,
            client_id=None,
            client_secret=None,
            username=None,
            password=None,
            access_token_getter=None,
            refresh_token=None,
            verify=True,
            tz=ZoneInfo("UTC"),
            timeout=(10, 120),
            proxies=None,
    ):
        BaseClient.__init__(
            self,
            url=url,
            client_id=client_id,
            client_secret=client_secret,
            username=username,
            password=password,
            refresh_token=refresh_token,
            access_token_getter=access_token_getter,
            verify=verify,
            timeout=timeout,
            proxies=proxies,
        )

        # Set the timezone
        self.tz = ZoneInfo(tz) if isinstance(tz, str) else tz

        # Check if the current version is supported
        self._check_version()

    @property
    @functools.lru_cache(maxsize=10)
    def version(self):
        """TrendMiner appliance version

        Returns
        -------
        version : str
            The current version
        """
        response = self.session.get("/trendhub/version")
        return response.json()["release.version"]

    @property
    @functools.lru_cache(maxsize=10)
    def resolution(self):
        """TrendMiner appliance index resolution

        Returns
        -------
        pandas.Timedelta
        """
        response = self.session.get("/ds/configurations/INDEX_RESOLUTION")
        return pd.Timedelta(seconds=float(response.json()["value"]))

    @property
    @functools.lru_cache(maxsize=10)
    def index_horizon(self):
        """TrendMiner appliance index horizon

        Returns
        -------
        datetime
        """
        response = self.session.get("/ds/timeseries/indexhorizon")
        return  pd.Timestamp(response.json()["horizon"]).tz_convert(tz=self.tz)

    def _check_version(self):
        if not any([self.version.startswith(version) for version in SUPPORTED_VERSIONS]):
            warnings.warn(
                f"This SDK version was tested for use with TrendMiner versions "
                f"[{' | '.join(SUPPORTED_VERSIONS)}] while your TrendMiner version is [{self.version}]. "
                f"Some functionality might not work as expected. ",
                VersionMismatchWarning
            )
