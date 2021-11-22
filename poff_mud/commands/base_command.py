class BaseCommand:
    name = "default command"
    keywords = []

    def __init__(self, gs, mud_server):
        self.gs = gs
        self.mud = mud_server

    def execute(self, player, params, command_used):
        pass

    @property
    def help(self):
        pass
