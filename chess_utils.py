import pygame
import Screen
import pieces
from teams import Team


def add_pawns(white_team, black_team):
    for place in range(Screen.BOARD_LINE):
        white_team.pieces.append(pieces.Pawn(True, place))
    for place in range(Screen.BOARD_LINE):
        black_team.pieces.append(pieces.Pawn(False, place))


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


def is_checkmated(white_team: Team, black_team: Team, is_turn_white):
    team_have_turn = black_team
    if white_team.is_white_team is is_turn_white:
        team_have_turn = white_team

    for piece in team_have_turn.pieces:

        valid_move_squares = piece.get_valid_move_squares()

        for check_move in valid_move_squares:
            if not is_check_after_move(check_move, is_turn_white, piece, white_team, black_team):
                return False

    return True


def check_if_there_is_chess(white_team, black_team, is_turn_white):
    team_doesnt_have_turn = black_team
    if white_team.is_white_team is not is_turn_white:
        team_doesnt_have_turn = white_team

    for piece in team_doesnt_have_turn.pieces:
        if not piece.is_eaten:
            valid_move_squares = piece.get_valid_move_squares()
            for square in valid_move_squares:
                if isinstance(square.current_piece, pieces.King):
                    return True
    return False


def move_turn(piece_clicked, clicked_square, is_white_team_turn, white_team, black_team):
    Screen.color_all_square_to_original_color()

    if piece_clicked.is_white_team is not is_white_team_turn:
        return False

    # check_castling.
    if isinstance(piece_clicked, pieces.King) and isinstance(clicked_square.current_piece, pieces.Rook):
        return check_castling(piece_clicked, clicked_square, is_white_team_turn, white_team, black_team)

    if clicked_square not in piece_clicked.get_valid_move_squares():
        return False

    if is_check_after_move(clicked_square, is_white_team_turn, piece_clicked, white_team, black_team):
        return False

    piece_clicked.move(clicked_square)
    return True


def do_castling(king, rook, is_white_team_turn, white_team, black_team):

    king_line = king.square.line_cord
    king_tur = king.square.tur_cord
    save_king_location = (king_line, king_tur)

    next_king_move = -1
    if rook.square.tur_cord > king_tur:
        next_king_move = 1

    king_tur += next_king_move
    if move_turn(king, Screen.squares[king_line][king_tur], is_white_team_turn, white_team, black_team):
        king_tur += next_king_move
        if move_turn(king, Screen.squares[king_line][king_tur], is_white_team_turn, white_team, black_team):
            rook.move(Screen.squares[king_line][king_tur - next_king_move])
            return True

    king.move(Screen.squares[save_king_location[0]][save_king_location[1]])
    return False


def check_castling(king, rook_square, is_white_team_turn, white_team, black_team):
    rook = rook_square.current_piece

    if king.move_counter != 0 or rook.move_counter != 0:
        return False

    if check_if_there_is_chess(white_team, black_team, is_white_team_turn):
        return False

    return do_castling(king, rook, is_white_team_turn, white_team, black_team)


def is_check_after_move(clicked_square, is_white_team_turn, piece_clicked: pieces.Piece, white_team: Team, black_team: Team):
    eaten_piece = clicked_square.current_piece

    current_piece_square = piece_clicked.square
    piece_clicked.move(clicked_square)

    check_after_move = check_if_there_is_chess(white_team, black_team, is_white_team_turn)

    piece_clicked.move(current_piece_square)

    if eaten_piece is not None:
        eaten_piece.move(clicked_square)
        eaten_piece.is_eaten = False

    return check_after_move
