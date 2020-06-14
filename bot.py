from teams import Team
import chess_utils
import pieces


def move(white_team: Team, bot_team: Team, depth=2):
    if chess_utils.is_checkmated(bot_team, white_team):
        return None

    _, best_move = mini(white_team, bot_team, -10000000, 1000000, depth)
    piece, move_square = best_move
    chess_utils.move_turn(piece, move_square, bot_team, white_team)
    return piece


def mini(white_team: Team, bot_team: Team, alpha, beta, depth):
    best_score = 1000
    best_move = None

    if chess_utils.is_checkmated(bot_team, white_team):
        return best_score, best_move

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
                        return alpha, best_move

                    if score_after_move < beta:
                        # Bigger score -> White player is winning.
                        best_move = (piece, move_square)
                        beta = score_after_move

    return beta, best_move


def maxi(white_team: Team, bot_team: Team, alpha, beta, depth):
    best_move = None
    best_score = -1000

    if chess_utils.is_checkmated(white_team, bot_team):
        return best_score, best_move

    if depth == 0:
        return chess_utils.get_score(white_team, bot_team), best_move

    # if chess_utils.check_if_there_is_chess(bot_team):
    #     # breakpoint()
    #     x = 1 + 2

    for piece in white_team.pieces:
        for move_square in piece.get_valid_move_squares():
            with chess_utils.SaveMove(piece, move_square):

                if chess_utils.move_turn(piece, move_square, white_team, bot_team):
                    score_after_move, _ = mini(white_team, bot_team, alpha, beta, depth-1)
                    if score_after_move > beta:
                        best_move = (piece, move_square)
                        return beta, best_move

                    if score_after_move > alpha:
                        # Bigger score -> White player is winning.
                        best_move = (piece, move_square)
                        alpha = score_after_move

    return alpha, best_move


# def search_mate(white_team, bot_team, fake_moves):
#     for piece in bot_team.pieces:
#         for square in piece.get_valid_move_squares():
#             fake_moves.append([piece, square])
#             chess_utils.move_turn(piece, square, white_team=white_team, black_team=bot_team,
#                                   team_got_turn=bot_team)
#             if chess_utils.check_if_there_is_chess(white_team, bot_team, white_team):
#                 for move in fake_moves:
#                     piece = move[0]
#                     square = move[1]
#                     piece.move(square)
#
#                 for white_piece in white_team.pieces:
#                     white_piece.is_eaten = False
#
#                 move = fake_moves[0]
#                 piece = move[0]
#                 square = move[1]
#                 chess_utils.move_turn(piece, square, white_team=white_team, black_team=bot_team,
#                                       team_got_turn=bot_team)
#                 piece.move_counter += 1
#                 return
#     search_mate(white_team, bot_team, fake_moves)

def search_mate(white_team, bot_team, fake_moves,):
    moves = []
    for piece in bot_team.pieces:
        for square in piece.get_valid_move_squares():
            moves.append([piece, square])
            chess_utils.move_turn(piece, square, white_team=white_team, black_team=bot_team,
                                  team_got_turn=bot_team)
            if chess_utils.check_if_there_is_chess(white_team, bot_team, white_team):
                for move in fake_moves:
                    piece = move[0]
                    square = move[1]
                    piece.move(square)

                for white_piece in white_team.pieces:
                    white_piece.is_eaten = False

                move = fake_moves[0]
                piece = move[0]
                square = move[1]
                chess_utils.move_turn(piece, square, white_team=white_team, black_team=bot_team,
                                      team_got_turn=bot_team)
                piece.move_counter += 1
                return
    search_mate(white_team, bot_team, fake_moves)



def get_best_move(white_team, bot_team, is_fake_turn_white):
    best_score_dif = -180
    save_square = None
    save_piece = None
    team = bot_team
    if is_fake_turn_white:
        team = white_team
    for piece in team.pieces:
        for square in piece.get_valid_move_squares():
            eaten_piece = square.current_piece
            if eaten_piece is not None:
                print(eaten_piece)
            current_piece_square = piece.square
            if chess_utils.move_turn(piece, square, False, white_team, bot_team):
                white_team.update_score()
                bot_team.update_score()
                current_diff = bot_team.score - white_team.score
                if current_diff > best_score_dif:
                    save_square = square
                    save_piece = piece
                    best_score_dif = current_diff

                piece.move(current_piece_square)
                if eaten_piece is not None:
                    eaten_piece.move(eaten_piece.square)
                    eaten_piece.is_eaten = False
    return save_piece, save_square, best_score_dif
