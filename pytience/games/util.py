from typing import List, Callable, NoReturn, Any
from dataclasses import dataclass, field


@dataclass
class UndoAction:
    function: Callable
    args: List[Any] = field(default_factory=list)

    def dump(self):
        return {'action': self.function.__name__, 'args': self.args}

    def __call__(self, *_, **__):
        self.function(*self.args)


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
            [action.dump() for action in actions]
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
                UndoAction(getattr(self, action['action']), *action['args']) for action in actions
            ]
            for actions in undo_stack
        ]
