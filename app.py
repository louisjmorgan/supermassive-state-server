import json
from flask import Flask, request
from flask_socketio import SocketIO, emit
from flask_cors import CORS
from lib.state_machine import StateMachine
from transitions.core import MachineError


# load config
with open(file='./config/master/states.json', encoding='utf8') as file:
    states = json.load(file)

with open(file='./config/master/transitions.json', encoding='utf8') as file:
    transitions = json.load(file)


# Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
CORS(app, resources={r"/*": {"origins": "*"}})
socketio = SocketIO(app, cors_allowed_origins="*")

# global callbacks


def broadcast_state_change(event):
    """updates all websocket listeners with the latest state"""
    print("after state change", event.state)
    # emit("state change", {"state": event.state.name},
    #      broadcast=True, namespace="/")


# set up state machine
machine = StateMachine(states=states,
                       transitions=transitions,
                       initial="intro",
                       auto_transitions=False,
                       after_state_change=broadcast_state_change,
                       send_event=True)


@app.route('/')
def hello():
    """hello world test function"""
    return '<h1>Hello, World!</h1>'


@app.route('/state', methods=['POST', 'GET'])
def set_state():
    """retrieve and update the state"""

    if request.method == 'POST':

        new_state = request.json['state']

        # may_transition = machine.may_to_state(new_state)
        # if not may_transition:
        #     return {"description": f"Cannot transition from {machine.state} to {new_state}"}, 400

        machine.to_state(machine, new_state)
        return {"state": machine.state, "triggers": machine.get_valid_triggers()}

    if request.method == 'GET':

        return {"state": machine.state, "triggers": machine.get_valid_triggers()}


@app.route('/next', methods=['POST'])
def next_state():
    """go to next ordered transition"""
    # if "next_state" not in machine.get_valid_triggers():
    #     return {"description": "This state does not have an ordered transition"}, 400
    machine.next_state()
    return {"state": machine.state, "triggers": machine.get_valid_triggers()}


@app.route('/trigger', methods=['POST'])
def trigger():
    """perform named trigger"""
    name = request.json["trigger"]
    print(machine.get_nested_triggers(), machine.state)
    # if name not in machine.get_valid_triggers():
    #     return {"description": f"Invalid trigger {name}"}, 400
    try:
        machine.trigger(name)
    except MachineError as e:
        print(e)
        return {"description": str(e)}, 400

    return {"state": machine.state, "triggers": machine.get_valid_triggers()}


@socketio.on("connect")
def connected():
    """event listener when client connects to the server"""
    print(request.sid)
    print("client has connected")
    emit("after connect", {"data": f"id: {request.sid} is connected"})


@socketio.on("disconnect")
def disconnected():
    """event listener when client disconnects to the server"""
    print("user disconnected")
    emit("disconnect", f"user {request.sid} disconnected", broadcast=True)


if __name__ == '__main__':

    socketio.run(app, debug=True, port=5001, extra_files=[
                 './config/master/states.json', './config/master/transitions.json',])
