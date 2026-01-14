"""THINGS.PY

Contains class definitions for some things
"""
from collections.abc import Callable, Collection, Iterable
from typing import override, Union

from ..util.fonts import platform

Action = Union[str, Iterable[str]]

class Thing:
    """The base class for all things"""
    @override
    def __repr__(self) -> str:
        return "❓" if platform != "darwin" else "?"

## Some physical things

class Obstacle(Thing):
    @override
    def __repr__(self) -> str:
        return "🚧" if platform != "darwin" else "X"


class Food(Thing):
    @override
    def __repr__(self) -> str:
        return "🍔" if platform != "darwin" else "f"


class Water(Thing):
    @override
    def __repr__(self) -> str:
        return "💧" if platform != "darwin" else "w"


class Animal(Thing):
    """ A generic animal thing """
    pass


class Dog(Animal):
    """If it looks like a dog and it barks like a dog ..."""
    @override
    def __repr__(self) -> str:
        return "🐶" if platform != "darwin" else "d"


## Some agent things

class Agent(Thing):
    """ Base class for all agents """
    pass


class RationalAgent(Agent):
    """ Base class for rational agent """
    def __init__(self, program:Callable) -> None:
        self.performance = 0
        # Check that program is callable function
        if program is None or not isinstance(program, Callable):
            raise ValueError("No valid program provided")
        self.program:Callable = program


class ModelBasedAgent(RationalAgent):
    """ Base class for model based agents 
    
    Requires a program method to be defined
        program(percepts:Collection[Thing]) -> Action
    """
    def __init__(self):
        """ Initialize the agent with its program """
        super().__init__(self.program)

    def program(self, percepts:Collection[Thing]) -> Action:
        """ The agent program 
        Given a collection of percepts, return an action
        """
        raise NotImplementedError

## State
class State(Thing):
    """ Base class for states """
    @override
    def __repr__(self) -> str:
        return self.__class__.__name__
    
class Bump(State):
    """ A bump state """
    pass