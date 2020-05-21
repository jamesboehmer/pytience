from collections import Counter
from itertools import product
from unittest import TestCase

from pytience.cards.deck import Deck, Pip, Suit, Color, Card
from pytience.cards.exception import NoCardsRemainingException


class DeckTestCase(TestCase):
    def test_shuffle(self):
        deck = Deck()
        self.assertFalse(deck.is_shuffled, "Deck should not be shuffled before shuffling")
        ordered_cards = deck.cards.copy()
        deck.shuffle()
        self.assertTrue(deck.is_shuffled, "Deck should be shuffled after shuffling")
        shuffled_cards = deck.cards.copy()
        self.assertNotEqual(ordered_cards, shuffled_cards,
                            "Shuffled cards shouldn't resemble ordered cards after shuffling")
        shuffled_deck = Deck().shuffle()
        self.assertIsInstance(shuffled_deck, Deck, "Deck.shuffle should return itself.")

    def test_reveal(self):
        for card in Deck(num_jokers_per_deck=1).cards:
            self.assertFalse(card.is_revealed)
            self.assertTrue(card.is_concealed)
            concealed = card.conceal()  # Test for idempotency and continuation
            self.assertFalse(card.is_revealed)
            self.assertTrue(card.is_concealed)
            self.assertIsNotNone(concealed, "Card conceal should return itself.")
            # self.assertEqual(len(str(card)), 1, "Concealed card string should always be 1 char.")
            card.reveal()
            self.assertTrue(card.is_revealed)
            self.assertFalse(card.is_concealed)
            if card.pip is None:
                self.assertEqual(len(str(card)), 1, "Revealed Joker card string should always be 1 char.")
            else:
                self.assertGreaterEqual(len(str(card)), 2, "Revealed card strings should always be 2 or mar chars.")
            revealed = card.reveal()  # Test for idempotency and continuation
            self.assertIsNotNone(revealed, "Card reveal should return itself.")
            self.assertTrue(card.is_revealed)
            self.assertFalse(card.is_concealed)
            card.conceal()
            self.assertFalse(card.is_revealed)
            self.assertTrue(card.is_concealed)

    def test_card_counts(self):
        deck = Deck()
        self.assertEqual(len(deck.cards), 52, "There should be exactly 52 cards in a standard deck.")
        self.assertEqual(len(deck), 52, "The length of the deck should equal the length of the deck's card list.")
        self.assertEqual(deck.remaining, 52, "The deck's remaining count should equal the length the deck's card list.")
        c = Counter(card.suit for card in deck.cards)

        self.assertEqual(len(c), 4, "There should be exactly 4 suits in the deck.")
        for suit, count in c.items():
            self.assertEqual(count, 13, "There should be exactly 13 cards per suit ({}).".format(str(suit)))

        deck = Deck(num_decks=2)
        self.assertEqual(len(deck), 104, "There should be exactly 104 cards in a double standard deck.")

        deck = Deck(num_jokers_per_deck=2)
        self.assertEqual(len(deck), 54, "There should be exactly 54 cards in a standard deck with 2 jokers.")

        deck = Deck(num_decks=2, num_jokers_per_deck=2)
        self.assertEqual(len(deck), 108, "There should be exactly 108 cards in a double standard deck with 2 jokers.")

    def test_deal(self):
        deck = Deck()
        first_card = deck.cards[0]
        second_card = deck.cards[1]
        last_card = deck.cards[51]

        dealt_card = deck.deal()

        self.assertEqual(len(deck), 51, "There should be exactly 51 cards remaining after 1 has been dealt.")
        self.assertEqual(dealt_card, first_card, "The dealt card should be the first card in the deck.")
        self.assertEqual(second_card, deck.cards[0], "The second card should now be first in the deck after a deal.")
        self.assertEqual(last_card, deck.cards[50], "The last card in the deck should still be the last card.")

        deck.undeal(dealt_card)
        self.assertEqual(len(deck), 52, "There should be exactly 52 cards remaining after 1 deal/undeal.")
        self.assertEqual(dealt_card, deck.cards[0], "The undealt card should be the first card in the deck.")
        self.assertEqual(second_card, deck.cards[1], "The second card should be back in second place.")
        self.assertEqual(last_card, deck.cards[51], "The last card should be back in last place.")

        for _ in range(52):
            self.assertIsNotNone(deck.deal(), "The first 52 deals should always return a card.")

        with self.assertRaises(NoCardsRemainingException, msg="The 53rd deal should return None."):
            deck.deal()

    def test_deal_all(self):
        deck = Deck()
        original_cards = deck.cards.copy()
        self.assertEqual(len(original_cards), 52, "There should be exactly 52 cards remaining in a new deck.")
        dealt_cards = [card for card in deck.deal_all()]
        self.assertEqual(len(deck), 0, "The deck should be empty after deal_all.")
        self.assertSequenceEqual(original_cards, dealt_cards, "Dealt cards should match the original cards.")

    def test_replenish(self):
        deck = Deck()
        self.assertEqual(len(deck), 52, "Deck should have 52 remaining cards before dealing any.")
        first_five_cards = [deck.cards[n] for n in range(5)]
        next_five_cards = [deck.cards[n] for n in range(5, 10)]
        last_five_cards = [deck.cards[n] for n in range(47, 52)]

        dealt_cards = [deck.deal() for _ in range(5)]
        self.assertEqual(first_five_cards, dealt_cards, "Dealt cards should come from the top of the deck in order.")
        self.assertEqual(len(deck), 47, "Deck should have 47 remaining cards after dealing 5.")

        new_last_five_cards = [deck.cards[n] for n in range(42, 47)]
        self.assertEqual(last_five_cards, new_last_five_cards, "The last 5 cards in the deck should remain the same.")

        deck.replenish(dealt_cards)
        self.assertEqual(len(deck), 52, "Deck should have 52 remaining cards after replenishment.")

        new_first_five_cards = [deck.cards[n] for n in range(5)]
        self.assertEqual(next_five_cards, new_first_five_cards, "The 6-10th cards should now be 1-5.")

        replenished_last_five_cards = [deck.cards[n] for n in range(47, 52)]
        self.assertEqual(replenished_last_five_cards, dealt_cards, "The original first 5 cards should now be the last.")

    def test_card_faces(self):
        deck = Deck(num_jokers_per_deck=2)
        for card in deck.cards:
            self.assertEqual(card.is_face, card.pip in (Pip.Jack, Pip.Queen, Pip.King), "Face cards must be J, Q, or K")

    def test_card_colors(self):
        deck = Deck()
        for card in deck.cards:
            if card.suit in (Suit.Spades, Suit.Clubs):
                self.assertEqual(card.color, Color.Black)
            elif card.suit in (Suit.Hearts, Suit.Diamonds):
                self.assertEqual(card.color, Color.Red)

    def test_color(self):
        self.assertEqual(str(Color.Black), 'Black')
        self.assertEqual(str(Color.Red), 'Red')

    def test_pip(self):
        self.assertEqual(str(Pip.Ace), 'A')
        self.assertEqual(str(Pip.Two), '2')
        self.assertEqual(str(Pip.Three), '3')
        self.assertEqual(str(Pip.Four), '4')
        self.assertEqual(str(Pip.Five), '5')
        self.assertEqual(str(Pip.Six), '6')
        self.assertEqual(str(Pip.Seven), '7')
        self.assertEqual(str(Pip.Eight), '8')
        self.assertEqual(str(Pip.Nine), '9')
        self.assertEqual(str(Pip.Ten), '10')
        self.assertEqual(str(Pip.Jack), 'J')
        self.assertEqual(str(Pip.Queen), 'Q')
        self.assertEqual(str(Pip.King), 'K')

    def test_parse_card(self):
        for (suit, pip, revealed) in product(Suit, Pip, [True, False]):
            card_string = '{}{}{}'.format('|' if not revealed else '', pip.value, suit.value)
            card = Card.parse_card(card_string)
            self.assertEqual(card.pip, pip, "The parsed card should have the correct pip.")
            self.assertEqual(card.suit, suit, "The parsed card should have the correct suit.")
            self.assertEqual(card.is_revealed, revealed, "The parsed card should have the correct reveal state.")
        for revealed in (True, False):
            card = Card.parse_card('{}*'.format('|' if not revealed else ''))
            self.assertIsNone(card.pip, "Joker should have no pip")
            self.assertIsNone(card.suit, "Joker should have no suit")
            self.assertEqual(card.is_revealed, revealed, "The parsed card should have the correct reveal state.")

    def test_dump(self):
        deck = Deck().shuffle()
        cards = list(map(str, deck.cards))
        dump = deck.dump()
        self.assertListEqual(cards, dump["cards"])
        self.assertEqual(deck.num_decks, dump["num_decks"])
        self.assertEqual(deck.num_jokers, dump["num_jokers"])
        self.assertEqual(deck.is_shuffled, dump["is_shuffled"])

    def test_load(self):
        # TODO move this to an external fixture
        dump = {"num_decks": 1, "num_jokers": 0, "is_shuffled": True,
                "cards": ["|10♠", "|4♦", "|4♠", "|J♥", "|2♥", "|7♥", "|5♥", "|A♠", "|5♣", "|Q♠", "|J♠", "|Q♣", "|9♠"]}
        deck = Deck(deck_dump=dump)
        self.assertListEqual(list(map(str, deck.cards)), dump["cards"])
        self.assertEqual(deck.num_decks, dump["num_decks"])
        self.assertEqual(deck.num_jokers, dump["num_jokers"])
        self.assertEqual(deck.is_shuffled, dump["is_shuffled"])

