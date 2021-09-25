from celery import Celery

app = Celery('celery_task', broker='amqps://chirboie:DJ_cJFHcT8QMDegH2JR7N5Jm2SDZbVki@shrimp.rmq.cloudamqp.com/chirboie',
             backend='db+sqlite:///celery_backend.sqlite3')


@app.task
def test():
    print("bruh")