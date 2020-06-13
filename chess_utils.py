import pygame
import Screen
import pieces
from teams import Team


class SaveMove:
    def __init__(self, piece: pieces.Piece, move_square: Screen.Square):
        self.piece = piece
        self.move_square = move_square
        self.eaten_piece = None
        self.current_piece_square = None

    def __enter__(self):
        self.eaten_piece = self.move_square.current_piece
        self.current_piece_square = self.piece.square

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Move pieces moved to there last position.
        self.piece.move(self.current_piece_square)
        if self.eaten_piece is not None:
            self.eaten_piece.move(self.eaten_piece.square)
            self.eaten_piece.is_eaten = False


def add_pawns(white_team, black_team):
    for place in range(Screen.BOARD_LINE):
        white_team.pieces.append(pieces.Pawn(True, place))
    for place in range(Screen.BOARD_LINE):
        black_team.pieces.append(pieces.Pawn(False, place))


def get_score(white_team: Team, black_team: Team):
    white_team.update_score()
    black_team.update_score()

    return white_team.score - black_team.score


def place_pieces(white_team: Team, black_team: Team):
    # Added knights.
    black_team.pieces.extend([pieces.Knight(Screen.squares[7][6], False), pieces.Knight(Screen.squares[7][1], False)])
    white_team.pieces.extend([pieces.Knight(Screen.squares[0][1], True), pieces.Knight(Screen.squares[0][6], True)])
    # Added bishops.
    black_team.pieces.extend([pieces.Bishop(Screen.squares[7][2], False), pieces.Bishop(Screen.squares[7][5], False)])
    white_team.pieces.extend([pieces.Bishop(Screen.squares[0][2], True), pieces.Bishop(Screen.squares[0][5], True)])
    # Added queens.
    black_team.pieces.append(pieces.Queen(Screen.squares[7][4], False))
    white_team.pieces.append(pieces.Queen(Screen.squares[0][4], True))
    # Added rooks.
    black_team.pieces.extend([pieces.Rook(False, Screen.squares[7][0]),pieces.Rook(False, Screen.squares[7][7])])
    white_team.pieces.extend([pieces.Rook(True, Screen.squares[0][0]), pieces.Rook(True, Screen.squares[0][7])])

    add_pawns(white_team, black_team)
    # Added kings.
    black_team.pieces.append(pieces.King(False))
    white_team.pieces.append(pieces.King(True))


def is_checkmated(team_got_turn: Team, team_doesnt_got_turn: Team):

    for piece in team_got_turn.pieces:
        valid_move_squares = piece.get_valid_move_squares()
        for check_move in valid_move_squares:
            if not is_check_after_move(check_move, team_doesnt_got_turn, piece):
                return False

    return True


def check_if_there_is_chess(team_doesnt_got_turn):
    for piece in team_doesnt_got_turn.pieces:
        if piece.is_eaten:
            continue

        valid_move_squares = piece.get_valid_move_squares()
        for square in valid_move_squares:
            if isinstance(square.current_piece, pieces.King):
                return True

    return False


def move_turn(piece_clicked, clicked_square, team_got_turn: Team, team_doesnt_got_turn: Team):
    Screen.color_all_square_to_original_color()

    if piece_clicked not in team_got_turn.pieces:
        return False

    # check_castling.
    if isinstance(piece_clicked, pieces.King) and isinstance(clicked_square.current_piece, pieces.Rook):
        return check_castling(piece_clicked, clicked_square, team_got_turn, team_doesnt_got_turn)

    if clicked_square not in piece_clicked.get_valid_move_squares():
        return False
    if is_check_after_move(clicked_square, team_doesnt_got_turn, piece_clicked):
        return False

    piece_clicked.move(clicked_square)

    if isinstance(piece_clicked, pieces.Pawn) and piece_clicked.is_reached_to_end():
        replace(team_got_turn, piece_clicked)
    return True


def replace(pawn_team: Team, pawn):
    pawn_team.pieces.remove(pawn)
    print("Which piece do you want instead of the pawn?")
    piece_chose = input("q - queen, b - bishop, r - rook, k - knight\n")
    option_to_piece = {
        'q': pieces.Queen(pawn.square, pawn.IS_IN_WHITE_TEAM),
        'b': pieces.Bishop(pawn.square, pawn.IS_IN_WHITE_TEAM),
        'r': pieces.Rook(pawn.IS_IN_WHITE_TEAM, pawn.square),
        'k': pieces.Knight(pawn.square, pawn.IS_IN_WHITE_TEAM),
    }
    try:
        pawn_team.pieces.append(option_to_piece[piece_chose])
        pawn.square.current_piece = option_to_piece[piece_chose]
    except KeyError:
        pawn_team.pieces.append(pawn)
        replace(pawn_team, pawn)


def do_castling(king, rook, team_got_turn, team_doesnt_got_turn):

    king_line = king.square.line_cord
    king_tur = king.square.tur_cord
    save_king_location = (king_line, king_tur)

    next_king_move = -1
    if rook.square.tur_cord > king_tur:
        next_king_move = 1

    king_tur += next_king_move
    if move_turn(king, Screen.squares[king_line][king_tur], team_got_turn, team_doesnt_got_turn):
        king_tur += next_king_move
        if move_turn(king, Screen.squares[king_line][king_tur], team_got_turn, team_doesnt_got_turn):
            rook.move(Screen.squares[king_line][king_tur - next_king_move])
            return True

    king.move(Screen.squares[save_king_location[0]][save_king_location[1]])
    return False


def check_castling(king, rook_square, team_got_turn, team_doesnt_got_turn):
    rook = rook_square.current_piece

    if king.move_counter != 0 or rook.move_counter != 0:
        return False

    if check_if_there_is_chess(team_doesnt_got_turn):
        return False

    return do_castling(king, rook, team_got_turn, team_doesnt_got_turn)


def is_check_after_move(clicked_square, team_doesnt_got_turn, piece_clicked: pieces.Piece):
    with SaveMove(piece_clicked, clicked_square):
        piece_clicked.move(clicked_square)
        check_after_move = check_if_there_is_chess(team_doesnt_got_turn)

    return check_after_move
