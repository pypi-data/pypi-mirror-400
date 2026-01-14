from ..search import things

from ..util.fonts import platform

Agent = things.Agent
UtilityBasedAgent = things.UtilityBasedAgent

class Hospital(things.Thing):
    def __repr__(self):
        return "🏥" if platform != "darwin" else "+"

class House(things.Thing):
    def __repr__(self):
        return "🏠" if platform != "darwin" else "^"

class Optimiser(things.Agent):
    def __repr__(self):
        return "📈"