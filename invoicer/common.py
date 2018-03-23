from functools import wraps
from flask import request, redirect, session, url_for


bs4_color_themes = [
    'black', 'blue', 'azure', 'green', 'orange', 'red', 'purple'
]


# See here https://www.w3schools.com/w3css/w3css_color_themes.asp
# `banner` is `w3-theme-d1`, and `table_header` is `w3-theme`
color_theme_data = {
    'red': {
        'banner': {'color': '#fff', 'background_color': '#f32617'},
        'table_header': {'color': '#fff', 'background_color': '#f44336'},
    },
    'khaki': {
        'banner': {'color': '#fff', 'background_color': '#ecdf6c'},
        'table_header': {'color': '#000', 'background_color': '#f0e68c'},
    },
    'blue-grey': {
        'banner': {'color': '#fff', 'background_color': '#57707d'},
        'table_header': {'color': '#fff', 'background_color': '#607d8b'},
    }
}


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
