class GameEnd(Exception):
    pass


class Tie(GameEnd):
    pass


class Checkmated(GameEnd):
    pass


class RunOutOfTime(GameEnd):
    pass


class MoveError(Exception):
    pass


class CheckAfterMove(MoveError):
    pass


class SquareNotInValidMoves(MoveError):
    pass


class TeamDoesntGotTurn(MoveError):
    pass


class CantCastling(MoveError):
    pass


class DidntMove(Exception):
    pass


class UserExitGame(Exception):
    pass
