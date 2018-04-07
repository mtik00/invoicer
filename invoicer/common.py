try:
    from urlparse import urlparse, urljoin
except Exception:
    from urllib.parse import urlparse, urljoin

from flask import request


def form_is_deleting():
    """
    Returns ``True`` if the form was posted to delete something; ``False``
    otherwise.
    """
    return bool(
        ('delete' in request.form) or
        (request.form.get('validate_delete', '').lower() == 'delete') or
        ('delete' in request.form.get('delete_modal_target', ''))
    )


def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return (test_url.scheme in ('http', 'https')) and (ref_url.netloc == test_url.netloc)
