from enum import Enum
from functools import partial
from typing import Dict, List, Iterable, Union, Type

from pytience.cards.deck import Suit, Card, Pip
from pytience.cards.exception import NoCardsRemainingException
from pytience.games.solitaire import CARD_VALUES
from pytience.games.solitaire.exception import ConcealedCardNotAllowedException, NoSuchSuitException, \
    IllegalFoundationBuildOrderException
from pytience.games.util import Undoable


# TODO: make more specific exceptions so that error conditions can be less ambiguous
class Foundation(Undoable):

    def __init__(self, suits: Union[Type[Enum], Iterable]):
        self.piles: Dict[Suit, List[Card]] = {suit: [] for suit in suits}
        super().__init__()

    def get(self, suit: Suit) -> Card:
        if suit not in self.piles:
            raise NoSuchSuitException('No such suit.')
        pile = self.piles.get(suit)
        if not pile:
            raise NoCardsRemainingException('No foundation cards for suit {}'.format(suit))

        card = pile.pop()
        self.undo_stack.append([
            partial(pile.append, card)
        ])
        return card

    def put(self, card: Card):
        undo_log = []
        if card.is_concealed:
            raise ConcealedCardNotAllowedException('Foundation cards must be revealed')
        pile = self.piles[card.suit]
        if card.pip == Pip.Ace:
            pile.append(card)
            undo_log.append(partial(pile.pop))
        elif not pile:
            raise IllegalFoundationBuildOrderException('Foundation cards must be built sequentially per suit.')
        else:
            value = CARD_VALUES[card.pip]
            top_value = CARD_VALUES[pile[-1].pip]
            if value != top_value + 1:
                raise IllegalFoundationBuildOrderException('Foundation cards must be build sequentially per suit.')
            pile.append(card)
            undo_log.append(partial(pile.pop))
        if undo_log:
            self.undo_stack.append(undo_log)

    @property
    def is_full(self) -> bool:
        return all(len(pile) == 13 for pile in list(self.piles.values()))
