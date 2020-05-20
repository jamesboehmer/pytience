from cmd import Cmd
from functools import wraps
from io import StringIO
from itertools import zip_longest
from pathlib import Path
import json

from colorama import Style, Fore, Back

from pytience.cards.deck import Card, Suit, Color
from pytience.games.solitaire.klondike import KlondikeGame

PROMPT = 'klondike{}> '
DEFAULT_SAVE_FILE = Path.home().joinpath('.pytience').joinpath('klondike.save')


def error_handler(function):
    @wraps(function)  # required to preserve docstrings for the help function
    def _error_handler(command, line):
        try:
            function(command, line)
        except Exception as error:  # pylint: disable=broad-except
            command.errors.append(error)
        name = function.__name__[3:]
        if line:
            name = name + ' {}'.format(line)
        command.prompt = PROMPT.format('[{}]'.format(name))

    return _error_handler


class KlondikeCmd(Cmd):

    def __init__(self, *args):
        super().__init__(*args)
        self.prompt = PROMPT.format('[type ? for help]')
        self.intro = None
        self.aliases = {
            't': self.do_tableau,
            'd': self.do_deal,
            'w': self.do_waste,
            'f': self.do_foundation,
            'n': self.do_new,
            'u': self.do_undo,
            'h': self.do_help,
            'q': self.do_quit,
            'EOF': self.do_quit
        }
        self.errors = []
        try:
            self.klondike = self.load()
        except FileNotFoundError as _:
            self.klondike = KlondikeGame()
        except Exception as e:  # pylint: disable=broad-except
            self.errors.append(e)
            self.klondike = KlondikeGame()

    def preloop(self):
        self.print_game()

    def do_help(self, arg):
        """Show the help menu"""
        print("\033[H\033[J")  # Clear screen
        super().do_help(arg)
        print("Press return to continue...")
        try:
            input()
        except EOFError:
            pass

    @staticmethod
    def do_quit(_):
        """Quit to terminal"""
        return True

    @error_handler
    def do_new(self, _):
        """Reset the game with a new shuffled deck"""
        self.klondike = KlondikeGame()

    @error_handler
    def do_undo(self, _):
        """Undo the last move"""
        self.klondike.undo()

    @error_handler
    def do_deal(self, _):
        """Deal a new card from the top of the stock"""
        self.klondike.deal()

    @error_handler
    def do_waste(self, line):
        """Usage: waste [<tableau pile>]
        Move the top card in the waste pile to the specified tableau pile.
        If the tableau pile is omitted, attempt to fit it in the foundation, or find a tableau pile.
        """
        args = tuple(map(int, line.split()))
        tableau_destination_pile = args[0] if args else None
        self.klondike.select_waste(tableau_destination_pile)

    @error_handler
    def do_foundation(self, line):
        """Usage: foundation <c(lubs)|d(diamonds|s(pades)|h(earts)> [<tableau pile num>]
        Move a card from the foundation to the tableau.
        If the tableau pile is omitted, attempt to find a tableau pile.
        """
        args = line.split()
        if not args:
            raise Exception("Usage: foundation <c|d|s|h> [<tableau pile num>]")
        suit = {
            'c': Suit.Clubs,
            'd': Suit.Diamonds,
            'h': Suit.Hearts,
            's': Suit.Spades
        }.get(args[0])
        if not suit:
            raise Exception("Usage: foundation <c|d|s|h> [<tableau pile num>]")
        tableau_destination_pile = int(args[1]) if len(args) > 1 else None
        self.klondike.select_foundation(suit, tableau_destination_pile)

    @error_handler
    def do_tableau(self, line):
        """Usage: tableau <from_pile> [<card_num> [to_pile]]
        Move a card from a specified tableau pile.
        If the card number is omitted, choose top card (-1).
        If the pile number is omitted, seek a foundation spot, then seek another tableau pile.
        """
        if not line:
            raise Exception('Usage: tableau <from_pile> [<card_num> [to_pile]]')
        args = tuple(map(int, line.split()))
        pile_num = args[0]
        card_num = args[1] if len(args) > 1 else -1
        destination_pile_num = args[2] if len(args) > 2 else None
        self.klondike.select_tableau(pile_num, card_num, destination_pile_num)

    @error_handler
    def do_solve(self, _):
        """Pick a card from the tableau to move to the foundation.
        All cards must be dealt and revealed.
        """
        self.klondike.solve()

    @staticmethod
    def save(klondike, filename=None):
        # TODO: change serialization to JSON
        DEFAULT_SAVE_FILE.parent.mkdir(parents=True, exist_ok=True)
        filename = filename or DEFAULT_SAVE_FILE
        with open(filename, 'w') as f:
            json.dump(klondike.dump(), f)

    @error_handler
    def do_save(self, line):
        """Usage: save [filename]"""
        filename = line or DEFAULT_SAVE_FILE
        self.save(self.klondike, filename)

    @staticmethod
    def load(filename=None):
        # TODO: change serialization to JSON
        filename = filename or DEFAULT_SAVE_FILE
        with open(filename, 'r') as f:
            game_dump = json.load(f)
            return KlondikeGame(game_dump=game_dump)

    @error_handler
    def do_load(self, line):
        """Usage: load [filename]"""
        self.klondike = self.load(line)

    def postcmd(self, stop, line):
        self.save(self.klondike)
        self.print_game()
        return stop

    def default(self, line):
        cmd, arg, line = self.parseline(line)
        if cmd == "_dump":
            print("\033[H\033[J")  # Clear screen
            self.print_dump()
            print("Press return to continue...")
            try:
                input()
            except EOFError:
                pass
            return False
        try:
            # if there are 1-3 integer args, assume they're tableau args
            _args = line.split()[:3]
            all(int(_arg) for _arg in _args)  # will raise ValueError if any args are not ints
            return self.do_tableau(line)
        except ValueError:
            pass
        if cmd in self.aliases:
            return self.aliases[cmd](arg)
        else:
            self.errors.append(Exception("*** Unknown syntax: {} ***".format(line)))

    def print_dump(self):
        print(json.dumps(self.klondike.dump(), indent=2, ensure_ascii=False))

    def print_game(self):
        def _paint_suit(_suit):
            return '{}{}{}{}'.format(Style.BRIGHT, Fore.RED if _suit.color == Color.Red else '', _suit.value,
                                     Style.RESET_ALL)

        def _paint_card(_card: Card, left_pad: int = 0, right_pad: int = 0):
            card_string = '#' if _card.is_concealed else str(_card)
            length = len(card_string)
            left = ' ' * (left_pad - length)
            right = ' ' * (right_pad - length - len(left))

            if _card.is_concealed or _card.pip is None:
                return '{}{}{}{}{}'.format(left, Style.BRIGHT, str(card_string), Style.RESET_ALL, right)

            return '{}{}{}{}{}{}'.format(left, Style.BRIGHT, _card.pip.value, _paint_suit(_card.suit), Style.RESET_ALL,
                                         right)

        # paint the whole screen at once to avoid flashing
        with StringIO() as buffer:

            # Clear screen
            buffer.write("\033[H\033[J")

            # Print status line
            if self.klondike.is_solved():
                status = 'Solved!'
            elif self.errors:
                status = str(self.errors.pop())
            else:
                status = ''
            buffer.write('{}{}{}{}{}\n'.format(Style.BRIGHT, Back.RED, Fore.BLACK, status, Style.RESET_ALL))

            buffer.write("Score: {}\n".format(self.klondike.score))

            buffer.write("Stock: {}\n".format(self.klondike.stock.remaining))

            waste = '[{}]'.format(', '.join([_paint_card(card) for card in self.klondike.waste]))
            buffer.write('Waste: {}\n'.format(waste))

            # Print foundation
            foundation = []
            for suit, pile in self.klondike.foundation.piles.items():
                if not pile:
                    foundation.append('[{}]'.format(_paint_suit(suit)))
                else:
                    painted_card = _paint_card(pile[-1])
                    foundation.append(painted_card.ljust(3))
            buffer.write('Foundation: {}\n'.format('  '.join(foundation)))

            buffer.write('Tableau:\n')
            column_width = 3
            spacer = ' ' * 2
            buffer.write(
                '{}\n'.format(spacer.join(str(p).ljust(column_width) for p in range(len(self.klondike.tableau.piles)))))
            buffer.write(
                '{}\n'.format(spacer.join('-' * column_width for _ in range(len(self.klondike.tableau.piles)))))

            # Transpose the piles so they can be written as equal-length rows
            transposed_piles = dict(enumerate(zip_longest(*self.klondike.tableau.piles)))
            for row_num, row in transposed_piles.items():
                buffer.write('{}\n'.format(
                    spacer.join(
                        [_paint_card(_card, right_pad=column_width) if _card else '[ ]' if row_num == 0 else '   ' for
                         _card in
                         row]
                    )
                ))
            # Pad to 13 lines
            buffer.write('\n' * (19 - len(transposed_piles)))

            print(buffer.getvalue())


def play():
    while True:
        try:
            KlondikeCmd().cmdloop()

            break
        except KeyboardInterrupt:
            pass


if __name__ == '__main__':
    play()
