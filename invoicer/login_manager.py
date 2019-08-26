from flask_login import LoginManager

from .models import User


login_manager = LoginManager()
login_manager.login_view = "login_page.login"
login_manager.login_message_category = "error"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
