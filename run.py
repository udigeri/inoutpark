from app import flask_app
from app import init_db
import sys


if __name__ == '__main__':
    HOST = "0.0.0.0"
    PORT = 80
    DEBUG = False
    flask_app.config['SECRET_KEY'] = 'uno-tuti_secret_things_inoutparks'


    if len(sys.argv) > 1:
        # command = sys.argv[1]
        init_db(flask_app)


    flask_app.run(host=HOST, debug=DEBUG, port=PORT)