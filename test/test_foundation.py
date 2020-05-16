from unittest import TestCase
from itertools import product
from pytience.games.solitaire.foundation import Foundation
from pytience.games.solitaire.exception import NoSuchSuitException, ConcealedCardNotAllowedException, \
    IllegalFoundationBuildOrderException
from pytience.cards.exception import NoCardsRemainingException
from pytience.cards.deck import Suit, Pip, Card


class FoundationTestCase(TestCase):
    def test_create(self):
        foundation = Foundation(Suit)

        self.assertSetEqual(set(foundation.piles.keys()), set(suit for suit in Suit),
                            'The Foundation should have one pile per suit.')
        for pile in foundation.piles.values():
            self.assertEqual(len(pile), 0, 'New foundation piles should be empty')

    def test_put(self):
        foundation = Foundation(Suit)
        ace_hearts = Card(Pip.Ace, Suit.Hearts)
        two_hearts = Card(Pip.Two, Suit.Hearts)
        three_hearts = Card(Pip.Three, Suit.Hearts)

        with self.assertRaises(ConcealedCardNotAllowedException,
                               msg='Only revealed cards may be placed in the foundation.'):
            foundation.put(two_hearts)

        two_hearts.reveal()
        with self.assertRaises(IllegalFoundationBuildOrderException,
                               msg='Empty foundation piles should only accept Aces.'):
            foundation.put(two_hearts)

        ace_hearts.reveal()
        foundation.put(ace_hearts)
        self.assertEqual(len(foundation.piles[Suit.Hearts]), 1, "Foundation Hearts pile should have exactly 1 card.")
        self.assertEqual(foundation.piles[Suit.Hearts][-1], ace_hearts,
                         "The top foundation Hearts card should be the recently placed ace.")

        three_hearts.reveal()
        with self.assertRaises(IllegalFoundationBuildOrderException,
                               msg='Foundation piles should be built sequentially by suit.'):
            foundation.put(three_hearts)

        foundation.put(two_hearts)
        self.assertEqual(len(foundation.piles[Suit.Hearts]), 2, "Foundation Hearts pile should have exactly 2 cards.")

        foundation.put(three_hearts)
        self.assertEqual(len(foundation.piles[Suit.Hearts]), 3, "Foundation Hearts pile should have exactly 3 cards.")

    def test_get(self):
        foundation = Foundation(Suit)
        for suit in Suit:
            with self.assertRaises(NoCardsRemainingException,
                                   msg="It should be illegal to get from an empty foundation"):
                foundation.get(suit)
        with self.assertRaises(NoSuchSuitException,
                               msg="It should be illegal to get a non-existent suit from the foundation"):
            foundation.get("foo")

        ace_hearts, two_hearts, three_hearts = (Card(pip, Suit.Hearts).reveal() for pip in
                                                [Pip.Ace, Pip.Two, Pip.Three])

        foundation.piles[Suit.Hearts].extend([ace_hearts, two_hearts, three_hearts])
        for suit in Suit.Spades, Suit.Diamonds, Suit.Clubs:
            with self.assertRaises(NoCardsRemainingException,
                                   msg="There should be no cards in the other foundation piles."):
                foundation.get(suit)
        card = foundation.get(Suit.Hearts)
        self.assertEqual(card, three_hearts, "The top card should have been a three.")

        card = foundation.get(Suit.Hearts)
        self.assertEqual(card, two_hearts, "The top card should have been a two.")

        card = foundation.get(Suit.Hearts)
        self.assertEqual(card, ace_hearts, "The top card should have been an ace.")

        with self.assertRaises(NoCardsRemainingException,
                               msg="The foundation heart pile should be empty by now."):
            foundation.get(Suit.Hearts)

    def test_is_full(self):
        foundation = Foundation(Suit)
        self.assertFalse(foundation.is_full, "Foundation should not be considered full without cards.")

        for pip, suit in product(Pip, Suit):
            self.assertFalse(foundation.is_full,
                             "Foundation should not be considered full with fewer than 13 cards per pile.")
            foundation.piles[suit].append(Card(pip, suit))

        self.assertTrue(foundation.is_full, "Foundation should be considered full with 13 cards in each pile.")

    def test_undo_put(self):
        pass  # TODO: implement

    def test_undo_get(self):
        pass  # TODO: implement
