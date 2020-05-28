import timer


class Team:
    def __init__(self, is_white_team):
        self.is_white_team = is_white_team
        self.pieces = []
        self.timer = timer.Timer()
        self.score = 0

    def update_score(self):
        self.score = sum(piece.SCORE for piece in self.pieces)

