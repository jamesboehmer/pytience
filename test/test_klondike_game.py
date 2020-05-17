from unittest import TestCase

from pytience.games.solitaire.klondike import KlondikeGame
from pytience.cards.deck import Card, Pip, Suit
from pytience.games.exception import IllegalMoveException


class KlondikeGameTestCase(TestCase):
    def test_create(self):
        klondike = KlondikeGame()
        self.assertTrue(klondike.stock.is_shuffled, "The klondike deck should be shuffled.")
        self.assertEqual(len(klondike.stock), 24, "Klondike starting stock should have 24 cards remaining.")
        self.assertEqual(len(klondike.waste), 0, "Klondike starting waste should be empty.")
        self.assertEqual(klondike.score, 0, "Klondike starting score should be 0.")
        self.assertEqual(len(klondike.foundation.piles), 4, "Klondike foundation should have 4 piles.")
        self.assertEqual(len(klondike.undo_stack), 0, "Klondike undo stack should be empty.")

    def test_deal(self):
        klondike = KlondikeGame()
        self.assertEqual(len(klondike.stock), 24, "Klondike starting stock should have 24 cards remaining.")
        self.assertEqual(len(klondike.waste), 0, "Klondike starting waste should be empty.")
        self.assertEqual(len(klondike.undo_stack), 0, "Klondike undo stack should be empty.")
        klondike.deal()
        self.assertEqual(len(klondike.stock), 23, "Klondike stock should have 23 cards remaining after dealing.")
        self.assertEqual(len(klondike.waste), 1, "Klondike waste should have 1 card.")
        self.assertEqual(len(klondike.undo_stack), 1, "Klondike undo stack should have 1 event.")

        for _ in range(23):
            klondike.deal()
        self.assertEqual(len(klondike.stock), 0, "Klondike stock should have 0 cards remaining after dealing them all.")
        self.assertEqual(len(klondike.waste), 24, "Klondike waste should have all 24 cards.")
        self.assertEqual(len(klondike.undo_stack), 24, "Klondike undo stack should have 24 events.")

        klondike.deal()
        self.assertEqual(len(klondike.stock), 23,
                         "Klondike stock should have 23 cards remaining after cycling the waste.")
        self.assertEqual(len(klondike.waste), 1, "Klondike waste should have 1 card after replenishing the stock.")
        self.assertEqual(len(klondike.undo_stack), 25, "Klondike undo stack should have 25 events.")

        klondike.stock.cards.clear()
        klondike.waste.clear()
        self.assertEqual(len(klondike.stock), 0,
                         "Klondike stock should have 0 cards remaining after clearing the deck.")
        self.assertEqual(len(klondike.waste), 0, "Klondike waste should have 0 cards after clearing.")
        self.assertEqual(len(klondike.undo_stack), 25, "Klondike undo stack should still have 25 events.")

        with self.assertRaises(IllegalMoveException,
                               msg="Klondike should raise an exception if there are no cards left to deal or recycle."):
            klondike.deal()

        self.assertEqual(len(klondike.stock), 0,
                         "Klondike stock should still have 0 cards remaining after clearing the deck.")
        self.assertEqual(len(klondike.waste), 0, "Klondike waste should still have 0 cards after clearing.")
        self.assertEqual(len(klondike.undo_stack), 25, "Klondike undo stack should still have 25 events.")

    def test_seek_tableau_to_foundation(self):
        klondike = KlondikeGame()
        # force a situation with multiple aces and a matching two.  Place the card below it too so it doesn't become
        # a foundation candidate after it's revealed
        for pile_num, (hidden_pip, hidden_suit, pip, suit) in enumerate([
            (Pip.King, Suit.Clubs, Pip.Jack, Suit.Hearts),
            (None, None, Pip.Two, Suit.Hearts),
            (None, None, Pip.Jack, Suit.Spades),
            (Pip.King, Suit.Diamonds, Pip.Ace, Suit.Diamonds),
            (None, None, Pip.Four, Suit.Clubs),
            (Pip.Queen, Suit.Clubs, Pip.Two, Suit.Clubs),
        ]):
            klondike.tableau.piles[pile_num + 1][-2] = Card(hidden_pip, hidden_suit)
            klondike.tableau.piles[pile_num + 1][-1] = Card(pip, suit).reveal()
        klondike.tableau.piles[0][0] = Card(Pip.Ace, Suit.Clubs).reveal()

        # precondition
        self.assertEqual(len(klondike.tableau.piles[0]), 1, "Starting pile 0 should have 1 card.")
        self.assertEqual(len(klondike.tableau.piles[4]), 5, "Starting pile 4 should have 5 cards.")
        self.assertEqual(len(klondike.tableau.piles[6]), 7, "Starting pile 6 should have 7 cards.")
        self.assertEqual(sum(len(pile) for pile in klondike.foundation.piles.values()), 0,
                         "There should be no cards in the foundation.")
        self.assertEqual(len(klondike.undo_stack), 0, "There should be 0 undo events.")

        # first card moves
        klondike.seek_tableau_to_foundation()
        self.assertEqual(len(klondike.tableau.piles[0]), 0, "Pile 0 should have lost a card to the foundation.")
        self.assertEqual(len(klondike.tableau.piles[4]), 5, "Pile 4 should still have 5 cards.")
        self.assertEqual(len(klondike.tableau.piles[6]), 7, "Pile 6 should still have 7 cards.")
        self.assertEqual(sum(len(pile) for pile in klondike.foundation.piles.values()), 1,
                         "There should be 1 card in the foundation.")
        self.assertEqual(len(klondike.undo_stack), 1, "There should be 1 undo event.")

        # second card moves
        klondike.seek_tableau_to_foundation()
        self.assertEqual(len(klondike.tableau.piles[0]), 0, "Pile 1 should still have 1 card.")
        self.assertEqual(len(klondike.tableau.piles[4]), 4, "Pile 4 should have lost a card to the foundation.")
        self.assertEqual(len(klondike.tableau.piles[6]), 7, "Pile 6 should still have 7 cards.")
        self.assertEqual(sum(len(pile) for pile in klondike.foundation.piles.values()), 2,
                         "There should be 2 cards in the foundation.")
        self.assertEqual(len(klondike.undo_stack), 2, "There should be 2 undo events.")

        # third card moves
        klondike.seek_tableau_to_foundation()
        self.assertEqual(len(klondike.tableau.piles[0]), 0, "Pile 1 should still have 1 card.")
        self.assertEqual(len(klondike.tableau.piles[4]), 4, "Pile 4 should still have 4 cards.")
        self.assertEqual(len(klondike.tableau.piles[6]), 6, "Pile 6 should have lost a card to the foundation.")
        self.assertEqual(sum(len(pile) for pile in klondike.foundation.piles.values()), 3,
                         "There should be 3 cards in the foundation.")
        self.assertEqual(len(klondike.undo_stack), 3, "There should be 3 undo events.")

        # no cards left to move
        with self.assertRaises(IllegalMoveException,
                               msg="Should raise exception if there are no foundation candidates."):
            klondike.seek_tableau_to_foundation()

        self.assertEqual(sum(len(pile) for pile in klondike.foundation.piles.values()), 3,
                         "There should still be 3 cards in the foundation.")
        self.assertEqual(len(klondike.undo_stack), 3, "There should still be 3 undo events.")

    def test_adjust_score(self):
        klondike = KlondikeGame()
        self.assertEqual(klondike.score, 0, "Starting score should be 0")
        self.assertEqual(len(klondike.undo_stack), 0, "Starting undo_stack should be empty.")

        klondike.adjust_score(37)
        self.assertEqual(klondike.score, 37, "The score should now be 37")
        self.assertEqual(len(klondike.undo_stack), 0, "Undo_stack should still be empty.")

        klondike.adjust_score(-19)
        self.assertEqual(klondike.score, 18, "The score should now be 18")
        self.assertEqual(len(klondike.undo_stack), 0, "Undo_stack should still be empty.")

    def test_tableau_move(self):
        pass  # TODO: implement

    def test_tableau_to_foundation(self):
        pass  # TODO: implement

    def test_waste_to_tableau(self):
        pass  # TODO: implement

    def test_waste_to_foundation(self):
        pass  # TODO: implement

    def test_foundation_to_tableau(self):
        pass  # TODO: implement

    def test_undo(self):
        pass  # TODO: implement
