import time


class RunOutOfTime(Exception):
    pass


def switch_timers(team_got_turn, team_doesnt_got_turn):
    team_got_turn.timer.resume()
    team_doesnt_got_turn.timer.pause()


def set_game_length(minutes):
    Timer.GAME_LENGTH = minutes*60


def sleep(sleep_time):
    time.sleep(sleep_time)


class Timer:
    # in seconds.
    GAME_LENGTH = 300

    def __init__(self):
        self.start_time = time.perf_counter()
        self.time_passed = 0
        self.time_paused = 0
        self.total_time_paused = 0
        self.is_pause = False

    def pause(self):
        if self.is_pause:
            raise TimeError("Timer can't pause because already paused")
        self.time_paused = time.perf_counter()
        self.is_pause = True

    def resume(self):
        if not self.is_pause:
            raise TimeError("Timer can't resume because timer isn't paused")
        self.is_pause = False
        self.total_time_paused += time.perf_counter() - self.time_paused

    def get_seconds(self):
        return int(self.time_passed)

    def get_seconds_left_to_last_minute(self):
        return int(60 - self.get_seconds() % 60)

    def get_minutes_left(self):
        return int(self.GAME_LENGTH / 60 - self.get_seconds() / 60)

    def update_timer(self):
        if self.is_pause:
            return
        self.time_passed = time.perf_counter() - self.start_time - self.total_time_paused
        self.check_out_of_time()

    def check_out_of_time(self):
        if self.get_seconds() >= self.GAME_LENGTH:
            raise RunOutOfTime
