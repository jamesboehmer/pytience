from pytience.games.exception import IllegalMoveException


class IllegalTableauMoveException(IllegalMoveException):
    pass


class IllegalFoundationMoveException(IllegalMoveException):
    pass


class ConcealedCardNotAllowedException(IllegalMoveException):
    pass


class NoSuchSuitException(IllegalFoundationMoveException):
    pass


class IllegalFoundationBuildOrderException(IllegalFoundationMoveException):
    pass


class IllegalTableauBuildOrderException(IllegalTableauMoveException):
    pass


class TableauPileIndexError(IllegalTableauMoveException):
    pass


class TableauCardIndexError(IllegalTableauMoveException):
    pass


class TableauCardNotAvailableException(IllegalTableauMoveException):
    pass
