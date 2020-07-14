import pygame
import screen
import pieces
from teams import Team


class SaveMove:
    def __init__(self, piece: pieces.Piece, move_square: screen.Square):
        self.piece = piece
        self.move_square = move_square
        self.eaten_piece = None
        self.current_piece_square = None

    def __enter__(self):
        self.eaten_piece = self.move_square.current_piece
        self.current_piece_square = self.piece.square

    def __exit__(self, exception_type, exc_value, exc_tb):
        # Move pieces moved to there last position.
        if exception_type is DidntMove:
            return

        self.return_piece_to_pawn_if_needed()
        self.piece.move(self.current_piece_square)

        if self.eaten_piece is not None:
            self.eaten_piece.move(self.eaten_piece.square)
            self.eaten_piece.is_eaten = False

    def return_piece_to_pawn_if_needed(self):
        # TODO Check if work.
        if not isinstance(self.piece, pieces.Pawn):
            return
        if not (self.move_square.line_cord == 7 or self.move_square.line_cord == 0):
            return

        pawn = self.piece
        print(pawn)
        print(self.move_square)
        new_piece = self.piece.square.current_piece
        if new_piece is pawn:
            return
        pawn.team.pieces.remove(new_piece)
        pawn.team.pieces.append(pawn)


class GameEnd(Exception):
    pass


class Tie(GameEnd):
    pass


class Checkmated(GameEnd):
    pass


class DidntMove(Exception):
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


def add_pawns(white_team, black_team):
    for tur in range(screen.BOARD_LINE):
        white_team.pieces.append(pieces.Pawn(white_team, tur))
        # black_team.pieces.append(pieces.Pawn(black_team, tur))


def place_pieces(white_team: Team, black_team: Team):
    # Add knights.
    # black_team.pieces.extend([pieces.Knight(screen.squares[7][6], black_team), pieces.Knight(screen.squares[7][1], black_team)])
    white_team.pieces.extend([pieces.Knight(screen.squares[0][1], white_team), pieces.Knight(screen.squares[0][6], white_team)])
    # Add bishops.
    # black_team.pieces.extend([pieces.Bishop(screen.squares[7][2], black_team), pieces.Bishop(screen.squares[7][5], black_team)])
    white_team.pieces.extend([pieces.Bishop(screen.squares[0][2], white_team), pieces.Bishop(screen.squares[0][5], white_team)])
    # Add queens.
    # black_team.pieces.append(pieces.Queen(screen.squares[7][4], black_team))
    white_team.pieces.append(pieces.Queen(screen.squares[0][4], white_team))
    # Add rooks.
    # black_team.pieces.extend([pieces.Rook(screen.squares[7][0], black_team), pieces.Rook(screen.squares[7][7], black_team, )])
    white_team.pieces.extend([pieces.Rook(screen.squares[0][0], white_team), pieces.Rook(screen.squares[0][7], white_team)])

    add_pawns(white_team, black_team)
    # Add kings.
    black_team.pieces.append(pieces.King(black_team))
    white_team.pieces.append(pieces.King(white_team))


def is_checkmated(team_got_turn: Team, team_doesnt_got_turn: Team):
    if not is_there_chess(team_doesnt_got_turn):
        return False
    for piece in team_got_turn.pieces:
        if piece.is_eaten:
            continue
        valid_move_squares = piece.get_valid_move_squares()
        for check_move in valid_move_squares:
            if not is_check_after_move(check_move, team_doesnt_got_turn, piece):
                return False

    return True


def is_there_chess(team_doesnt_got_turn):
    for piece in team_doesnt_got_turn.pieces:
        if piece.is_eaten:
            continue

        valid_move_squares = piece.get_valid_move_squares()
        for square in valid_move_squares:
            if isinstance(square.current_piece, pieces.King):
                return True
    return False


def is_check_after_move(clicked_square, team_doesnt_got_turn, piece_clicked: pieces.Piece):
    with SaveMove(piece_clicked, clicked_square):
        piece_clicked.move(clicked_square)
        check_after_move = is_there_chess(team_doesnt_got_turn)
    return check_after_move


def try_to_move(piece_clicked, clicked_square, team_got_turn: Team, team_doesnt_got_turn: Team):
    screen.color_all_square_to_original_color()

    if piece_clicked.team is not team_got_turn:
        raise TeamDoesntGotTurn

    # check_castling.
    if isinstance(piece_clicked, pieces.King) and isinstance(clicked_square.current_piece, pieces.Rook):
        if piece_clicked.team is clicked_square.current_piece.team:
            if not check_castling(piece_clicked, clicked_square, team_got_turn, team_doesnt_got_turn):
                raise CantCastling
            # Did castling.
            return

    if clicked_square not in piece_clicked.get_valid_move_squares():
        raise SquareNotInValidMoves

    if is_check_after_move(clicked_square, team_doesnt_got_turn, piece_clicked):
        raise CheckAfterMove

    piece_clicked.move(clicked_square)

    if isinstance(piece_clicked, pieces.Pawn) and piece_clicked.is_reached_to_end():
        replace_auto_to_queen(piece_clicked)


def replace_auto_to_queen(pawn):
    print(pawn)
    pawn.team.pieces.remove(pawn)
    pawn.team.pieces.append(pieces.Queen(pawn.square, pawn.team))


def replace(pawn_team: Team, pawn):
    pawn_team.pieces.remove(pawn)
    print("Which piece do you want instead of the pawn?")
    piece_chose = input("q - queen, b - bishop, r - rook, k - knight\n")
    option_to_piece = {
        'q': pieces.Queen(pawn.square, pawn.team),
        'b': pieces.Bishop(pawn.square, pawn.team),
        'r': pieces.Rook(pawn.team, pawn.square),
        'k': pieces.Knight(pawn.square, pawn.team),
    }
    try:
        pawn_team.pieces.append(option_to_piece[piece_chose])
        pawn.square.current_piece = option_to_piece[piece_chose]
    except KeyError:
        pawn_team.pieces.append(pawn)
        replace(pawn_team, pawn)


def castling(king, rook, team_got_turn, team_doesnt_got_turn):
    king_line = king.square.line_cord
    king_tur = king.square.tur_cord
    save_king_location = (king_line, king_tur)

    next_king_move = 1 if rook.square.tur_cord > king_tur else -1

    king_tur += next_king_move
    try:
        try_to_move(king, screen.squares[king_line][king_tur], team_got_turn, team_doesnt_got_turn)
        king_tur += next_king_move
        try_to_move(king, screen.squares[king_line][king_tur], team_got_turn, team_doesnt_got_turn)
        rook.move(screen.squares[king_line][king_tur - next_king_move])
        return True
    
    except MoveError:
        king.move(screen.squares[save_king_location[0]][save_king_location[1]])
        return False


def check_castling(king, rook_square, team_got_turn, team_doesnt_got_turn):
    rook = rook_square.current_piece

    if king.move_counter != 0 or rook.move_counter != 0:
        return False

    if is_there_chess(team_doesnt_got_turn):
        return False

    return castling(king, rook, team_got_turn, team_doesnt_got_turn)


def is_tie(team_got_turn, team_doesnt_got_turn):
    # TODO check if it works.
    for piece in team_got_turn.pieces:
        for move_square in piece.get_valid_move_squares():
            with SaveMove(piece, move_square):
                try:
                    try_to_move(piece, move_square, team_got_turn, team_doesnt_got_turn)
                    # Team got turn have a valid move
                    return False
                except MoveError:
                    continue
    return True
