from dataclasses import dataclass


REGULAR_MOVE = "1"
GET_GAMES = "2"
CREATE_GAME = "3"
JOIN_GAME = "4"

ERROR_MESSAGE = "0".encode()
OK_MESSAGE = "1".encode()

SERVER_PORT = 5555


@dataclass
class Request:
    owner: str
    type: str
    content: str = None


def set_server_regular_message(msg):
    return (str(len(msg)) + msg).encode()


def set_waiting_players_msg(waiting_players: dict):
    """
    :param waiting_players:
     list of players who waiting for other player to join their game.
    :return:
    A valid message including all games waiting for a player.
    The message form is first players waiting count and than every name length and the name itself
    "43guy5yuval4anne4itay".encode()
    """
    msg = str(len(waiting_players))
    for player in waiting_players.values():
        msg = msg + str(len(player.name)) + player.name
    return msg.encode()


def set_request_to_server(request: Request):
    """
    msg should look like this:
    name-length_name_request-type_content
    """

    request_string = str(len(request.owner)) + request.owner + request.type

    if request.type == REGULAR_MOVE:
        request_string = request_string + request.content

    elif request.content is not None:
        request_string = request_string + str(len(request.content)) + request.content

    print(f"Your final request is: {request_string}")
    return request_string.encode()
