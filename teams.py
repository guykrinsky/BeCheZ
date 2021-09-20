import timer


def get_teams_colors(team_got_turn, team_doesnt_got_turn):
    # Return white team and black team.
    white_team = team_got_turn if team_got_turn.is_white_team else team_doesnt_got_turn
    black_team = team_got_turn if not team_got_turn.is_white_team else team_doesnt_got_turn
    return white_team, black_team


class Team:
    def __init__(self, is_white_team):
        self.pieces = []
        self.timer = timer.Timer()
        self.score = 0
        self.is_white_team = is_white_team
        self.eaten_pieces = []

    def update_score(self):
        self.score = sum(piece.score for piece in self.pieces if not piece.is_eaten)

    def __str__(self):
        return 'white team' if self.is_white_team else 'black team'

    def print_pieces(self):
        for piece in self.pieces:
            print(f'\n{piece}')


def get_score_difference(white_team: Team, black_team: Team):
    white_team.update_score()
    black_team.update_score()
    score_difference = white_team.score - black_team.score
    return score_difference

