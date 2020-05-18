from unittest import TestCase
from unittest.mock import patch

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
        # TODO: check for score adjustments
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

    def test_select_tableau_no_pile_num(self):
        # 1 No pile_num, no foundation candidate in the tableau - should raise exception

        klondike = KlondikeGame()
        for pile_num, card in enumerate(["10♦", "9♠", "J♦", "6♣", "3♦", "9♥", "2♦"]):
            klondike.tableau.piles[pile_num][-1] = Card.parse_card(card)

        with self.assertRaises(IllegalMoveException,
                               msg="Should raise exception when there are no args and no foundation candidates."):
            klondike.select_tableau()

        # 2 No pile_num, foundation candidate exists in the tableau.
        klondike.tableau.piles[3][-1] = Card.parse_card("A♣")

        with patch('pytience.games.solitaire.klondike.KlondikeGame.seek_tableau_to_foundation') as mock_method:
            klondike.select_tableau()
            mock_method.assert_called_once()

    def test_select_tableau_invalid_piles(self):
        klondike = KlondikeGame()
        # pile_num == destination_pile_num - should raise exception
        with self.assertRaises(IllegalMoveException, msg="Should raise exception if pile_num==destination_pile_num."):
            klondike.select_tableau(pile_num=0, destination_pile_num=0)

        with self.assertRaises(IllegalMoveException, msg="Should raise exception if pile_num==destination_pile_num."):
            klondike.select_tableau(pile_num=0, card_num=-100, destination_pile_num=0)

        # invalid pile_num - raise exception
        with self.assertRaises(IllegalMoveException, msg="Should raise exception if pile_num doesn't exist."):
            klondike.select_tableau(pile_num=-1)

        # valid pile_num, invalid card_num
        with self.assertRaises(IllegalMoveException,
                               msg="Should raise exception if card_num isn't passed with pile_num."):
            klondike.select_tableau(pile_num=0)

        klondike.tableau.piles[0].pop()
        with self.assertRaises(IllegalMoveException, msg="Should raise exception if card_num is invalid."):
            klondike.select_tableau(pile_num=0, card_num=0)

        # valid pile_num, valid single card_num, invalid destination
        klondike.tableau.piles[0].append(Card.parse_card("10♦"))
        klondike.tableau.piles[1][-1] = Card.parse_card("9♠")
        with self.assertRaises(IllegalMoveException, msg="Should raise exception if destination is invalid."):
            klondike.select_tableau(pile_num=0, card_num=0, destination_pile_num=1)

    def test_select_tableau_no_destination(self):
        klondike = KlondikeGame()
        # valid pile_num, valid single card_num, no destination, no foundation fit, no tableau fit - exception

        for pile_num, card in enumerate(["10♦", "9♠", "J♦", "6♣", "3♦", "9♥", "2♦"]):
            klondike.tableau.piles[pile_num][-1] = Card.parse_card(card)

        with self.assertRaises(IllegalMoveException,
                               msg="Should raise exception when there's no destination specified and no fit."):
            klondike.select_tableau(3, -1)

        # valid pile_num, valid single card_num, no destination, foundation fit
        klondike.foundation.piles[Suit.Clubs].append(Card.parse_card("5♣"))
        self.assertEqual(len(klondike.foundation.piles[Suit.Clubs]), 1,
                         "There should be exactly 1 card in the club foundation pile.")
        self.assertEqual(len(klondike.tableau.piles[3]), 4, "There should now be exactly 4 cards in pile 3.")
        klondike.select_tableau(3, -1)
        self.assertEqual(len(klondike.foundation.piles[Suit.Clubs]), 2,
                         "There should be exactly 2 cards in the club foundation pile.")
        self.assertEqual(len(klondike.tableau.piles[3]), 3, "There should now be exactly 3 cards left in pile 3.")

        # valid pile_num, valid single card_num, no destination, no foundation fit, tableau fit
        klondike = KlondikeGame()
        for pile_num, card in enumerate(["10♦", "9♠", "J♦", "6♣", "3♦", "9♥", "2♦"]):
            klondike.tableau.piles[pile_num][-1] = Card.parse_card(card)
        self.assertEqual(sum(len(p) for p in klondike.foundation.piles.values()), 0,
                         "There should be no cards in the foundation.")
        self.assertEqual(len(klondike.tableau.piles[1]), 2, "There should be exactly 2 cards in pile 1.")
        self.assertEqual(len(klondike.tableau.piles[0]), 1, "There should be exactly 1 card in pile 0.")
        klondike.select_tableau(1, 1)
        self.assertEqual(sum(len(p) for p in klondike.foundation.piles.values()), 0,
                         "There should still be exactly 0 cards in the foundation.")
        self.assertEqual(len(klondike.tableau.piles[1]), 1, "There should now be exactly 1 card left in pile 1.")
        self.assertEqual(len(klondike.tableau.piles[0]), 2, "There should now be exactly 2 cards in pile 0.")

        # valid pile_num, valid multi card_num, no destination, tableau fit
        klondike = KlondikeGame()
        for pile_num, card in enumerate(["10♦", "8♥", "J♦", "6♣", "3♦", "9♥", "2♦"]):
            klondike.tableau.piles[pile_num][-1] = Card.parse_card(card)
        klondike.tableau.piles[1][0] = Card.parse_card("9♠")

        self.assertEqual(len(klondike.tableau.piles[1]), 2, "There should be exactly 2 cards in pile 1.")
        self.assertEqual(len(klondike.tableau.piles[0]), 1, "There should be exactly 1 card in pile 0.")
        klondike.select_tableau(1, 0)
        self.assertEqual(len(klondike.tableau.piles[1]), 0, "There should now be exactly 0 cards left in pile 1.")
        self.assertEqual(len(klondike.tableau.piles[0]), 3, "There should now be exactly 3 cards in pile 0.")

    def test_select_Tableau_valid_destination(self):

        # valid pile_num, valid single card_num, valid destination, no tableau fit - exception

        # valid pile_num, valid single card_num, valid destination, tableau fit
        pass  # TODO: implement

    def test_waste_to_tableau(self):
        pass  # TODO: implement

    def test_waste_to_foundation(self):
        pass  # TODO: implement

    def test_foundation_to_tableau(self):
        pass  # TODO: implement

    def test_undo(self):
        pass  # TODO: implement
