from typing import List, Callable, NoReturn
from functools import partial


class Undoable:
    def __init__(self):
        self.undo_stack: List[List[Callable]] = []

    def undo(self) -> NoReturn:
        """Undo the last event on the undo stack"""
        if self.undo_stack:
            action_stack = self.undo_stack.pop()
            while action_stack:
                undo_action = action_stack.pop()
                undo_action()

    def export_undo_stack(self) -> object:
        """
        Creates a serialization-friendly representation of the undo stack using
        function names and args instead of partials
        :return: A language-agnostic object representing the undo stack
        """
        return [
            [{'function_name': action.func.__name__, 'args': action.args} for action in actions]
            for actions in self.undo_stack
        ]

    def import_undo_stack(self, undo_stack) -> NoReturn:
        """
        Turn a list of lists of serialized functions from `export_undo_stack` into partials.
        Since the function_names are relative to self, care must be made not to
        :param undo_stack: A list of lists of
        """
        self.undo_stack = [
            [
                partial(getattr(self, action['function_name']), *action['args']) for action in actions
            ]
            for actions in undo_stack
        ]
