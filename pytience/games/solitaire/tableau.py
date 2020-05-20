from typing import List, NoReturn

from pytience.cards.deck import Deck, Card, Pip
from pytience.games.solitaire import CARD_VALUES
from pytience.games.solitaire.exception import TableauCardIndexError, TableauPileIndexError, \
    TableauCardNotAvailableException, IllegalTableauBuildOrderException, ConcealedCardNotAllowedException
from pytience.games.util import Undoable, UndoAction


class Tableau(Undoable):
    def __init__(self, size: int = 7, deck: Deck = None, tableau_dump: object = None):
        if tableau_dump:
            self.load(tableau_dump)
        else:
            self.piles: List[List[Card]] = [[] for _ in range(max(size, 1))]

            # Cards should be dealt one per tableau pile, revealing the top card as it's dealt.
            if deck is not None:
                for starting_pile_num in range(len(self.piles)):
                    for pile_num in range(starting_pile_num, len(self.piles)):
                        card = deck.deal()
                        if pile_num == starting_pile_num:
                            card.reveal()
                        self.piles[pile_num].append(card)

            super().__init__()

    def undo_put(self, pile_num: int, num_cards: int):
        pile = self.piles[pile_num]
        for _ in range(num_cards):
            pile.pop()

    def put(self, cards: List[Card], pile_num: int) -> NoReturn:
        if cards[0].is_concealed:
            raise ConcealedCardNotAllowedException('Concealed cards may not be built on the tableau.')
        if pile_num > len(self.piles) - 1:
            raise TableauPileIndexError('No such tableau pile: {}'.format(pile_num))
        pile = self.piles[pile_num]
        if not pile:
            if cards[0].pip == Pip.King:
                pile.extend(cards)
                self.undo_stack.append(UndoAction(self.undo_put, [pile_num, len(cards)]))
                return
            else:
                raise IllegalTableauBuildOrderException('Only Kings may be built on empty tableau piles.')
        elif cards[0].color == pile[-1].color or CARD_VALUES[cards[0].pip] != CARD_VALUES[pile[-1].pip] - 1:
            raise IllegalTableauBuildOrderException(
                'Tableau cards must be built in descending order with alternate colors')
        else:
            pile.extend(cards)
            self.undo_stack.append(UndoAction(self.undo_put, [pile_num, len(cards)]))

    def undo_get(self, pile_num: int, card_strings: List[str], re_conceal: bool):
        if re_conceal:
            self._conceal(pile_num)
        self.piles[pile_num].extend(map(Card.parse_card, card_strings))

    def get(self, pile_num: int, card_num: int) -> List[Card]:
        if card_num is None:
            raise TableauCardIndexError('Card num not specified')
        if pile_num > len(self.piles) - 1:
            raise TableauPileIndexError('No such tableau pile: {}'.format(pile_num))
        pile = self.piles[pile_num]

        cards = pile[card_num:]
        if not cards:
            raise TableauCardIndexError('No card at pile [{}][{}]'.format(pile_num, card_num))
        if cards[0].is_concealed:
            raise TableauCardNotAvailableException('Pile {} Card {} is concealed'.format(pile_num, card_num))

        # chop off the end of the pile
        for _ in range(len(cards)):
            pile.pop()
        revealed = self._reveal(pile_num)
        self.undo_stack.append(UndoAction(self.undo_get, [pile_num, list(map(str, cards)), revealed]))
        return cards

    def _reveal(self, pile_num: int) -> bool:
        """
        Reveal the top card in the specified pile.
        Intended for internal use only.
        :param pile_num:
        :return: True if card was flipped, False if it was already revealed
        """
        pile = self.piles[pile_num]
        if pile and pile[-1].is_concealed:
            pile[-1].reveal()
            return True
        else:
            return False

    def _conceal(self, pile_num: int) -> bool:
        """
        Conceal the top card in the specified pile.
        Intended for internal use only.
        :param pile_num:
        :return: True if card was flipped, False if it was already revealed
        """
        pile = self.piles[pile_num]
        if pile and pile[-1].is_revealed:
            pile[-1].conceal()
            return True
        else:
            return False

    def dump(self) -> object:
        """
        Dumps the current state of the Tableau
        :return: A JSON-ready object
        """
        return {
            "piles": [
                list(map(str, pile))
                for pile in self.piles
            ],
            "undo_stack": self.dump_undo_stack()
        }

    def load(self, tableau_dump: object) -> NoReturn:
        """
        Import the tableau state previously exported with dump()
        :param tableau_dump: An object previously exported by dump()
        """
        self.piles = [[Card.parse_card(card_string) for card_string in pile] for pile in tableau_dump["piles"]]
        self.load_undo_stack(tableau_dump["undo_stack"])

    def __repr__(self):
        return str([len(p) for p in self.piles])

    def __len__(self):
        return len(self.piles)
