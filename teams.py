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
        if self.pieces[0].is_in_white_team:
            return 'white team'
        return 'black team'

    def print_pieces(self):
        for piece in self.pieces:
            print(f'\n{piece}')

