from unittest import TestCase

from pytience.games.solitaire.klondike import KlondikeGame
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
