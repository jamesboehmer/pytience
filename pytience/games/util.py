from typing import List, Callable, NoReturn


class Undoable:  # pylint: disable=too-few-public-methods
    def __init__(self):
        self.undo_stack: List[List[Callable]] = []

    def undo(self) -> NoReturn:
        """Undo the last action on the undo stack"""
        if self.undo_stack:
            function_stack = self.undo_stack.pop()
            while function_stack:
                undo_function = function_stack.pop()
                undo_function()
