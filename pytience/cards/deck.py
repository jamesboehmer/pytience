# -*- coding: utf-8 -*-
import random
from collections import deque
from dataclasses import dataclass
from enum import Enum
from itertools import product
from typing import Iterable

from pytience.cards.exception import NoCardsRemainingException


class Color(Enum):
    Black = 1
    Red = 2

    def __str__(self):
        return str(self.name)


class Suit(Enum):
    Spades = '♠'
    Diamonds = '♦'
    Clubs = '♣'
    Hearts = '♥'

    @property
    def color(self):
        if self in [Suit.Clubs, Suit.Spades]:
            return Color.Black
        return Color.Red

    def __str__(self):
        return str(self.value)


class Pip(Enum):
    Ace = 'A'
    Two = '2'
    Three = '3'
    Four = '4'
    Five = '5'
    Six = '6'
    Seven = '7'
    Eight = '8'
    Nine = '9'
    Ten = '10'
    Jack = 'J'
    Queen = 'Q'
    King = 'K'

    def __str__(self):
        return str(self.value)


@dataclass
class Card:
    pip: Pip
    suit: Suit
    is_revealed: bool = False

    @property
    def is_concealed(self):
        return not self.is_revealed

    @property
    def is_face(self):
        return self.pip in [Pip.Jack, Pip.Queen, Pip.King]

    @property
    def color(self):
        return self.suit.color

    def reveal(self):
        self.is_revealed = True
        return self

    def conceal(self):
        self.is_revealed = False
        return self

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        state = '|' if self.is_concealed else ''
        if self.pip is None:
            return '{}*'.format(state)
        else:
            return '{}{}{}'.format(state, self.pip.value, self.suit.value)

    @classmethod
    def parse_card(cls, card_string) -> 'Card':
        """
        Converts a card string, e.g. "10♣" to a Card(Pip.Ten, Suit.Clubs)
        :param card_string: The string representing the card
        :return: new Card object
        """

        is_revealed = True
        if card_string[0] == '|':
            is_revealed = False
            card_string = card_string[1:]

        if card_string == '*':
            pip, suit = None, None
        else:
            pip = Pip(card_string[:-1]) or None
            suit = Suit(card_string[-1]) or None

        return Card(pip, suit, is_revealed)


class Deck:
    def __init__(self, num_decks: int = 1, num_jokers_per_deck: int = 0, deck_dump: object = None):
        if deck_dump:
            self.load(deck_dump)
        else:
            self.num_decks = num_decks
            self.num_jokers = num_jokers_per_deck
            self.cards = deque(
                [Card(pip, suit) for suit, pip in product(Suit, Pip)] * num_decks +
                [Card(None, None)] * num_jokers_per_deck * num_decks
            )
            self.is_shuffled = False

    def shuffle(self):
        """Ensure the deck is shuffled"""
        random.shuffle(self.cards)
        self.is_shuffled = True
        return self

    @property
    def remaining(self) -> int:
        """Number of cards remaining in the deck"""
        return len(self.cards)

    def deal(self) -> Card:
        """Deal a single concealed card from the top of the deck"""
        if not self.cards:
            raise NoCardsRemainingException("No cards remaining in the deck.")
        return self.cards.popleft()

    def deal_all(self) -> Iterable[Card]:
        """Deal all the cards"""
        while len(self.cards) > 0:
            yield self.cards.popleft()

    def undeal(self, card: Card) -> object:
        """Add a single card to the top of the deck"""
        self.cards.appendleft(card)
        return self

    def replenish(self, cards: Iterable[Card]) -> object:
        """Add a list of cards to the bottom of the deck"""
        self.cards.extend(cards)
        return self

    def dump(self):
        return {
            "num_decks": self.num_decks,
            "num_jokers": self.num_jokers,
            "is_shuffled": self.is_shuffled,
            "cards": list(map(str, self.cards))
        }

    def load(self, deck_dump: object):
        self.num_decks = deck_dump["num_decks"]
        self.num_jokers = deck_dump["num_jokers"]
        self.is_shuffled = deck_dump["is_shuffled"]
        self.cards = deque([Card.parse_card(card_string) for card_string in deck_dump["cards"]])

    def __len__(self):
        return self.remaining
