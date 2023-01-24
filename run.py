from app import flask_app

if __name__ == '__main__':
    HOST = "0.0.0.0"
    PORT = 80
    DEBUG = False
    flask_app.config['SECRET_KEY'] = 'my_uno-tuti_secret_things_inoutparks'
    flask_app.run(host=HOST, debug=DEBUG, port=PORT)