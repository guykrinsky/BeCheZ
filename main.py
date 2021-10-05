from chess_utils import *
from teams import *
import timer
import protocol
import screen
import opening_screen
import exceptions
import bot
import os
import threading
import socket
import pygame
import random
import string
import logging

SOUNDS_PATH = 'sounds'

team_got_turn = Team(is_white_team=True)
team_doesnt_got_turn = Team(is_white_team=False)
turn_number = 0
username = "default_name"
my_socket = None


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

    logging.debug(f"piece moved is {piece_clicked}")

    if is_checkmated(team_got_turn, team_doesnt_got_turn):
        screen.draw_winner(team_doesnt_got_turn)
        raise exceptions.Checkmated

    if is_tie(team_got_turn, team_doesnt_got_turn):
        screen.draw_tie()
        raise exceptions.Tie

    piece_clicked.move_counter += 1
    remove_eaten_pieces(white_team, black_team)

    turn_number += 1
    logging.info(f"turn number: {turn_number}")


# For debugging
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
        raise exceptions.GameEnd


def random_word(length):
    return ''.join(random.choice(string.ascii_letters) for x in range(length))


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

        if game_type == opening_screen.ONLINE_GAME_TYPE:
            move = starting_square + destination_square
            request = protocol.Request(username, protocol.REGULAR_MOVE, move).set_request_to_server()
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
        if team_got_turn is not my_team and game_type == opening_screen.BOT_GAME_TYPE:
            # bot turn.
            piece_moved = bot.move(team_doesnt_got_turn, team_got_turn, bot_depth)
            update_game_after_move(piece_moved, black_team, white_team)

        elif team_got_turn is not my_team and game_type == opening_screen.ONLINE_GAME_TYPE:
            game_status = my_socket.recv(1)
            logging.debug(f"game status: {game_status}")
            if game_status == protocol.ERROR_MESSAGE:
                logging.info("opponent player quit")
                screen.draw_winner(my_team)
                raise exceptions.GameEnd

            start_square = screen.squares[int(my_socket.recv(1))][int(my_socket.recv(1))]
            destination_square = screen.squares[int(my_socket.recv(1))][int(my_socket.recv(1))]

            piece_moved = start_square.current_piece
            piece_moved.move(destination_square)
            update_game_after_move(piece_moved, black_team, white_team)

        else:
            for event in pygame.event.get():
                piece_clicked = event_handler(event, piece_clicked, game_type)


def  quit_from_sever(client_socket: socket.socket):
    quit_request = protocol.Request(opening_screen.username, protocol.QUIT).set_request_to_server()
    opening_screen.my_socket.send(quit_request)
    client_socket.close()


def main():
    global my_socket
    global username
    logging.basicConfig(level=logging.INFO)

    try:
        # Get game data from user.
        # The return values is in the global vars of opening screen module.
        opening_screen.starting_screen()

    except exceptions.FinishStartingScreen:
        game_type = opening_screen.game_type
        game_length = opening_screen.game_length
        bot_depth = opening_screen.level
        is_player_white = opening_screen.is_white
        my_socket = opening_screen.my_socket
        username = opening_screen.username

    except exceptions.UserExitGame:
        if opening_screen.my_socket is not None:
            quit_from_sever(opening_screen.my_socket)
        return

    timer.set_game_length(game_length)
    screen.add_squares_to_board()
    white_team, black_team = get_teams_colors(team_got_turn, team_doesnt_got_turn)
    place_pieces(white_team, black_team)

    my_team = white_team if is_player_white else black_team

    screen.draw_eaten_pieces(white_team, black_team)

    # Start remote threads.
    scoreboard_thread = threading.Thread(target=redraw_scoreboard, daemon=True)
    scoreboard_thread.start()
    board_thread = threading.Thread(target=update_screen, daemon=True)
    board_thread.start()

    try:
        game_loop(game_type, my_team, bot_depth)

    except exceptions.UserExitGame:
        if my_socket is not None:
            # Already connected to server
            quit_from_sever(my_socket)
        return

    except exceptions.GameEnd:
        logging.info("Game ended.")
        timer.sleep(10)
        if my_socket is not None:
            # Already connected to server
            quit_from_sever(my_socket)
        return


if __name__ == '__main__':
    main()
