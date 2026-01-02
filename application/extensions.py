"""Various 3rd party flask extensions that are intialized to be used
in app factory.
"""

from secure import Secure
from flask_bcrypt import Bcrypt
from flask_executor import Executor
from flask_wtf.csrf import CSRFProtect

secure_headers = Secure()
bcrypt = Bcrypt()
exe = Executor()
csrf = CSRFProtect()
