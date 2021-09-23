from chess_utils import *
from teams import *
import timer
import protocol
import screen
import exceptions
import bot
import os
import threading
import socket
import pygame
import random
import string

SOUNDS_PATH = 'sounds'

team_got_turn = Team(is_white_team=True)
team_doesnt_got_turn = Team(is_white_team=False)
turn_number = 0
name = "default_name"
my_socket = None


BOT_GAME = 1
ONLINE_GAME = 2
TWO_PLAYERS_GAME = 3


def update_screen():
    while True:
        pygame.display.flip()


def redraw_scoreboard():
    white_team, black_team = get_teams_colors(team_got_turn, team_doesnt_got_turn)
    while True:
        screen.draw_scoreboard(team_got_turn, team_doesnt_got_turn)
        check_timers_out_of_time(white_team, black_team)


def get_square_clicked():
    mouse_pos = pygame.mouse.get_pos()

    for line in screen.squares:
        for square in line:
            if square.rect.collidepoint(mouse_pos):
                return square


def switch_turn(white_team, black_team):
    global team_got_turn
    global team_doesnt_got_turn
    team_got_turn = team_doesnt_got_turn
    if team_got_turn is white_team:
        team_doesnt_got_turn = black_team
    else:
        team_doesnt_got_turn = white_team

    timer.switch_timers(team_got_turn, team_doesnt_got_turn)


def remove_eaten_pieces(white_team, black_team):
    for piece in white_team.pieces + black_team.pieces:
        piece_team = white_team if piece.team.is_white_team else black_team
        if piece.is_eaten:
            piece_team.pieces.remove(piece)


def update_eaten_pieces(white_team: Team, black_team: Team):
    for piece in white_team.pieces:
        if piece.is_eaten and piece not in white_team.eaten_pieces:
            white_team.eaten_pieces.append(piece)
            return
    for piece in black_team.pieces:
        if piece.is_eaten and piece not in black_team.eaten_pieces:
            black_team.eaten_pieces.append(piece)


def update_game_after_move(piece_clicked, black_team, white_team):
    switch_turn(white_team, black_team)
    screen.draw_board()
    update_eaten_pieces(white_team, black_team)
    screen.draw_eaten_pieces(white_team, black_team)
    global turn_number
    pygame.mixer.Sound(os.path.join(SOUNDS_PATH, 'pong.wav')).play()

    print(piece_clicked)

    if is_checkmated(team_got_turn, team_doesnt_got_turn):
        screen.draw_winner(team_doesnt_got_turn)
        raise exceptions.Checkmated

    if is_tie(team_got_turn, team_doesnt_got_turn):
        screen.draw_tie()
        raise exceptions.Tie

    piece_clicked.move_counter += 1
    turn_number += 1

    remove_eaten_pieces(white_team, black_team)

    # only for print shit.
    score_dif = get_score_difference(white_team, black_team)
    team_leading = white_team if score_dif > 0 else black_team
    print(f'turn {turn_number}:\n'
          f'team leading is {team_leading} in {score_dif}\n'
          f'keep going!')


def print_board(white_team, black_team):
    print(white_team)
    white_team.print_pieces()
    print(black_team)
    black_team.print_pieces()


def check_timers_out_of_time(white_team, black_team):
    try:
        # If white team is out of time exception would raise and black team would win
        team_won = black_team
        white_team.timer.update_timer()

        # If black team is out of time exception would raise and white team would win
        team_won = white_team
        black_team.timer.update_timer()

    except exceptions.RunOutOfTime:
        screen.draw_winner(team_won)
        raise


def random_word(length):
    return ''.join(random.choice(string.ascii_letters) for x in range(length))


def get_games_list():
    games = list()
    list_length = my_socket.recv(1).decode()
    print(f"number of players waiting for their games is {list_length}")
    for x in range(int(list_length)):
        game_title_length = int(my_socket.recv(1).decode())
        games.append(my_socket.recv(game_title_length).decode())
    return games


def event_handler(event, piece_clicked, game_type):
    white_team, black_team = get_teams_colors(team_got_turn, team_doesnt_got_turn)

    if event.type == pygame.QUIT:
        raise exceptions.UserExitGame

    if event.type != pygame.MOUSEBUTTONDOWN:
        return piece_clicked

    # User clikced on something.
    clicked_square = get_square_clicked()

    if clicked_square is None:
        # User click on something out of board.
        return piece_clicked

    if piece_clicked is None:
        if clicked_square.current_piece in team_got_turn.pieces:
            piece_clicked = clicked_square.current_piece
            piece_clicked.color_next_step()
            screen.draw_board()  # Draw the colored squares.
        return piece_clicked

    # If user already clicked on a piece,
    # we try to move the piece to the square the user clicked on.
    try:
        starting_square = str(piece_clicked.square.line_cord) + str(piece_clicked.square.tur_cord)
        destination_square = str(clicked_square.line_cord) + str(clicked_square.tur_cord)

        try_to_move(piece_clicked, clicked_square, team_got_turn, team_doesnt_got_turn)
        # Move have finished successfully.

        if game_type == ONLINE_GAME:

            # send move to server
            move = starting_square + destination_square
            request = protocol.set_request_to_server(protocol.Request(name, protocol.REGULAR_MOVE, move))
            my_socket.send(request)

        update_game_after_move(piece_clicked, black_team, white_team)
        return None

    except exceptions.MoveError:
        # The move wasn't valid.
        pygame.mixer.Sound(os.path.join(SOUNDS_PATH, 'error.wav')).play()

        # Print all the squares in their original colors.
        screen.draw_board()
        return None


def game_loop(game_type, my_team, bot_depth=0):
    white_team, black_team = get_teams_colors(team_got_turn, team_doesnt_got_turn)
    white_team.timer.resume()
    piece_clicked = None
    screen.draw_bg(team_got_turn, team_doesnt_got_turn)

    while True:
        if team_got_turn is not my_team and game_type == BOT_GAME:
            # bot turn.
            piece_moved = bot.move(team_doesnt_got_turn, team_got_turn, bot_depth)
            update_game_after_move(piece_moved, black_team, white_team)

        elif team_got_turn is not my_team and game_type == ONLINE_GAME:
            start_square = screen.squares[int(my_socket.recv(1))][int(my_socket.recv(1))]
            destination_square = screen.squares[int(my_socket.recv(1))][int(my_socket.recv(1))]
            piece_moved = start_square.current_piece
            piece_moved.move(destination_square)
            update_game_after_move(piece_moved, black_team, white_team)

        else:
            for event in pygame.event.get():
                piece_clicked = event_handler(event, piece_clicked, game_type)


def main():
    # Get game data from user.
    is_one_player, game_length, bot_depth, is_player_white = screen.starting_screen()

    timer.set_game_length(game_length)
    screen.add_squares_to_board()
    white_team, black_team = get_teams_colors(team_got_turn, team_doesnt_got_turn)
    place_pieces(white_team, black_team)

    my_team = white_team if is_player_white else black_team
    game_type = ONLINE_GAME

    screen.draw_eaten_pieces(white_team, black_team)

    # Start remote threads.
    scoreboard_thread = threading.Thread(target=redraw_scoreboard, daemon=True)
    scoreboard_thread.start()
    board_thread = threading.Thread(target=update_screen, daemon=True)
    board_thread.start()

    if game_type == ONLINE_GAME:
        # connect to server
        global my_socket
        my_socket = socket.socket()
        my_socket.connect(("127.0.0.1", protocol.SERVER_PORT))
        global name
        # name = input("Enter your name:")
        name = random_word(5)
        print(f"Your name is : {name}")

        my_socket.send(protocol.set_request_to_server(protocol.Request(name, protocol.GET_GAMES)))
        games_list = get_games_list()
        print(f"Games list is: {games_list}")

        if len(games_list) == 0:
            my_team = white_team
            print("Creating game")
            my_socket.send(protocol.set_request_to_server(protocol.Request(name, protocol.CREATE_GAME)))
            print("waiting for second player")
            opponent_player_name_length = int(my_socket.recv(1).decode())
            opponent_player_name = my_socket.recv(opponent_player_name_length).decode()
            print(f"Playing against: {opponent_player_name}")

        # There is someone waiting for opponent.
        else:
            my_team = black_team
            counter = 0
            while counter < len(games_list):
                opponent_name = games_list[counter]
                print(f"trying to join to {opponent_name} game")
                my_socket.send(protocol.set_request_to_server(protocol.Request(name, protocol.JOIN_GAME, opponent_name)))
                is_valid = my_socket.recv(1)
                if not is_valid:
                    print("oops Error")
                    counter += 1

                # joined to game successfully.
                print("")
                break

    try:
        game_loop(game_type, my_team)

    except exceptions.UserExitGame:
        return

    except exceptions.GameEnd:
        print("Game ended.")
        timer.sleep(10)
        # TODO: Return to main screen.
        return


if __name__ == '__main__':
    main()
