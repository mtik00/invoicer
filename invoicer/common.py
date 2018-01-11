from functools import wraps
from flask import request, redirect, session, url_for


def login_required(f):
    """
    Decorator used to make sure the user is logged in before handling the
    request.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function
