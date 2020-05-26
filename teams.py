import timer


class Team:
    def __init__(self, is_white_team):
        self.is_white_team = is_white_team
        self.pieces = []
        self.timer = timer.Timer()

