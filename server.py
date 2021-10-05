import socket
import select
import protocol
from dataclasses import dataclass
import logging

SERVER_IP = "0.0.0.0"
PLAYERS_PLAYING = dict()


@dataclass
class Message:
    data: bytes
    destination: socket.socket


class Player:
    def __init__(self, name: str, player_socket: socket.socket, game_length=5, is_player_white=0, opponent_player=None):
        self.name = name
        self.socket = player_socket
        self.opponent_player = opponent_player
        if opponent_player is None:
            self.game_length = game_length
            self.is_player_white = is_player_white
        else:
            self.game_length = opponent_player.game_length
            self.is_player_white = not is_player_white


def player_left(player_quit_name: str, waiting_players: dict, clients_socket: list):
    # If player isn't in waiting player or PLAYERS PLAYING his opponent already left.

    msg = None

    if player_quit_name in waiting_players.keys():
        waiting_players.pop(player_quit_name)

    elif player_quit_name in PLAYERS_PLAYING:
        player_quit = PLAYERS_PLAYING.pop(player_quit_name)
        opponent_player = PLAYERS_PLAYING.pop(player_quit.opponent_player.name)
        msg = [Message(protocol.ERROR_MESSAGE, opponent_player.socket)]

    return msg


def handle_request(request_sender_socket: socket.socket, waiting_players: dict, clients_socket: list):
    """
    :param clients_socket: list of all connected sockets. it would be change when player quit.
    :param request_sender_socket: The socket of the player who sent the request.
    :param waiting_players: Dict of players who waiting for opponent.
    this is dict and not list because server need to find player by name when clients asking to join game
    :return: A list with new messages would be send to clients.
    """
    request_sender_name_length = int(request_sender_socket.recv(1).decode())
    request_sender_name = request_sender_socket.recv(request_sender_name_length).decode()
    request_type = request_sender_socket.recv(1).decode()

    if request_type == protocol.QUIT:
        logging.info(f"{request_sender_name} left the server")
        clients_socket.remove(request_sender_socket)
        return player_left(request_sender_name, waiting_players,  clients_socket)

    if request_type == protocol.REGULAR_MOVE:
        start_square = request_sender_socket.recv(2).decode()
        destination_square = request_sender_socket.recv(2).decode()
        logging.info(f"{request_sender_name} moved {start_square} to {destination_square}")

        opponent_player = PLAYERS_PLAYING[request_sender_name].opponent_player
        return [Message((protocol.OK_MESSAGE.decode() + start_square + destination_square).encode(), opponent_player.socket)]

    elif request_type == protocol.CREATE_GAME:
        # message content including is player white team and game length.
        is_player_white = request_sender_socket.recv(1).decode()  # True or false
        # Game length should be always 2 digits. zero fill.
        game_length = request_sender_socket.recv(2).decode()
        first_player = Player(request_sender_name, request_sender_socket, game_length, is_player_white)
        waiting_players[request_sender_name] = first_player
        logging.info(f"{first_player.name} created game: length {first_player.game_length} he is white: {first_player.is_player_white}")

    elif request_type == protocol.GET_GAMES:
        logging.info(f"{request_sender_name} want to see all players waiting for opponent.")
        logging.debug(f"players waiting for opponent: {waiting_players}")
        return [Message(protocol.set_waiting_players_msg(waiting_players), request_sender_socket)]

    elif request_type == protocol.JOIN_GAME:
        other_player_length = int(request_sender_socket.recv(1).decode())
        other_player_name = request_sender_socket.recv(other_player_length).decode()

        if other_player_name in waiting_players.keys():
            other_player = waiting_players.pop(other_player_name)
            # player_join is the player who send the request.
            player_join = Player(request_sender_name, request_sender_socket, opponent_player=other_player)
            PLAYERS_PLAYING[other_player_name] = other_player
            PLAYERS_PLAYING[request_sender_name] = player_join

            other_player.opponent_player = player_join
            # Return two messages:
            # first approval that the request has accomplished
            # second the name of the player who joined to the player who waiting.
            logging.info(f"{request_sender_name} joined {other_player_name} game")
            return [Message(protocol.OK_MESSAGE, request_sender_socket),
                    Message(protocol.set_server_regular_message(request_sender_name), other_player.socket)]

        else:
            logging.error(f"{request_sender_name} want to connect to a doesn't exist game.")
            return [Message(protocol.ERROR_MESSAGE, request_sender_socket)]


def start_server() -> socket.socket:
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((SERVER_IP, protocol.SERVER_PORT))
    server_socket.listen()
    return server_socket


def main():
    logging.basicConfig(level=logging.INFO)
    server_socket = start_server()
    logging.info("Server is up")
    clients_sockets = list()
    # Players opened games and waiting for other player.
    waiting_players = dict()
    ready_messages = list()
    while True:
        rlist, wlist, xlist = select.select([server_socket] + clients_sockets, [server_socket] + clients_sockets, [])

        # New client
        if server_socket in rlist:
            new_client_socket, new_client_address = server_socket.accept()
            clients_sockets.append(new_client_socket)
            logging.info("new client arrived")
            rlist.remove(server_socket)

        # New data
        for request_sender_socket in rlist:
            msg = handle_request(request_sender_socket, waiting_players, clients_sockets)

            if msg is not None:
                ready_messages.extend(msg)

        # send all messages to clients listening to server.
        for msg in ready_messages:
            if msg.destination in wlist:
                msg.destination.send(msg.data)
                ready_messages.remove(msg)


if __name__ == '__main__':
    main()
