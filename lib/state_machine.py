"""module providing state machine logic with custom helper methods"""
import json
from transitions.extensions import HierarchicalMachine
from lib.utils import listify, flatten_list, unique_list
from functools import reduce


def load_config():
    """load config data from json files and combine into single state and single transition object"""
    # load master config
    with open(file='./config/master/states.json', encoding='utf8') as file:
        master_states = json.load(file)

    with open(file='./config/master/transitions.json', encoding='utf8') as file:
        master_transitions = json.load(file)

    standalone_state_configs = [
        ("phone", './config/phone/states.json'),
        ("taskroom", './config/taskroom/states.json'),
    ]

    for entry in standalone_state_configs:
        (key, path) = entry
        print(key, path)
        # load nested taskroom config
        with open(file=path, encoding='utf8') as file:
            standalone_state = json.load(file)

        master_states[master_states.index(
            list(filter(
                lambda s: s["name"] == key, master_states))[0]
        )] = standalone_state
    print(master_states)
    return (master_states, master_transitions)

def state_reducer(parent, state):
    if isinstance(state, list):
        reduce(state_reducer, state, parent)
    if state not in parent:
        parent[state] = {}
    return parent[state]

def build_state_tree(state_list, tree):
    if isinstance(state_list, list):
        for sub_list in state_list:
            if isinstance(sub_list, list):
                new_tree = build_state_tree(sub_list, tree)
                return new_tree
            else:
                tree[sub_list] = build_state_tree(state_list[1:], {})
                return tree
    else:
        return {}
        


class StateMachine(HierarchicalMachine):
    """State Machine"""

    def __init__(self, *args, **kwargs):
        (states, transitions) = load_config()

        super().__init__(self, *args, **kwargs, states=states, transitions=transitions)
        # self.add_ordered_transitions()
        print(self.get_valid_triggers())

    # helper methods
    def get_valid_transitions(self):
        """returns transitions that are valid from the current state"""
        return [*filter(lambda t: t.source == self.state, self.get_transitions())]

    def get_valid_triggers(self):
        """returns triggers that are valid from the current state"""
        state = listify(self.state)
        triggers = [self.get_nested_triggers(
            nested_state.split(self.state_cls.separator)) for nested_state in state]
        return unique_list(flatten_list(triggers))

    def may_to_state(self, dest):
        """checks if a given transition is allowed"""
        return dest in [transition.dest for transition in self.get_valid_transitions()]

    def get_state_tree(self):
        """gets array containing hierarchy of nested/parallel states"""
        return json.loads(json.dumps((self.build_state_tree(self.state, self.state_cls.separator))))
        # return [nested_state.split(self.state_cls.separator) for nested_state in listify(self.state)]

    # transition callbacks
    def log_event(self, event):
        """test method"""
        print(event)

    def on_choose_taskroom_question(self, event):
        """Handles selection of taskroom question by the controller"""
        print(self.state, event)
