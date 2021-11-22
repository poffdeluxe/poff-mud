class GameState:
    def __init__(self):
        self.rooms = {}
        self.players = {}
        self.timer_manager = None

    def get_players_in_room(self, room_id):
        result_players = []

        # go through every player in the game
        for pid, pl in self.players.items():
            # if they're in the same room as the player
            if self.players[pid]["room"] == room_id:
                result_players.append(self.players[pid])

        return result_players
