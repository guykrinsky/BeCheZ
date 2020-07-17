import teams
import chess_utils
import pieces

MAXIMUM_SCORE = 10_000_000
MINIMUM_SCORE = -1 * MAXIMUM_SCORE


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

    if rook1_square is not None:
        try:
            chess_utils.try_to_move(king, rook1_square, bot_team, white_team)
            return True, king
        except chess_utils.MoveError:
            pass

    if rook2_square is not None:
        try:
            chess_utils.try_to_move(king, rook2_square, bot_team, white_team)
            return True, king

        except chess_utils.MoveError:
            pass

    return False, king


def move(white_team: teams.Team, bot_team: teams.Team, depth=2):
    did_castling, king = try_castling(white_team, bot_team)
    if did_castling:
        return king

    if chess_utils.is_checkmated(bot_team, white_team):
        raise chess_utils.Checkmated

    if chess_utils.is_tie(bot_team, white_team):
        raise chess_utils.Tie

    score, best_move = mini(white_team, bot_team, depth, MINIMUM_SCORE)
    piece_moved, move_square = best_move

    chess_utils.try_to_move(piece_moved, move_square, bot_team, white_team)
    return piece_moved


def mini(white_team: teams.Team, bot_team: teams.Team, depth, max_from_previous_moves):
    best_score = MAXIMUM_SCORE
    best_move = None

    if depth == 0:
        return teams.get_score_dif(white_team, bot_team), None

    for piece in bot_team.pieces:
        if piece.is_eaten:
            continue
        valid_moves = piece.get_valid_move_squares()
        for move_square in valid_moves:
            try:
                # If Didn't move, code wouldn't crash, just move to next move.
                score_after_move = future_move(piece, move_square, white_team, bot_team, depth, best_score,
                                               is_bot_future_turn=True)

                if score_after_move <= max_from_previous_moves:
                    best_move = (piece, move_square)
                    best_score = score_after_move
                    return best_score, best_move

                if score_after_move < best_score:
                    best_move = (piece, move_square)
                    best_score = score_after_move

            except chess_utils.DidntMove:
                pass

    return best_score, best_move


def maxi(white_team: teams.Team, bot_team: teams.Team, depth, min_from_previous_moves):
    best_move = None
    best_score = MINIMUM_SCORE

    if depth == 0:
        return teams.get_score_dif(white_team, bot_team), best_move

    for piece in white_team.pieces:
        if piece.is_eaten:
            continue
        valid_moves = piece.get_valid_move_squares()
        for move_square in valid_moves:
            try:
                # If Didn't move code wouldn't crash, just move to next move.
                score_after_move = future_move(piece, move_square, white_team, bot_team, depth, best_score,
                                               is_bot_future_turn=False)

                if score_after_move >= min_from_previous_moves:
                    best_move = (piece, move_square)
                    best_score = score_after_move
                    return best_score, best_move

                if score_after_move > best_score:
                    best_move = (piece, move_square)
                    best_score = score_after_move

            except chess_utils.DidntMove:
                pass

    return best_score, best_move


def future_move(piece, move_square, white_team, bot_team, depth, min_or_max, is_bot_future_turn):
    next_move = maxi if is_bot_future_turn else mini
    team_got_turn = bot_team if is_bot_future_turn else white_team
    team_doesnt_got_turn = white_team if team_got_turn is bot_team else bot_team

    with chess_utils.SaveMove(piece, move_square):
        try:
            chess_utils.try_to_move(piece, move_square, team_got_turn, team_doesnt_got_turn)
        except chess_utils.MoveError:
            raise chess_utils.DidntMove

        score_after_move, _ = next_move(white_team, bot_team, depth - 1, min_or_max)
    return score_after_move
