from typing import List, NoReturn

from pytience.cards.deck import Deck, Card, Suit
from pytience.games.solitaire.foundation import Foundation
from pytience.games.solitaire.tableau import Tableau
from pytience.games.util import Undoable, UndoAction
from pytience.games.solitaire.exception import IllegalMoveException, IllegalTableauMoveException, \
    IllegalFoundationMoveException, TableauPileIndexError
from pytience.cards.exception import NoCardsRemainingException

POINTS_WASTE_FOUNDATION = 10
POINTS_WASTE_TABLEAU = 5
POINTS_TABLEAU_FOUNDATION = 15


class KlondikeGame(Undoable):
    def __init__(self, game_dump: object = None):
        if game_dump:
            self.load(game_dump)
        else:
            self.stock: Deck = Deck().shuffle()
            self.tableau: Tableau = Tableau(7, self.stock)
            self.waste: List[Card] = []
            self.score = 0
            self.foundation = Foundation(suits=Suit)
            super().__init__()

    def undo_deal(self, undo_replenish: bool):
        self.stock.undeal(self.waste.pop().conceal())
        if undo_replenish:
            self.waste.extend(map(lambda c: c.reveal(), self.stock.deal_all()))

    def deal(self) -> NoReturn:
        """Deal n cards from the stock into the waste pile"""

        replenished = False
        if self.stock.remaining == 0:
            if self.waste:
                self.stock.replenish(c.conceal() for c in self.waste)
                self.waste.clear()
                replenished = True  # we need to know this for the undo event
        try:
            self.waste.append(self.stock.deal().reveal())
            self.undo_stack.append(UndoAction(self.undo_deal, [replenished]))
        except NoCardsRemainingException:
            raise IllegalMoveException('No cards left in the stock or waste')

    def adjust_score(self, points: int):
        self.score += points

    def undo_select_foundation(self):
        self.adjust_score(POINTS_TABLEAU_FOUNDATION)
        self.tableau.undo()
        self.foundation.undo()

    def select_foundation(self, suit: Suit, tableau_destination_pile: int = None):
        card = self.foundation.get(suit)

        destinations = [tableau_destination_pile] if tableau_destination_pile is not None else range(len(self.tableau))
        for pile_num in destinations:
            try:
                self.tableau.put([card], pile_num)
                self.adjust_score(-POINTS_TABLEAU_FOUNDATION)
                self.undo_stack.append(UndoAction(self.undo_select_foundation))
                return
            except TableauPileIndexError as e:
                self.foundation.undo()
                raise e
            except IllegalTableauMoveException:
                pass

        self.foundation.undo()
        raise IllegalMoveException('No tableau fit for {}'.format(str(card)))

    def undo_select_waste(self, undo_foundation: bool, card_string: str):
        if undo_foundation:
            self.adjust_score(-POINTS_WASTE_FOUNDATION)
            self.foundation.undo()
        else:
            self.adjust_score(-POINTS_WASTE_TABLEAU)
            self.tableau.undo()
        self.waste.append(Card.parse_card(card_string))

    def select_waste(self, tableau_destination_pile: int = None):
        """Try to find the best fit for the top waste card"""

        if not self.waste:
            raise IllegalMoveException('No cards in the waste.')
        card = self.waste.pop()
        if tableau_destination_pile is None:
            try:
                self.foundation.put(card)
                self.adjust_score(POINTS_WASTE_FOUNDATION)
                self.undo_stack.append(UndoAction(self.undo_select_waste, [True, str(card)]))
                return
            except IllegalFoundationMoveException:
                pass

        destinations = [tableau_destination_pile] if tableau_destination_pile is not None else range(len(self.tableau))
        for pile_num in destinations:
            try:
                self.tableau.put([card], pile_num)
                self.adjust_score(POINTS_WASTE_TABLEAU)
                self.undo_stack.append(UndoAction(self.undo_select_waste, [False, str(card)]))
                return
            except IllegalTableauMoveException:
                pass
        self.waste.append(card)
        raise IllegalMoveException(
            'No {}tableau fit for {}'.format(
                'foundation or ' if tableau_destination_pile is None else '',
                str(card)
            )
        )

    def undo_seek_tableau_to_foundation(self):
        self.adjust_score(-POINTS_TABLEAU_FOUNDATION)
        self.foundation.undo()
        self.tableau.undo()

    def seek_tableau_to_foundation(self):
        # Seek a tableau pile whose top card fits in the foundation
        for _pile_num in range(len(self.tableau)):
            try:
                cards = self.tableau.get(_pile_num, -1)
                self.foundation.put(cards[0])
                self.score += POINTS_TABLEAU_FOUNDATION
                self.undo_stack.append(UndoAction(self.undo_seek_tableau_to_foundation))
                return
            except IllegalTableauMoveException:
                # The chosen pile has no cards.  No tableau undo needed.
                pass
            except IllegalFoundationMoveException:
                # There was no fit in the foundation, so put the card back in the tableau and move on
                self.tableau.undo()
        raise IllegalMoveException("No tableau cards fit in the foundation.")

    def undo_select_tableau(self, undo_foundation: bool):
        if undo_foundation:
            self.adjust_score(-POINTS_TABLEAU_FOUNDATION)
            self.foundation.undo()
        else:
            self.tableau.undo()
        self.tableau.undo()

    def select_tableau(self, pile_num: int = None, card_num: int = None, destination_pile_num: int = None):
        if pile_num is None:
            self.seek_tableau_to_foundation()
            return
        else:
            # Instead of seeking a foundation pile
            if pile_num == destination_pile_num:
                raise IllegalTableauMoveException("Destination pile can't be the same as the origin.")

            # A specific tableau pile was chosen, so use it
            cards = self.tableau.get(pile_num, card_num)

            # First see if it fits in the foundation
            if len(cards) == 1 and destination_pile_num is None:
                try:
                    self.foundation.put(cards[0])
                    self.score += POINTS_TABLEAU_FOUNDATION
                    self.undo_stack.append(UndoAction(self.undo_select_tableau, [True]))
                    return
                except IllegalFoundationMoveException:
                    pass  # Don't undo the tableau get because we need to search for another tableau destination now

            # If it doesn't fit in the foundation, seek a tableau pile or use the given tableau destination
            destinations = [destination_pile_num] if destination_pile_num else range(len(self.tableau.piles))
            for destination in destinations:
                if pile_num != destination:
                    try:
                        self.tableau.put(cards, destination)
                        self.undo_stack.append(UndoAction(self.undo_select_tableau, [False]))
                        return
                    except IllegalTableauMoveException:
                        pass
            self.tableau.undo()
        # We couldn't find a card in the tableau that fit in the foundation
        # OR The chosen tableau card didn't fit in the foundation
        # OR The chosen tableau card didn't fit anywhere in the tableau
        # OR the chosen tableau card didn't fit in the chosen tableau pile
        raise IllegalMoveException('No fit for Pile {} Card {}'.format(pile_num, card_num))

    def is_solvable(self) -> bool:
        if len(self.stock) + len(self.waste) > 0:
            return False
        for pile in self.tableau.piles:
            if pile and pile[0].is_concealed:
                return False
        return True

    def is_solved(self) -> bool:
        return self.foundation.is_full

    def solve(self):
        if not self.is_solvable():
            raise IllegalMoveException("Can't solve with cards remaining in the stock or waste.")

        if not self.is_solved():
            self.seek_tableau_to_foundation()

    def dump(self) -> object:
        return {
            "score": self.score,
            "stock": self.stock.dump(),
            "waste": list(map(str, self.waste)),
            "foundation": self.foundation.dump(),
            "tableau": self.tableau.dump(),
            "undo_stack": self.dump_undo_stack()
        }

    def load(self, game_dump: object) -> NoReturn:
        self.score = game_dump.get("score", 0)
        self.stock = Deck(deck_dump=game_dump.get("stock", dict()))
        self.waste = list(map(Card.parse_card, game_dump.get("waste", list())))
        self.foundation = Foundation(foundation_dump=game_dump.get("foundation", dict()))
        self.tableau = Tableau(tableau_dump=game_dump.get("tableau", dict()))
        self.load_undo_stack(game_dump.get("undo_stack", list()))
