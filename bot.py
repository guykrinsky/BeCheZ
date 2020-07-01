import teams
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
    is_castling, king = try_castling(white_team, bot_team)
    if is_castling:
        return king

    if chess_utils.is_checkmated(bot_team, white_team) or chess_utils.is_tie(bot_team, white_team):
        return None

    score, best_move = mini(white_team, bot_team, depth)

    print(f'piece - {best_move[0]}. moved to - {best_move[1]}\n'
          f'current score after the move is {score}')

    piece, move_square = best_move
    chess_utils.try_to_move(piece, move_square, bot_team, white_team)
    return piece


def mini(white_team: teams.Team, bot_team: teams.Team, depth):
    best_score = 1000
    best_move = None

    if chess_utils.is_tie(bot_team, white_team):
        return 0

    if depth == 0:
        return teams.get_score_dif(white_team, bot_team), best_move

    for piece in bot_team.pieces:
        if piece.is_eaten:
            continue
        valid_moves = piece.get_valid_move_squares()
        for move_square in valid_moves:
            try:
                # If Didn't move, code wouldn't crash, just move to next move.
                score_after_move = futuire_move(piece, move_square, white_team, bot_team, depth, is_bot_futiure_turn=True)

                if score_after_move < best_score:
                    best_move = (piece, move_square)
                    best_score = score_after_move

            except chess_utils.DidntMove:
                pass

    return best_score, best_move


def maxi(white_team: teams.Team, bot_team: teams.Team, depth):
    best_move = None
    best_score = -1000

    if chess_utils.is_tie(bot_team, white_team):
        return 0

    if depth == 0:
        return teams.get_score_dif(white_team, bot_team), best_move

    for piece in white_team.pieces:
        if piece.is_eaten:
            continue

        valid_moves = piece.get_valid_move_squares()
        for move_square in valid_moves:
            try:
                # If Didn't move code wouldn't crash, just move to next move.
                with chess_utils.SaveMove(piece, move_square):
                    score_after_move = futuire_move(piece, move_square, white_team, bot_team, depth, is_bot_futiure_turn=False)

                    if score_after_move > best_score:
                        best_move = (piece, move_square)
                        best_score = score_after_move

            except chess_utils.DidntMove:
                pass

    return best_score, best_move


def futuire_move(piece, move_square, white_team, bot_team, depth, is_bot_futiure_turn):
    next_move = maxi if is_bot_futiure_turn else mini
    team_got_turn = bot_team if is_bot_futiure_turn else white_team
    team_doesnt_got_turn = white_team if team_got_turn is bot_team else bot_team

    with chess_utils.SaveMove(piece, move_square):
        try:
            chess_utils.try_to_move(piece, move_square, team_got_turn, team_doesnt_got_turn)
        except chess_utils.MoveError:
            raise chess_utils.DidntMove

        score_after_move, _ = next_move(white_team, bot_team, depth - 1)

    return score_after_move


# This two fuctions not in use.
def maxi_without_with(white_team: teams.Team, bot_team: teams.Team, depth):
    best_move = None
    best_score = -1000

    if chess_utils.is_checkmated(white_team, bot_team):
        return best_score, best_move

    if depth == 0:
        return teams.get_score_dif(white_team, bot_team), best_move

    for piece in white_team.pieces:
        for move_square in piece.get_valid_move_squares():
            eaten_piece = move_square.current_piece
            current_piece_square = piece.square

            if chess_utils.try_to_move(piece, move_square, white_team, bot_team):

                score_after_move, _ = mini(white_team, bot_team, depth-1)

                if score_after_move > best_score:
                    best_move = (piece, move_square)
                    best_score = score_after_move
                piece.move(current_piece_square)
                if eaten_piece is not None:
                    eaten_piece.move(eaten_piece.square)
                    eaten_piece.is_eaten = False

    return best_score, best_move


def mini_with_alph_beta_proving(white_team: teams.Team, bot_team: teams.Team, alpha, beta, depth):
    best_score = 1000
    best_move = None

    if depth == 0:
        return teams.get_score_dif(white_team, bot_team), best_move

    for piece in bot_team.pieces:
        valid_moves = piece.get_valid_move_squares()
        for move_square in valid_moves:
            with chess_utils.SaveMove(piece, move_square):

                if chess_utils.try_to_move(piece, move_square, bot_team, white_team):
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
