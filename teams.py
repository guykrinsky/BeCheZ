import timer


class Team:
    def __init__(self, is_white_team):
        self.pieces = []
        self.timer = timer.Timer()
        self.score = 0
        self.is_white_team = is_white_team

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

