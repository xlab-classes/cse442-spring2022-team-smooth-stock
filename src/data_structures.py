from flask_login import LoginManager, UserMixin
import app

class User(UserMixin):
    is_authenticated = False
    is_active = False
    is_anonymous = False
    id = 0
    def get_id(self):
        return (self.id)

