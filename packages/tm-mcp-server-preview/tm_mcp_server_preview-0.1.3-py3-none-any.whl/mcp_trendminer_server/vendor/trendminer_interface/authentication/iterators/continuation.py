import trendminer_interface._input as ip
from trendminer_interface.constants import MAX_GET_SIZE


class ContinuationIterator:
    """Can iterate a request over multiple pages, and joins the main outputs together in a single list.

    Works for data that is returned with a continuation token. Subsequent requests using the returned continuation
    tokens need to be done, until the response size is smaller than the get size.
    """
    def __init__(self, session, keys):
        self.session = session
        self.keys = ip.any_list(keys)

    def _content_list(self, method, url, **kwargs):
        """Iterate a given request, and then extract the relevant data from each request, returning a list"""
        full_output = []
        continuation_token = ""
        kwargs.setdefault("json", {"fetchSize": MAX_GET_SIZE})
        size = kwargs["json"]["fetchSize"]
        while True:
            kwargs["json"].update({"continuationToken": continuation_token})
            response = self.session.request(method=method, url=url, **kwargs)
            output = response.json()
            for key in self.keys:
                output = output[key]
            full_output = full_output + output
            if len(output) < size:
                break
            continuation_token = response.json()["page"]["continuationToken"]

        return full_output

    def post(self, url, **kwargs):
        """Iterate a POST request, returning a list of content requested from each subsequent request"""
        return self._content_list(method="POST", url=url, **kwargs)
