from enum import Enum
from typing import Dict, List, Iterable, Union, Type

from pytience.cards.deck import Suit, Card, Pip
from pytience.cards.exception import NoCardsRemainingException
from pytience.games.solitaire import CARD_VALUES
from pytience.games.solitaire.exception import ConcealedCardNotAllowedException, NoSuchSuitException, \
    IllegalFoundationBuildOrderException
from pytience.games.util import Undoable, UndoAction


# TODO: make more specific exceptions so that error conditions can be less ambiguous
class Foundation(Undoable):

    def __init__(self, suits: Union[Type[Enum], Iterable]):
        self.piles: Dict[Suit, List[Card]] = {suit: [] for suit in suits}
        super().__init__()

    def undo_get(self, suit: str, card: str):
        _suit = Suit(suit)
        _card = Card.parse_card(card)
        pile = self.piles.get(_suit)
        pile.append(_card)

    def get(self, suit: Suit) -> Card:
        if suit not in self.piles:
            raise NoSuchSuitException('No such suit.')
        pile = self.piles.get(suit)
        if not pile:
            raise NoCardsRemainingException('No foundation cards for suit {}'.format(suit))

        card = pile.pop()
        self.undo_stack.append(UndoAction(self.undo_get, [str(suit), str(card)]))
        return card

    def undo_put(self, suit: str):
        _suit = Suit(suit)
        pile = self.piles.get(_suit)
        pile.pop()

    def put(self, card: Card):
        if card.is_concealed:
            raise ConcealedCardNotAllowedException('Foundation cards must be revealed')
        pile = self.piles[card.suit]
        if card.pip == Pip.Ace:
            pile.append(card)
            self.undo_stack.append(UndoAction(self.undo_put, [str(card.suit)]))
        elif not pile:
            raise IllegalFoundationBuildOrderException('Foundation cards must be built sequentially per suit.')
        else:
            value = CARD_VALUES[card.pip]
            top_value = CARD_VALUES[pile[-1].pip]
            if value != top_value + 1:
                raise IllegalFoundationBuildOrderException('Foundation cards must be build sequentially per suit.')
            pile.append(card)
            self.undo_stack.append(UndoAction(self.undo_put, [str(card.suit)]))

    @property
    def is_full(self) -> bool:
        return all(len(pile) == 13 for pile in list(self.piles.values()))
