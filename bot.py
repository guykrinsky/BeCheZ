from teams import Team
import chess_utils
import pieces


def try_castling(white_team, bot_team):
    king = None
    rook1_square = None
    rook2_square = None
    for piece in bot_team.pieces:
        if isinstance(piece, pieces.King):
            king = piece
            continue

        if isinstance(piece, pieces.Rook):
            if rook1_square is None:
                rook1_square = piece.square
                continue
            rook2_square = piece.square

    if rook1_square is not None and chess_utils.move_turn(king, rook1_square, bot_team, white_team):
        return True, king
    if rook2_square is not None and chess_utils.move_turn(king, rook2_square, bot_team, white_team):
        return True, king

    return False, king


def move(white_team: Team, bot_team: Team, depth=2):
    is_castling, king = try_castling(white_team, bot_team)
    if is_castling:
        return king

    if chess_utils.is_checkmated(bot_team, white_team):
        return None

    _, best_move = mini(white_team, bot_team, depth)
    piece, move_square = best_move
    chess_utils.move_turn(piece, move_square, bot_team, white_team)
    return piece


def mini(white_team: Team, bot_team: Team, depth):
    best_score = 1000
    best_move = None

    if depth == 0:
        return chess_utils.get_score(white_team, bot_team), best_move

    for piece in bot_team.pieces:
        valid_moves = piece.get_valid_move_squares()
        for move_square in valid_moves:
            with chess_utils.SaveMove(piece, move_square):

                if not chess_utils.move_turn(piece, move_square, bot_team, white_team):
                    continue

                score_after_move, _ = maxi(white_team, bot_team, depth - 1)
                if score_after_move < best_score:
                    best_move = (piece, move_square)
                    best_score = score_after_move

    return best_score, best_move


def maxi(white_team: Team, bot_team: Team, depth):
    best_move = None
    best_score = -1000

    if depth == 0:
        return chess_utils.get_score(white_team, bot_team), best_move

    for piece in white_team.pieces:
        for move_square in piece.get_valid_move_squares():
            with chess_utils.SaveMove(piece, move_square):

                if not chess_utils.move_turn(piece, move_square, white_team, bot_team):
                    continue

                score_after_move, _ = mini(white_team, bot_team, depth-1)

                if score_after_move > best_score:
                    best_move = (piece, move_square)
                    best_score = score_after_move

    return best_score, best_move


# This two fuctions not in use.
def maxi_without_with(white_team: Team, bot_team: Team, depth):
    best_move = None
    best_score = -1000

    if chess_utils.is_checkmated(white_team, bot_team):
        return best_score, best_move

    if depth == 0:
        return chess_utils.get_score(white_team, bot_team), best_move

    for piece in white_team.pieces:
        for move_square in piece.get_valid_move_squares():
            eaten_piece = move_square.current_piece
            current_piece_square = piece.square

            if chess_utils.move_turn(piece, move_square, white_team, bot_team):

                score_after_move, _ = mini(white_team, bot_team, depth-1)

                if score_after_move > best_score:
                    best_move = (piece, move_square)
                    best_score = score_after_move
                piece.move(current_piece_square)
                if eaten_piece is not None:
                    eaten_piece.move(eaten_piece.square)
                    eaten_piece.is_eaten = False

    return best_score, best_move


def mini_with_alph_beta_proving(white_team: Team, bot_team: Team, alpha, beta, depth):
    best_score = 1000
    best_move = None

    if depth == 0:
        return chess_utils.get_score(white_team, bot_team), best_move

    for piece in bot_team.pieces:
        valid_moves = piece.get_valid_move_squares()
        for move_square in valid_moves:
            with chess_utils.SaveMove(piece, move_square):

                if chess_utils.move_turn(piece, move_square, bot_team, white_team):
                    score_after_move, _ = maxi(white_team, bot_team, alpha, beta, depth-1)

                    if score_after_move <= alpha:
                        best_move = (piece, move_square)

                    if score_after_move < beta:
                        # Bigger score -> White player is winning.
                        best_move = (piece, move_square)
                        beta = score_after_move
                else:
                    continue

            if score_after_move <= alpha:
                return alpha, best_move

    return beta, best_move
