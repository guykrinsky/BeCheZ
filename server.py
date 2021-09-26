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
    def __init__(self, name: str, player_socket: socket.socket, opponent_player=None):
        self.name = name
        self.socket = player_socket
        self.opponent_player = opponent_player


@dataclass
class Game:
    # When creating game you don't know who is your opponent player.
    player1: Player
    player2: Player = None


def handle_request(request_sender_socket: socket.socket, waiting_players: dict):
    """
    :param request_sender_socket: The socket of the player who sent the request.
    :param waiting_players: List of players who waiting for opponent.
    :return: A list with new messages would be send to clients.
    """
    request_sender_name_length = int(request_sender_socket.recv(1).decode())
    request_sender_name = request_sender_socket.recv(request_sender_name_length).decode()
    request_type = request_sender_socket.recv(1).decode()

    if request_type == protocol.REGULAR_MOVE:
        start_square = request_sender_socket.recv(2).decode()
        destination_square = request_sender_socket.recv(2).decode()
        print(f"{request_sender_name} moved {start_square}"
              f" to {destination_square}")
        opponent_player = PLAYERS_PLAYING[request_sender_name].opponent_player
        return [Message((start_square + destination_square).encode(), opponent_player.socket)]

    elif request_type == protocol.CREATE_GAME:
        first_player = Player(request_sender_name, request_sender_socket)
        waiting_players[request_sender_name] = first_player
        print(f"{first_player.name} waiting for player to join his game")

    elif request_type == protocol.GET_GAMES:
        print(f"{request_sender_name} want to see all the games. The games:\n {waiting_players}")
        return [Message(protocol.set_waiting_players_msg(waiting_players), request_sender_socket)]

    elif request_type == protocol.JOIN_GAME:
        other_player_length = int(request_sender_socket.recv(1).decode())
        other_player_name = request_sender_socket.recv(other_player_length).decode()

        if other_player_name in waiting_players.keys():
            other_player = waiting_players.pop(other_player_name)
            # player_join is the player who send the request.
            player_join = Player(request_sender_name, request_sender_socket, other_player)
            PLAYERS_PLAYING[other_player_name] = other_player
            PLAYERS_PLAYING[request_sender_name] = player_join

            other_player.opponent_player = player_join
            # Return two messages:
            # first approval that the request has accomplished
            # second the name of the player who joined to the player who waiting.
            return [Message(protocol.OK_MESSAGE, request_sender_socket),
                    Message(protocol.set_server_regular_message(request_sender_name), other_player.socket)]

        else:
            # ERROR
            return [Message(protocol.ERROR_MESSAGE, request_sender_socket)]


def start_server() -> socket.socket:
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((SERVER_IP, protocol.SERVER_PORT))
    server_socket.listen()
    return server_socket


def main():
    server_socket = start_server()
    print("Server is up")
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
            print("new client arrived")
            rlist.remove(server_socket)

        # New data
        for request_sender_socket in rlist:
            msg = handle_request(request_sender_socket, waiting_players)

            if msg is not None:
                ready_messages.extend(msg)

        # send all messages to clients listening to server.
        for msg in ready_messages:
            if msg.destination in wlist:
                msg.destination.send(msg.data)
                ready_messages.remove(msg)


if __name__ == '__main__':
    main()
