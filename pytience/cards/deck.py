# -*- coding: utf-8 -*-
import random
from itertools import product
from collections import deque
from dataclasses import dataclass
from enum import Enum
from typing import Iterable, NoReturn
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
        if self.pip is None:
            return '*'
        else:
            return '{}{}{}'.format('|' if self.is_concealed else '', self.pip.value, self.suit.value)

    def __str__(self):
        if self.is_concealed:
            return '#'
        return repr(self)

    @classmethod
    def parse_card(cls, card_string) -> 'Card':
        """
        Converts a card string, e.g. "10♣" to a Card(Pip.Ten, Suit.Cubs)
        :param card_string: The string representing the card
        :return: new Card object
        """
        suit = Suit(card_string[-1])
        if card_string[0] == '|':
            pip = Pip(card_string[1:-1])
            return Card(pip, suit)
        else:
            pip = Pip(card_string[:-1])
            return Card(pip, suit).reveal()


class Deck:
    def __init__(self, num_decks: int = 1, num_jokers_per_deck: int = 0):
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

    def deal_all(self) -> Card:
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

    def __len__(self):
        return self.remaining
