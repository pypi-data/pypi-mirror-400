import trendminer_interface._input as ip
from trendminer_interface.constants import MAX_GET_SIZE



class PageIterator:
    """Can iterate a request over multiple pages, and joins the main outputs together in a single list.

    Works for data that is literally paginated, i.e., where the current page and total numer of pages are returned as
    part of the response.
    """
    def __init__(self, session, keys, json_params):
        self.session = session
        self.keys = ip.any_list(keys)
        if json_params:
            self.setter_key = "json"
        else:
            self.setter_key = "params"
        self.json_params = json_params

    def _extract_content(self, data):
        """Extract relevant content from a single json response"""
        value = data
        try:
            for key in self.keys:
                value = value[key]
            return value
        except KeyError:
            return []

    def _iterate_requests(self, method, url, **kwargs):
        """Iterate a given request to extract all paginated data"""
        kwargs.setdefault(self.setter_key, {"page": 0})
        kwargs[self.setter_key].update({"page": 0})

        responses = [self.session.request(method=method, url=url, **kwargs)]
        total_pages = responses[0].json()["page"]["totalPages"]

        if total_pages == 1:
            return responses

        for page in range(1, total_pages):
            kwargs[self.setter_key].update({"page": page})
            responses.append(self.session.request(method=method, url=url, **kwargs))

        return responses

    def _content_list(self, method, url, **kwargs):
        """Iterate a given request, and then extract the relevant data from each request, returning a list"""
        responses = self._iterate_requests(method=method, url=url, **kwargs)
        return [item for r in responses for item in self._extract_content(r.json())]

    def get(self, url, **kwargs):
        """Iterate a GET request, returning a list of content requested from each subsequent request"""
        return self._content_list(method="GET", url=url, **kwargs)

    def post(self, url, **kwargs):
        """Iterate a POST request, returning a list of content requested from each subsequent request"""
        return self._content_list(method="POST", url=url, **kwargs)


class PageIteratorNoTotal(PageIterator):
    """Iterate over multiple pages when the total number of pages is not returned correctly

    Some endpoints always return the totalPages parameters as 1, even though there are more pages. The only way to
    correctly iterate in that case is to keep incrementing the page number until the response size is smaller than the
    get size.
    """

    def _iterate_requests(self, method, url, **kwargs):
        """This method can no longer be used, we need to extract as we iterate"""
        raise NotImplementedError

    def _content_list(self, method, url, **kwargs):
        """Iterate a given request, and then extract the relevant data from each request, returning a list"""
        full_output = []
        kwargs.setdefault(self.setter_key, {"page": 0, "size": MAX_GET_SIZE})
        page = 0
        size = kwargs[self.setter_key]["size"]
        while True:
            kwargs[self.setter_key].update({"page": page})
            response = self.session.request(method=method, url=url, **kwargs)
            output = response.json()
            for key in self.keys:
                output = output[key]
            full_output = full_output + output
            if len(output) < size:
                break
            page += 1

        return full_output