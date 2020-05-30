from teams import Team
import chess_utils


def move(white_team: Team, bot_team: Team):
    best_score_dif = -200
    save_square = 0
    save_piece = 0
    for piece in bot_team.pieces:
        for square in piece.get_valid_move_squares():
            eaten_piece = square.current_piece
            current_piece_square = piece.square
            chess_utils.move_turn(piece, square, white_team, bot_team, False)
            player_team_fake_move = get_best_move(white_team, bot_team, True)
            print(player_team_fake_move[2])
            if player_team_fake_move[2] > best_score_dif:
                save_square = square
                save_piece = piece
                best_score_dif = player_team_fake_move[2]
            piece.move(current_piece_square)
            if eaten_piece is not None:
                eaten_piece.move(eaten_piece.square)
                eaten_piece.is_eaten = False

    chess_utils.move_turn(save_piece, save_square, False, white_team, bot_team)
    save_piece.move_counter += 1


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
