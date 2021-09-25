from flask import Flask
from celery_task import test

app = Flask(__name__)


@app.route('/')
def hello_world():  # put application's code here
    test.delay()
    return 'Hello World!'


if __name__ == '__main__':
    app.run()
