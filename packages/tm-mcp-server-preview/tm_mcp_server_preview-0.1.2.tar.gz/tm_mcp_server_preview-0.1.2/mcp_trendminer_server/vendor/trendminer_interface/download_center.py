import time

from requests import RequestException
from trendminer_interface.base import AuthenticatableBase


class DownloadCenter(AuthenticatableBase):
    """Download items from the appliance that were requested earlier"""

    def __init__(self, client, location):
        super().__init__(client=client)
        self.location = location

    def download(self, link, max_attempts=2, wait=5):
        """Download data from a givne url

        Parameters
        ----------
        link : str
            Download link
        max_attempts : int, default 2
            Number of attempts to download before throwing an error
        wait : float, default 5
            Time to wait between attempts, in seconds
        """
        # Get reference
        data = {"link": link}
        response = self.client.session.post(f"{self.location}/download/generate", json=data)
        reference = response.json()["data"]

        # Download data
        attempts = 0
        success = False
        while attempts < max_attempts:
            try:
                response = self.client.session.get(f"notifications/download/public", params={"data": reference})
                success = True
                break
            except RequestException:  # pragma: no cover
                attempts += 1
                time.sleep(wait)

        if not success:  # pragma: no cover
            raise FileNotFoundError(link)

        return response
