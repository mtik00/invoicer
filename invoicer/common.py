from functools import wraps
from flask import request, redirect, session, url_for


color_themes = [
    'red', 'pink', 'purple', 'deep-purple', 'blue', 'light-blue', 'cyan', 'teal',
    'green', 'light-green', 'lime', 'khaki', 'yellow', 'amber', 'orange',
    'deep-orange', 'blue-grey', 'brown', 'grey', 'dark-grey', 'black'
]


def login_required(f):
    """
    Decorator used to make sure the user is logged in before handling the
    request.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login_page.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function
