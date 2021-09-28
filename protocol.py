from dataclasses import dataclass

# Types of requests:
REGULAR_MOVE = "1"
GET_GAMES = "2"
CREATE_GAME = "3"
JOIN_GAME = "4"

# Status code:
ERROR_MESSAGE = "0".encode()
OK_MESSAGE = "1".encode()

SERVER_PORT = 5555


@dataclass
class Request:
    owner: str  # User who sent the request.
    type: str
    content: str = None

    def set_request_to_server(self):
        """
        :return
        final request to server would look like this:
        name-length_name_request-type content
        """

        request_string = str(len(self.owner)) + self.owner + self.type

        if self.type == REGULAR_MOVE or self.type == CREATE_GAME:
            # If request type is regular move, length is fixed.
            request_string += self.content

        elif self.content is not None:
            request_string += str(len(self.content)) + self.content

        print(f"Your final request is: {request_string}")
        return request_string.encode()


def set_server_regular_message(msg):
    return (str(len(msg)) + msg).encode()


def set_waiting_players_msg(waiting_players: dict):
    """
    :param waiting_players:
     list of players who waiting for other player to join their game.
    :return:
    A valid message including all games waiting for a player.
    The message form is that:
     players waiting count
     name length, name , is first player white (1/0), game length
    "43guy0105yuval1104anne054itay13".encode()
    """
    msg = str(len(waiting_players))
    for player in waiting_players.values():
        msg = msg + str(len(player.name)) + player.name + player.is_player_white + player.game_length
    return msg.encode()
