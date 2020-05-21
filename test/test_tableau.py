from collections import deque
from itertools import product
from unittest import TestCase

from pytience.cards.deck import Suit, Pip, Card, Deck
from pytience.games.solitaire.exception import IllegalTableauBuildOrderException, TableauCardIndexError, \
    ConcealedCardNotAllowedException, TableauPileIndexError, TableauCardNotAvailableException
from pytience.games.solitaire.tableau import Tableau


class TableauTestCase(TestCase):
    def test_create_empty(self):
        tableau = Tableau()
        self.assertEqual(len(tableau), 7, "Default tableau should have 7 piles.")

        self.assertTrue(all(len(pile) == 0 for pile in tableau.piles), "All new tableau piles should be empty.")

        tableau = Tableau(0)
        self.assertEqual(len(tableau), 1, "Minimum tableau size should be 1.")

        for size in range(1, 8):
            tableau = Tableau(size)
            self.assertEqual(len(tableau), size, "Tableau size should match the constructor argument.")

    def test_create_with_deck(self):
        deck = Deck().shuffle()
        tableau = Tableau(7, deck)
        for pile in tableau.piles:
            self.assertTrue(all(c.is_concealed for c in pile[:len(pile) - 1]),
                            "Only the top card in tableau piles should be revealed.")
            self.assertTrue(pile[-1].is_revealed)
        num_tableau_cards = sum(len(pile) for pile in tableau.piles)
        self.assertEqual(deck.remaining + num_tableau_cards, 52,
                         "There should be 52 cards between the deck and the tableau.")

    def test_put_concealed_on_empty_tableau(self):
        tableau = Tableau()
        for card in Deck().deal_all():
            with self.assertRaises(ConcealedCardNotAllowedException,
                                   msg="Concealed cards should not be allowed to be put in the tableau."):
                tableau.put([card], 0)

    def test_put_concealed_card_on_built_tableau(self):
        tableau = Tableau()
        for pile_num, suit in enumerate(Suit):
            tableau.put([Card(Pip.King, suit).reveal()], pile_num)
        for pile_num in range(len(Suit)):
            with self.assertRaises(ConcealedCardNotAllowedException,
                                   msg="Building a concealed card on a revealed card should raise an exception."):
                tableau.put([Card(None, None)], pile_num)

    def test_put_non_kings_on_empty_tableau(self):
        tableau = Tableau()
        for pip, suit, pile_num in product(filter(lambda p: p != Pip.King, Pip), Suit, range(len(tableau))):
            with self.assertRaises(IllegalTableauBuildOrderException,
                                   msg="Empty tableau piles should disallow non-kings "):
                tableau.put([Card(pip, suit).reveal()], pile_num)

        self.assertTrue(all(len(pile) == 0 for pile in tableau.piles))

    def test_put_build_order(self):
        tableau = Tableau()
        suits = deque([Suit.Spades, Suit.Diamonds, Suit.Clubs, Suit.Hearts])  # R/B/R/B
        for pile_num, suit in enumerate(suits):
            tableau.put([Card(Pip.King, suit).reveal()], pile_num)
        self.assertTrue(all(len(p) == 1 for p in tableau.piles[:len(suits)]),
                        "The first 4 tableau piles should have exactly 1 king card.")
        self.assertTrue(all(len(p) == 0 for p in tableau.piles[len(suits):]),
                        "The remaining tableau piles should have exactly 0 cards.")

        # Test invalid color with valid value
        for pile_num, suit in enumerate(suits):
            with self.assertRaises(IllegalTableauBuildOrderException,
                                   msg="Tableau builds should be rejected when colors aren't alternated."):
                tableau.put([Card(Pip.Queen, suit).reveal()], pile_num)

        # Test valid color with valid value
        suits.rotate(1)  # B/R/B/R
        for pile_num, suit in enumerate(suits):
            tableau.put([Card(Pip.Queen, suit).reveal()], pile_num)
        self.assertTrue(all(len(p) == 2 for p in tableau.piles[:len(suits)]),
                        "The first 4 tableau piles should have exactly 1 king card.")
        self.assertTrue(all(len(p) == 0 for p in tableau.piles[len(suits):]),
                        "The remaining tableau piles should have exactly 0 cards.")

        # Test valid color with invalid value
        suits.rotate(1)  # R/B/R/B
        for pile_num, suit in enumerate(suits):
            with self.assertRaises(IllegalTableauBuildOrderException,
                                   msg="Tableau builds should be rejected when values aren't descending."):
                tableau.put([Card(Pip.Ten, suit).reveal()], pile_num)
        self.assertTrue(all(len(p) == 2 for p in tableau.piles[:len(suits)]),
                        "The first 4 tableau piles should have exactly 1 king card.")
        self.assertTrue(all(len(p) == 0 for p in tableau.piles[len(suits):]),
                        "The remaining tableau piles should have exactly 0 cards.")

    def test_get_empty_pile(self):
        tableau = Tableau()
        for pile_num, card_num in product(range(len(tableau)), range(len(Pip))):
            with self.assertRaises(TableauCardIndexError,
                                   msg="Tableau get should raise an exception if the pile is empty."):
                tableau.get(pile_num, card_num)

    def test_get_invalid_pile_num(self):
        tableau = Tableau()

        with self.assertRaises(TableauPileIndexError,
                               msg="""Tableau get should raise an exception 
                               if the pile index is greater than the number of piles."""):
            tableau.get(7, 0)

    def test_get_invalid_card_num(self):
        tableau = Tableau()
        for pile_num, suit in enumerate(Suit):
            tableau.put([Card(Pip.King, suit).reveal()], pile_num)
        for pile_num in range(len(Suit)):
            with self.assertRaises(TableauCardIndexError,
                                   msg="""Tableau get should raise an exception 
                                   if the card index is greater than the length of the pile."""):
                tableau.get(pile_num, 1)

    def test_get_concealed_card(self):
        tableau = Tableau(7, Deck().shuffle())
        with self.assertRaises(TableauCardNotAvailableException,
                               msg="Getting a concealed card from the tableau should raise an exception."):
            tableau.get(6, 0)

    def test_get_valid_slice_with_reveal(self):
        tableau = Tableau(7, Deck().shuffle())
        self.assertEqual(len(tableau.piles[6]), 7, "Tableau pile[6] should have 7 cards.")
        self.assertTrue(tableau.piles[6][5].is_concealed, "Tableau pile[6][5] should be concealed.")
        tableau.get(6, -1)
        self.assertEqual(len(tableau.piles[6]), 6, "Tableau pile[6] should have 6 cards.")
        self.assertTrue(tableau.piles[6][5].is_revealed, "Tableau pile[6][5] should be concealed.")

    def test_get_valid_slice_without_reveal(self):
        tableau = Tableau(7, Deck().shuffle())
        tableau.piles[6][5] = Card(Pip.King, Suit.Hearts).reveal()
        tableau.piles[6][6] = Card(Pip.Queen, Suit.Clubs).reveal()
        self.assertEqual(len(tableau.piles[6]), 7, "Tableau pile[6] should have 7 cards.")
        self.assertTrue(tableau.piles[6][5].is_revealed, "Tableau pile[6][5] should be revealed.")
        tableau.get(6, -1)
        self.assertEqual(len(tableau.piles[6]), 6, "Tableau pile[6] should have 6 cards.")
        self.assertTrue(tableau.piles[6][5].is_revealed, "Tableau pile[6][5] should still be revealed.")

    def test_reveal(self):
        tableau = Tableau(7, Deck().shuffle())
        tableau.piles[6].pop()
        self.assertTrue(tableau.piles[6][-1].is_concealed, "Tableau pile[6][-1] should be concealed.")
        result = tableau._reveal(6)
        self.assertTrue(result, "Reveal action should have returned True for a concealed card.")
        self.assertTrue(tableau.piles[6][-1].is_revealed, "Tableau pile[6][-1] should be revealed.")
        result = tableau._reveal(6)
        self.assertFalse(result, "Reveal action should have returned False for a revealed card.")

    def test_conceal(self):
        tableau = Tableau(7, Deck().shuffle())
        self.assertTrue(tableau.piles[6][-1].is_revealed, "Tableau pile[6][-1] should be revealed.")
        result = tableau._conceal(6)
        self.assertTrue(result, "Conceal action should have returned True for a revealed card.")
        self.assertTrue(tableau.piles[6][-1].is_concealed, "Tableau pile[6][-1] should be concealed.")
        result = tableau._conceal(6)
        self.assertFalse(result, "Conceal action should have returned False for a concealed card.")

    def test_dump(self):
        tableau = Tableau()
        piles = [
            ["K♣", "Q♥", "J♣", "10♥", "9♣"],
            ["K♦"],
            ["|A♣", "|2♣", "10♦"],
            [],
            ["|4♣", "|6♥", "|8♦", "10♣", "9♦", "8♠", "7♦", "6♠"],
            ["|3♣", "K♠", "Q♦"],
            ["|9♥", "|5♦", "|3♠", "|7♣", "|8♣", "|K♥", "7♠", "6♦", "5♠", "4♥"]
        ]
        tableau.piles = list(map(lambda p: list(map(Card.parse_card, p)), piles))
        tableau.put(tableau.get(0, 2), 5)
        self.assertEqual(len(tableau.undo_stack), 2, "There should be exactly 2 undo actions in the tableau.")
        undo_stack = list(map(lambda u: {'action': u.function.__name__, 'args': u.args}, tableau.undo_stack))

        dump = tableau.dump()
        self.assertEqual(len(dump["piles"]), len(tableau.piles))
        for pile_num, tableau_pile in enumerate(tableau.piles):
            self.assertListEqual(list(map(str, tableau_pile)), dump["piles"][pile_num])
        self.assertListEqual(dump["undo_stack"], undo_stack)

    def test_load(self):
        dump = {"piles": [["K♣", "Q♥"], ["K♦"], ["|A♣", "|2♣", "10♦"], [],
                          ["|4♣", "|6♥", "|8♦", "10♣", "9♦", "8♠", "7♦", "6♠"], ["|3♣", "K♠", "Q♦", "J♣", "10♥", "9♣"],
                          ["|9♥", "|5♦", "|3♠", "|7♣", "|8♣", "|K♥", "7♠", "6♦", "5♠", "4♥"]],
                "undo_stack": [{"action": "undo_get", "args": [0, ["J♣", "10♥", "9♣"], False]},
                               {"action": "undo_put", "args": [5, 3]}]}
        tableau = Tableau(tableau_dump=dump)
        undo_stack = list(map(lambda u: {'action': u.function.__name__, 'args': u.args}, tableau.undo_stack))
        self.assertEqual(len(tableau.piles), len(dump["piles"]))
        for pile_num, tableau_pile in enumerate(tableau.piles):
            self.assertListEqual(list(map(str, tableau_pile)), dump["piles"][pile_num])
        self.assertListEqual(dump["undo_stack"], undo_stack)

    def test_undo_put(self):
        pass  # TODO: implement

    def test_undo_get_with_reveal(self):
        pass  # TODO: implement

    def test_undo_get_without_reveal(self):
        pass  # TODO: implement
