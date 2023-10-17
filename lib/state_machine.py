"""module providing state machine logic with custom helper methods"""
from transitions.extensions import HierarchicalMachine
from lib.utils import listify, flatten_list, unique_list


class StateMachine(HierarchicalMachine):
    """State Machine"""

    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, **kwargs)
        self.add_ordered_transitions()
        # print(self.get_triggers())

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

    # transition callbacks
    def log_event(self, event):
        """test method"""
        print(event)
