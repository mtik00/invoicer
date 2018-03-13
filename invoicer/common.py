from functools import wraps
from flask import request, redirect, session, url_for


w3_color_themes = [
    '',
    'red', 'pink', 'purple', 'deep-purple', 'blue', 'light-blue', 'cyan', 'teal',
    'green', 'light-green', 'lime', 'khaki', 'yellow', 'amber', 'orange',
    'deep-orange', 'blue-grey', 'brown', 'grey', 'dark-grey', 'black'
]

bs4_color_themes = [
    'black', 'blue', 'azure', 'green', 'orange', 'red', 'purple'
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
