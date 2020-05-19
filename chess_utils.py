import pygame
import Screen
import pieces


def add_pawns(board_pieces):
    for place in range(Screen.BOARD_LINE):
        board_pieces.append(pieces.Pawn(True, place))
    for place in range(Screen.BOARD_LINE):
        board_pieces.append(pieces.Pawn(False, place))
    return board_pieces


def place_pieces():
    # Added kings.
    board_pieces = [pieces.King(False), pieces.King(True)]
    # Added rooks.
    board_pieces.extend([pieces.Rook(True, Screen.squares[0][0]), pieces.Rook(False, Screen.squares[7][0]),
                         pieces.Rook(True, Screen.squares[0][7]), pieces.Rook(False, Screen.squares[7][7])])
    # Added bishops.
    board_pieces.extend([pieces.Bishop(Screen.squares[0][2], True), pieces.Bishop(Screen.squares[0][5], True),
                         pieces.Bishop(Screen.squares[7][2], False), pieces.Bishop(Screen.squares[7][5], False)])
    # Added queens.
    board_pieces.extend([pieces.Queen(Screen.squares[0][4], True), pieces.Queen(Screen.squares[7][4], False)])
    # Added knights.
    board_pieces.extend([pieces.Knight(Screen.squares[0][1], True), pieces.Knight(Screen.squares[0][6], True),
                         pieces.Knight(Screen.squares[7][6], False), pieces.Knight(Screen.squares[7][1], False)])
    board_pieces = add_pawns(board_pieces)
    return board_pieces


def is_checkmated(board_pieces, turn_is_white):
    for piece in board_pieces:
        if piece.is_white_team is not turn_is_white:
            continue

        valid_move_squares = piece.get_valid_move_squares()

        for check_move in valid_move_squares:
            if not is_check_after_move(check_move, turn_is_white, piece, board_pieces):
                return False

    return True


def check_if_there_is_chess(board_pieces, turn_is_white):
    for piece in board_pieces:
        if piece.is_white_team is not turn_is_white and not piece.is_eaten:
            valid_move_squares = piece.get_valid_move_squares()
            for square in valid_move_squares:
                if isinstance(square.current_piece, pieces.King):
                    return True
    return False


def do_castling(king, rook, is_white_team_turn, board_pieces):

    king_line = king.square.line_cord
    king_tur = king.square.tur_cord
    save_king_location = (king_line, king_tur)

    next_king_move = -1
    if rook.square.tur_cord > king_tur:
        next_king_move = 1

    king_tur += next_king_move
    if move_turn(king, Screen.squares[king_line][king_tur], is_white_team_turn, board_pieces):
        king_tur += next_king_move
        if move_turn(king, Screen.squares[king_line][king_tur], is_white_team_turn, board_pieces):
            rook.move(Screen.squares[king_line][king_tur - next_king_move])
            return True

    king.move(Screen.squares[save_king_location[0]][save_king_location[1]])
    return False


def check_castling(king, rook_square, is_white_team_turn, board_pieces):
    rook = rook_square.current_piece

    if king.move_counter != 0 or rook.move_counter != 0:
        return False

    if check_if_there_is_chess(board_pieces, is_white_team_turn):
        return False

    return do_castling(king, rook, is_white_team_turn, board_pieces)


def is_check_after_move(clicked_square, is_white_team_turn, piece_clicked: pieces.Piece, board_pieces):
    eaten_piece = clicked_square.current_piece

    current_piece_square = piece_clicked.square
    piece_clicked.move(clicked_square)

    check_after_move = check_if_there_is_chess(board_pieces, is_white_team_turn)

    piece_clicked.move(current_piece_square)

    if eaten_piece is not None:
        eaten_piece.move(clicked_square)
        eaten_piece.is_eaten = False

    return check_after_move
