import timer


class Team:
    def __init__(self):
        self.pieces = []
        self.timer = timer.Timer()
        self.score = 0

    def update_score(self):
        self.score = sum(piece.score for piece in self.pieces if not piece.is_eaten)

