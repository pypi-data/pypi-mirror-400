from numpy import inf as infinity
from ..optimisation.things import *
from ..agent.environment import GraphicEnvironment
from ..search.util import manhattan
import random

PRESET_STATES = {
    "empty": None,
    '0': {
        "hospitals": [(2, 4)],
        "houses": [(2,1),(1,3),(8,0),(6,4)],
        "height": 5,
        "width": 10,
    },
    '1': {
        "hospitals": [(4,0), (9,3)],
        "houses": [(2,1),(1,3),(8,0),(6,4)],
        "height": 5, 
        "width": 10},
    '2': {
        "houses": [(2,1),(1,3),(8,0),(6,4)],
        "height": 5, 
        "width": 10},
    '3': {
        "houses": [(1, 2), (5, 1), (12, 2), (13, 2), (4, 0), (8, 5), (15, 1), (12, 4), (1, 7), (6, 5), (15, 3), (0, 1), (0, 0), (10, 5), (5, 3), (3, 6), (6, 3), (0, 7)],
        "hospitals": [(11,6), (5,2), (4,1)],
        "height": 8,
        "width": 16},
    '4': {
        "houses": [(1, 14), (17, 6), (2, 4), (4, 17), (9, 4), (3, 14), (8, 1), (17, 15), (6, 10), (9, 7), (3, 19), (10, 11), (8, 18), (0, 15), (4, 15), (4, 7), (16, 11), (5, 8), (13, 12), (8, 13), (17, 3), (1, 13), (11, 9), (10, 15), (2, 3), (7, 10), (5, 1), (14, 19), (14, 7), (18, 6), (8, 3), (11, 2), (5, 7), (11, 8), (18, 16), (12, 13), (5, 2), (18, 14)],
        "hospitals": [(8,0), (0, 12), (17, 12), (3,5)],
        "height": 20,
        "width": 20},
    '5': {
        "houses": [ (26, 22), (8, 13), (5, 29), (19, 15), (27, 13), (17, 24), (15, 6), (0, 11), (0, 26), (1, 22), (0, 14), (13, 17), (4, 10), (27, 10), (28, 28), (26, 29), (17, 28), (10, 18), (3, 8), (25, 6), (16, 28), (1, 15), (10, 23), (10, 6), (26, 15), (15, 12), (27, 12), (13, 1), (15, 10), (9, 29), (22, 9), (17, 29), (21, 24), (12, 17), (8, 15), (19, 13), (1, 26), (12, 18), (20, 3), (15, 18), (16, 27), (25, 18), (4, 17), (21, 13), (6, 29), (10, 25), (15, 23), (18, 12), (8, 20), (11, 18), (10, 19), (9, 26), (9, 23), (17, 1), (24, 10), (11, 4), (3, 3), (8, 12), (22, 10), (12, 21), (19, 28), (21, 29), (10, 17), (27, 1), (26, 9), (9, 14), (21, 15), (29, 18), (20, 15), (13, 12), (24, 17), (7, 20), (28, 4), (19, 17), (1, 8), (26, 26), (11, 28), (2, 1)],
        "hospitals": [(15, 5), (6, 1), (11, 3), (27, 22), (8, 14)],
        "height": 30,
        "width": 30},
}



class HospitalOptimiser(Optimiser, UtilityBasedAgent):
    def explore(self, state):
        if not state: return
        print(f"{self}: exploring state\n    {state['hospitals']}")
        for hospital, loc in state["hospitals"].items():
            hospital.location = loc

    def utility(self, state):
        """ calculate distance from each hospital to houses """
        obj = 0
        houses, hospitals = state["houses"], state["hospitals"]
        for house in houses:
            dist_to_nearest = infinity   # very big
            for hospital in hospitals:
                dist = manhattan(
                    houses[house],
                    hospitals[hospital])
                if dist < dist_to_nearest:
                    dist_to_nearest = dist
            obj += dist_to_nearest
        return -obj


class HospitalPlacement(GraphicEnvironment):
    def __init__(self, init=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.initialise_state(init)

    @property
    def state(self):
        return {
            "hospitals": {
                thing: thing.location
                    for thing in self.things
                        if isinstance(thing, Hospital)},
            "houses": {
                thing: thing.location
                    for thing in self.things
                        if isinstance(thing, House)},
            "bounds": {
                "xmin": 0, "xmax": self.width-1,
                "ymin": 0, "ymax": self.height-1}
        }

    @property
    def neighbours(self):
        neighbours = []
        for i, hospital in enumerate(self.state["hospitals"]):
            location = hospital.location
            for x,y in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                proposal = location[0] + x, location[1] + y
                if self.is_inbounds(proposal):
                    candidate = self.state.copy()
                    candidate["hospitals"][hospital] = proposal
                    neighbours.append(candidate)
        return neighbours

    def is_inbounds(self, location):
        if not super().is_inbounds(location):
            return False
        return len(self.things_at(location)) == 0

    def add_agent(self, agent:Agent):
        if not isinstance(agent, Agent):
            raise TypeError(f"{self}: {agent} is not an Agent.")
        self.agents.add(agent)

    def add_thing_randomly(self, thing):
        x = random.randint(self.x_start, self.x_end-1)
        y = random.randint(self.y_start, self.y_end-1)
        lim, count = 10, 0
        while not self.is_inbounds((x,y)):
            count += 1
            if count > lim:
                print(f"Tried and failed to add {thing} to environment")
                return     
            x = random.randint(self.x_start, self.x_end-1)
            y = random.randint(self.y_start, self.y_end-1)
        self.add_thing(thing, (x,y))


    def initialise_state(self, state_dict):
        if state_dict is None:
            return
        if "height" in state_dict:
            self.height = state_dict["height"]
        if "width" in state_dict:
            self.width = state_dict["width"]
        self.size = self.width, self.height
        if "hospitals" in state_dict:
            for loc in state_dict["hospitals"]:
                self.add_thing(Hospital(), location=loc)
        for loc in state_dict["houses"]:
            self.add_thing(House(), location=loc)
        

    @property
    def is_done(self):
        if len(self.agents) == 0: return True  # if there are no agents
        return hasattr(self, "success") and self.success

    def percept(self, agent):
        return self.state, self.neighbours

    def execute_action(self, agent, action):
        """ Execute an action """
        command, state = action
        match command:
            case "done":
                if state:
                    agent.explore(state)
                self.success = True
            case "explore":
                agent.explore(state)