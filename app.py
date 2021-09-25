from flask import Flask, render_template
from celery_task import test

app = Flask(__name__)


@app.route('/')
def hello_world():  # put application's code here
    test.delay()
    return render_template("index.html")


if __name__ == '__main__':
    app.run()
