from flask import Flask, render_template, request, send_file
from flask_sqlalchemy import SQLAlchemy
import os
from read_midi import Preprocess
from network import RNN_Model, Bidirectional_Model

app = Flask(__name__)
app.secret_key = "hello world"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"

existing_music = {
    "moonlight1": "static/mid_files/moonlight1.mid",
    "fur-elise": "static/mid_files/for_elise_by_beethoven.mid",
    "alla-turca": "static/mid_files/alla-turca.mid",
    "campanella": "static/mid_files/lacampanella.mid"
}

existing_music_tempo = {
    "moonlight1": 2000000,
    "fur-elise": 500000,
    "alla-turca": 1000000,
    "campanella": 500000
}

db = SQLAlchemy(app)


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.String(100), nullable=False)
    task_status = db.Column(db.String(100), nullable=True)
    current_epoch = db.Column(db.Integer, nullable=True, default=0)
    total_epoch = db.Column(db.Integer, nullable=False)


@app.route('/', methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/start_task", methods=["GET"])
def start_task():
    if 'existing' in request.args:
        task_id = request.args["task_id"]
        train = request.args['trainMusic']
        model = request.args['model']
        epoch = request.args['epoch']
        length = request.args['length']
    else:
        # Will be implemented later, for custom music uploads
        task_id, train, model, epoch, length = None, None, None, None, None

    task = Task(task_id=task_id, total_epoch=int(epoch))
    db.session.add(task)
    db.session.commit()

    print("start")
    task.task_status = "Creating job"
    db.session.commit()

    if not os.path.isdir(f"outputs/{task_id}"):
        os.makedirs(f"outputs/{task_id}")

    task.task_status = "Processing"
    db.session.commit()
    print("processing")

    processed = Preprocess(existing_music[train])
    if model == 'gru':
        mymodel = RNN_Model(processed, task_id)
    else:
        mymodel = Bidirectional_Model(processed, task_id)

    task.task_status = "Training"
    print("training")
    db.session.commit()

    mymodel.train(epoch=int(epoch))

    task.task_status = "Writing"
    print("writing")
    db.session.commit()

    mymodel.generate(num_notes=int(length), prompt=[1, 2, 3], output_file=f"outputs/{task_id}/new.mid",
                     tempo=existing_music_tempo[train])

    task.task_status = "Success"
    db.session.commit()
    return "success"


@app.route('/generate/<task_id>', methods=["GET"])
def generate(task_id):
    return render_template("generate.html", task_id=task_id)


@app.route("/get_status", methods=['GET'])
def get_status():
    task_id = request.args["task_id"]

    task = Task.query.filter_by(task_id=task_id).first()

    if task is None:
        return "none"
    else:
        if task.task_status == "Training":
            return {"status": task.task_status, "epoch": task.current_epoch, "total": task.total_epoch}
        else:
            return {"status": task.task_status}


@app.route("/update_status", methods=['GET'])
def update_status():
    task_id = request.args["task_id"]
    curr_epoch = request.args["epoch"]

    task = Task.query.filter_by(task_id=task_id).first()
    task.current_epoch = int(curr_epoch)

    db.session.commit()

    return "True"


@app.route("/download/<task_id>", methods=["GET"])
def download(task_id):
    if os.path.isdir(f"outputs/{task_id}"):
        return send_file(f"outputs/{task_id}/new.mid", as_attachment=True)
    else:
        return "<h1>This file does not exist on the server</h1>"


if __name__ == '__main__':
    app.run(debug=True)
