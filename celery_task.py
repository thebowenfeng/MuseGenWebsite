from celery import Celery
import os
from read_midi import Preprocess
from network import RNN_Model, Bidirectional_Model

app = Celery('celery_task', broker='amqps://chirboie:DJ_cJFHcT8QMDegH2JR7N5Jm2SDZbVki@shrimp.rmq.cloudamqp.com/chirboie',
             backend='db+sqlite:///celery_backend.sqlite3')


existing_music = {
    "moonlight1": "/static/mid_files/moonlight1.mid",
    "fur elise": "/static/mid_files/for_else_by_beethoven.mid",
    "alla turca": "/static/mid_files/alla-turca.mid",
    "campanella": "/static/mid_files/lacampanella.mid"
}

existing_music_tempo = {
    "moonlight1": 2000000,
    "fur elise": 1000000,
    "alla turca": 500000,
    "campanella": 500000
}

@app.task(bind=True)
def gen_music(self, train_filename, model, epoch, length):
    task_id = self.request.id
    if os.path.isdir(task_id):
        os.makedirs(task_id)

    self.update_status(
        state='PROCESSING'
    )
    print("processing")

    processed = Preprocess(existing_music[train_filename])
    if model == 'gru':
        mymodel = RNN_Model(processed)
    else:
        mymodel = Bidirectional_Model(processed)

    self.update_status(
        state='TRAINING'
    )
    print("training")
    mymodel.train(epoch=int(epoch))

    self.update_status(
        state='WRITING'
    )
    print("writing")
    mymodel.generate(num_notes=int(length), prompt=[1, 2, 3], output_file=f"{task_id}/new.mid",
                     tempo=existing_music_tempo[train_filename])

    self.update_status(
        state='SUCCESS'
    )

    return True
