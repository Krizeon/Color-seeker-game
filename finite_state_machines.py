"""
list of all finite state machine classes
"""
import fsm

class HiddenPlatformHandler(fsm.FiniteStateMachineMixin):
    state_machine = {
        'off': ('on'),
        'on': ('off'),
    }
    def on_change_state(self, previous_state, next_state, **kwargs):
        if previous_state == 'off' and next_state == 'on':
            pass

    state = 'off'
