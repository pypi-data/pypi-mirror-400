import abc

from .session import TrendMinerSession


class BaseClient(abc.ABC):
    """Handles all authentication for the client. Stores the session."""

    def __init__(
            self,
            url,
            client_id,
            client_secret,
            username,
            password,
            refresh_token,
            access_token_getter,
            verify,
            timeout,
            proxies,
    ):

        self.session = TrendMinerSession(
            base_url=url,
            verify=verify,
            timeout=timeout,
            proxies=proxies,
            client_id=client_id,
            client_secret=client_secret,
            username=username,
            password=password,
            refresh_token=refresh_token,
            access_token_getter=access_token_getter
        )

    @property
    def url(self):
        """TrendMiner appliance url"""
        return self.session.base_url

    def __repr__(self):
        return f"<< {self.__class__.__name__}" \
               f" | {self.url}" \
               f" | {self.session.token_decoded['preferred_username']} >>"

