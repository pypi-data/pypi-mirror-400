from ..agent.things import Thing, Agent, RationalAgent, ModelBasedAgent, Action
from numpy import inf

from typing import Collection, override


class MazeRunner(Agent):
    """ Agent that runs mazes, visualised as 👾 """
    @override
    def __repr__(self) -> str:
        return "👾"


class GoalBasedAgent(ModelBasedAgent):
    """ Base class for goal based agents 
    
        Requires implemnentation of methods:
            `program(percepts:Collection[Thing]) -> Action`
            `at_goal() -> bool`
    """
    @property
    def at_goal(self) -> bool:
        """ checks if agent is at goal, needs overriding """
        raise NotImplementedError


class UtilityBasedAgent(GoalBasedAgent):
    """ Base class for utility based agents 
    
        Requires implemnentation of methods:
            `program(percepts:Collection[Thing]) -> Action`
            `at_goal() -> bool`
            `utility(action:Action) -> float`
    """
    def maximise_utility(self, actions: Collection[Action]) -> Action:
        """ calculates maximum utility from list of actions 
        
        :param actions: collection of possible actions
        :return: action with maximum utility
        """
        max_u = -inf  # negative infinity
        _flag = False  # safety check
        for action in actions:
            u = self.utility(action)
            if u > max_u:
                max_u = u
                output = action
                _flag = True
        if not _flag: raise ValueError("No valid actions provided")
        
        return output  # type: ignore


    def utility(self, action: Action) -> float:
        """ calculates utility of an action, needs overriding """
        raise NotImplementedError
