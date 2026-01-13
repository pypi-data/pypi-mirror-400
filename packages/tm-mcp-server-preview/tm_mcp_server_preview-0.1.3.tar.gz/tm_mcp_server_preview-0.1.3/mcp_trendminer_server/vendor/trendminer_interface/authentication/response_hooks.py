import requests
import json
import re
from trendminer_interface.exceptions import ResourceNotFound


def obscure_password(string):
    """Replaces password in (failed) responses with ***

    Parameters
    ----------
    string : str
        Response content potentially containing a plain-text password

    Returns
    -------
    str
        Input string, but with potential passwords replaced by '***'
    """
    return re.sub(
        "((?<=password=)|(?<=client_id=)|(?<=client_secret=))[^\n&]*", "***", string
    )


def expand_http_error(err):
    """Expand message of HTTP error to include the request body and response

    This allows a user to more easily see why a request might have failed

    Parameters
    ----------
    err : requests.HTTPError
        Original error which needs to be expanded

    Returns
    -------
    requests.HTTPError
        New error with the original request body, and the response content added
    """
    body = err.response.request.body

    try:
        body = json.dumps(json.loads(body), indent=4)
    except (json.decoder.JSONDecodeError, TypeError):
        pass

    if not isinstance(body, str):
        body = type(body).__name__
    else:
        body = obscure_password(body)

    try:
        content = json.dumps(err.response.json(), indent=4)
        content = obscure_password(content)
    except json.decoder.JSONDecodeError:
        content = str(err.response.content)

    new_message = f"{str(err)}\n" \
                  f"{err.response.request.method} REQUEST:\n" \
                  f"{body}\n\n" \
                  f"RESPONSE:\n" \
                  f"{content}"

    # Expand message
    err.args = (new_message,*err.args[1:])

    return err


def raise_all(response, *args, **kwargs):
    """Check response validity and raise error if response was not ok

    This function is used as the default hook for requests sent from a client session, meaning by default, failed
    requests will throw a HTTPError to the end user.

    Parameters
    ----------
    response : requests.Response
        Response that needs to be checked for status, raises an HTTPError when status was not ok

    Returns
    -------
    None
        Only checks input and potentially raises error, does not return anything
    """
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as err:
        if err.response is not None and err.response.status_code == 404:
            raise ResourceNotFound(err) from err
        raise expand_http_error(err) from err


def ignore_404(response, *args, **kwargs):
    """Check response and raises error for everything except for 404 status

    This function can be used as a hook for requests where it could be part of the normal workflow that a resource does
    not exist. For example, if we try to retrieve the index status of a Tag that is not indexed, the response status
    will be 404. Rather than throw an error to the user, we just want to tell the user that the tag is not indexed.

    Parameters
    ----------
    response : requests.Response
        Response that needs to be checked for status, raises an HTTPError when status was not ok or 404

    Returns
    -------
    None
        Only checks input and potentially raises error, does not return anything
    """
    if not response.status_code == 404:
        raise_all(response)

