from unittest import TestCase

from pytience.games.solitaire.klondike import KlondikeGame


class KlondikeGameTestCase(TestCase):
    def test_create(self):
        klondike = KlondikeGame()
        self.assertTrue(klondike.stock.is_shuffled, "The klondike deck should be shuffled.")
        self.assertEqual(len(klondike.stock), 24, "Klondike starting stock should have 24 cards remaining.")
        self.assertEqual(len(klondike.waste), 0, "Klondike starting waste should be empty.")
        self.assertEqual(klondike.score, 0, "Klondike starting score should be 0.")
        self.assertEqual(len(klondike.foundation.piles), 4, "Klondike foundation should have 4 piles.")

    def test_deal(self):
        pass  # TODO: implement

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
