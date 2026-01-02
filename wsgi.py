"""Entry point for Flask Applicatoin
"""
from application import create_app
import os

env = os.getenv('ENV')
print(env)
if env == 'development':
    app = create_app()
    with app.app_context():
        if __name__ == "__main__":
            app.run(host='0.0.0.0', port=3060, debug=True)
elif env == 'production':
    app = create_app()