"""ENVIRONMENT.PY
    This contains code for agent environments and simulations
"""
import warnings
import math
import random
from collections.abc import Collection, Iterable
from typing import Union, TypeVar, override

with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    import pygame

from ..engine import App
from ..util.colours import COLOR_BLACK, COLOR_WHITE
from ..util.fonts import _get_symbolic_font_unsafe
from .things import Thing, Agent, Obstacle, Action

SYMBOL_FONT_NAME = _get_symbolic_font_unsafe()

T = TypeVar("T")
GenericLocation = T | tuple[T] | None
XYLocation = tuple[int, int]

class BaseEnvironment:
    """ Base Environment
            Adapted from AIMI code
    """
    def __repr__(self) -> str:
        """ Base string representation """
        return self.__class__.__name__
    
    @property
    def is_done(self) -> bool:
        """ Property indicating completion of simulation, needs overriding
        """
        raise NotImplementedError
    
    def step(self) -> None:
        """ Executes incremental step in discrete environment, needs overriding
        """
        raise NotImplementedError
    
    def run(self, steps:int = 100, pause_for_user:bool = True) -> None:
        """ Executes the simulation until either environment is done, or total
        steps exceeds limit
        
        :param          steps: max. # of iterations in simulation, default 100
        :param pause_for_user: require user input before beginning, default True
        """
        if pause_for_user:
            input("Press enter to start simulation")

        print(f"{self}: Running for {steps} iterations.")

        for i in range(steps):
            if self.is_done:  # print terination message and exit
                print(f"{self}: Simulation complete after {i} of {steps} iterations.")
                return
            self.step() # else iterate one step
        print(  # if loop completes, print max steps reached
            f"{self}: Simulation complete after {steps} of {steps} iterations.")


class Environment(BaseEnvironment):
    """ An Environment is a BaseEnvironment that has Things and Agents
    """
    def __init__(self):
        """ Initialises set of things and agents """
        self.things = set()  # all things in environment
        self.agents = set()  # all agents in environment

    @property
    def is_done(self) -> bool:
        """ Is considered done if there are no agents in environment """
        return len(self.agents) == 0  # cannot simulate with no agents


    def step(self) -> None:
        """ Executes percept, program and action step for each agent. """
        if not self.is_done:
            actions = {
                agent: agent.program(self.percept(agent))
                    for agent in self.agents}  # dictionary of actions by agents
            
            for agent, action in actions.items():
                # iterate through each action and allow agent to execute it
                self.execute_action(agent, action) 

            if self.is_done:
                print(f"{self}: Task environment complete. No further actions.")


    def percept(self, agent:Agent) -> Collection[Thing]:
        """ Returns the collection, e.g. set or list, of Things that an Agent 
        can perceive in the current state.
        
        :param        agent: the agent that is percieving
        """
        raise NotImplementedError


    def execute_action(self, agent:Agent, action:Action) -> None:
        """ For a given agent and action, performs execution
         
        :param        agent: the agent that is executing an action
        :param       action: the action statement to be executed by the agent
        """
        raise NotImplementedError


    def add_thing(self, thing:Thing, location:GenericLocation = None) -> None:
        """ Adds a thing to the environment at a given location (if applicable).
        
        :param        thing: the Thing (or Thing subclass) to be added
        :param     location: the location to add the Thing at (if applicable)
        """
        if isinstance(thing, type):  # if a class is given, instantiate it
            if issubclass(thing, Thing):
                thing = thing()
            else:  # not a Thing
                print(f"{self}: Tried to add {thing} but its not a Thing.")
                return

        if not isinstance(thing, Thing):  # not a Thing
            print(f"{self}: Tried to add {thing} but its not a Thing.")
            return
    
        if thing in self.things:  # prevent duplicate addition
            print(f"{self}: Tried and failed to add duplicate {thing}.")
            return
        
        if location:  # if a location is specified, set it
            thing.location = location  # set location of thing
            print(f"{self}: Adding {thing} at {location}")
            self.things.add(thing)  # add thing to environment

        if isinstance(thing, Agent):  # if thing is an agent, add to agents list
            print(f"{self}: Adding {thing} to list of agents.")
            self.agents.add(thing)
    

    def add_agent(self, agent:Agent, location:GenericLocation=None) -> None:
        """ Adds an agent to the environment at a given location 
        (if applicable).

        Wrapper for add_thing, specifically for agents.
        
        :param        agent: the Agent (or Agent subclass) to be added
        :param     location: the location to add the Agent at (if applicable)
        """
        if not isinstance(agent, Agent):  # not an Agent
            print(f"{self}: {agent} is not an Agent. Adding as Thing instead.")
        self.add_thing(agent, location)  # delegate to add_thing


    def delete_thing(self, thing:Thing) -> None:
        """ Removes a thing from the environment.
        
        :param        thing: the Thing (or Thing subclass) to be removed
        """
        if thing not in self.things: return  # thing not in environment

        self.things.remove(thing)  # remove thing from environment
        if isinstance(thing, Agent):  # if thing is an agent,
            self.agents.remove(thing)   # remove from agents list too


    def things_at(self, location:GenericLocation) -> list[Thing]:
        """ Returns list of things at a given location. 
        
        :param     location: the location to get Things at
        """
        return [thing for thing in self.things if thing.location == location]
    

    def __call__(self, location:GenericLocation) -> list[Thing]:
        """ Allows environment to be called as function to get things at location.
        
        Wrapper for things_at.

        :param     location: the location to get Things at
        """
        return self.things_at(location)


class XYEnvironment(Environment):
    """ A 2D grid environment for agents and things """
    DEFAULT_BG = COLOR_BLACK  # default background color

    def __init__(self, width:int = 10, height:int = 10) -> None:
        """ Initialises environment of given width and height
        
        :param        width: width of environment grid
        :param       height: height of environment grid
        """
        if not isinstance(width, int) or not isinstance(height, int):
            raise TypeError(f"{self}: dimensions must be integers")
        
        if width < 1 or height < 1:
            raise ValueError(f"{self}: dimensions must be greater than zero")
        
        super().__init__()  # initialise base environment

        if not hasattr(self, 'color'):  # set default color if not overridden
            self.color = self.DEFAULT_BG
        
        self.width, self.height = width, height  # set dimensions
        self.observers = []  # observers of environment changes
        self.bumped = set()  # agents that have bumped into obstacles
        self.x_start_offset = self.x_end_offset = 0  # offsets for walls
        self.y_start_offset = self.y_end_offset = 0  # offsets for walls
    

    @property
    def x_start(self) -> int:
        """ Starting x coordinate considering walls """
        return 0 + self.x_start_offset
    

    @property
    def x_end(self) -> int:
        """ Ending x coordinate considering walls """
        return self.width - self.x_end_offset
    

    @property
    def y_start(self) -> int:
        """ Starting y coordinate considering walls """
        return 0 + self.y_start_offset
    

    @property
    def y_end(self) -> int:
        """ Ending y coordinate considering walls """
        return self.height - self.y_end_offset


    def things_near(self, location:XYLocation, radius:int|float = 1) -> Collection[Thing]:
        """ Returns list of things near a given location within a certain radius.
        
        :param     location: the location to get Things near
        :param       radius: the radius around location to search
        """
        raise NotImplementedError
    

    def _add_wall(self, location:XYLocation) -> None:
        """ Adds a wall at the given location if no obstacle is present.
        
        :param     location: the location to add wall at
        """
        class Wall(Obstacle): pass  # simple wall class

        if all(not isinstance(obj, Obstacle)  # only add wall if no obstacle
               for obj in self.things_at(location)):
            self.add_thing(Wall(), location)  # add wall to environment


    def add_walls(self) -> None:
        """ Adds walls around the perimeter of the environment """
        if self.width > 2:  # add left and right walls
            for y in range(self.height):
                self._add_wall((0, y))
                if self.width > 1: self._add_wall((self.width-1, y))

        if self.height > 2:  # add top and bottom walls
            for x in range(self.width):
                self._add_wall((x, 0))
                if self.height > 1: self._add_wall((x, self.height - 1))
            self.y_start_offset += 1  # account for walls
            self.y_end_offset += 1  # account for walls

        if self.width > 2:
            self.x_start_offset += 1  # account for walls
            self.x_end_offset += 1  # account for walls
    

    def is_valid(self, location:XYLocation) -> bool:
        """ Checks if a location is valid in the environment
        
        :param     location: the location to validate
        """
        if not isinstance(location, Iterable): return False  # must be iterable
        if len(location) != 2:  return False  # must be length 2
        if any(map(lambda x: not isinstance(x,int), location)): return False  # must be ints
        return True
    
    def is_inbounds(self, location):
        if not self.is_valid(location): return False
        x,y = location
        if not (x >= self.x_start and x < self.x_end): return False
        if not (y >= self.y_start and y < self.y_end): return False
        return True

    @override
    def add_thing(self, thing:Thing, location:XYLocation) -> None:
        if location is None:  # default to starting location
            location = (self.x_start, self.y_start)
        elif self.is_inbounds(location):  # check location validity
            location = tuple(location)  # force tuple to make hashable
        else:  # invalid location
            print(f"Tried and failed to add {thing} to environment")
            return
        
        if isinstance(self, Agent):  # if thing is an agent
            thing.bump = False  # give capacity to be bumped
        super().add_thing(thing, location)  # delegate to base method

        assert thing in self.things_at(location)  # sanity check


    def add_thing_randomly(self, thing:Thing):
        """ Adds a thing to a random location in the environment
        
        :param        thing: the Thing (or Thing subclass) to be added
        """
        x = random.randint(self.x_start, self.x_end-1)  # random x coord
        y = random.randint(self.y_start, self.y_end-1)  # random y coord
        self.add_thing(thing, (x,y))  # delegate to add_thing


class GraphicEnvironment(XYEnvironment):
    """ A graphical 2D grid environment for agents and things """
    @override
    def run(self, graphical=True, steps=100, **kwargs) -> None:
        """ Executes the simulation in graphical or base mode.
        
        :param       graphical: whether to run graphical version
        :param           steps: max. # of iterations in simulation, default 100
        :param        **kwargs: additional arguments for environment base class
        """
        if graphical:  # run graphical version
            EnvironmentApp(self, steps=steps, name=f"{self}", **kwargs).run()
        else:  # run base version
            super().run(steps=steps, **kwargs)


class EnvironmentApp(App):
    """EnvironmentApp
            Graphical version of an XYEnvironment 
    """
    # size = width, height = 600, 400  # uncomment to override
    def __init__(self,
                 environment:XYEnvironment|None = None, 
                 steps:int = 100, 
                 **kwargs) -> None:
        """ Initialises graphical environment app
        
        :param   environment: the XYEnvironment to visualise
        :param         steps: max. # of iterations in simulation, default 100
        :param      **kwargs: additional arguments for App base class
        """
        if environment is None:  # default to 12x8 XYEnvironment
            print(f"{self}: No environment specified, using default")
            environment = XYEnvironment(12, 8)
        if not isinstance(environment, XYEnvironment):  # check type
            raise TypeError(f"{self}: environment must be XYEnvironment")

        self.environment = environment
        self._fit_to_environment()  # fit window aspect to environment
        super().__init__(**kwargs)  # initialise base App class

        # font for rendering things
        self.thing_font = pygame.font.SysFont(SYMBOL_FONT_NAME, 28)

        self.counter = -1  # start at -1 to allow initial render
        self.steps = steps  # max. steps in simulation
        self._flag = True  # flag for completion message
        
    
    def _fit_to_environment(self) -> None:
        """ Fit width and height ratios to match environment """
        # determine whether environment is wider than tall
        _wider_than_tall = self.environment.width > self.environment.height

        if _wider_than_tall: 
            xy_ratio = self.environment.width/self.environment.height
            a, b = self.height, self.width
        else:
            xy_ratio = self.environment.height/self.environment.width
            b, a = self.height, self.width

        a = b // xy_ratio  # adjust dimensions
        b = int(a*xy_ratio)

        self.height, self.width = (a,b) if _wider_than_tall else (b,a)
        self.size = self.width, self.height  # set size attribute


    @override
    def update(self) -> None:
        """ Main process loop 
                Steps the environment simulation
        """
        if self.counter < 0:  # initial render only
            self.counter += 1
            return
        if self.counter < self.steps and not self.environment.is_done:
            self.environment.step()
            self.counter += 1
        elif self._flag:  # print completion message once
            print(f"{self.environment}: Simulation complete after {self.counter} of {self.steps} iterations.")
            self._flag = False


    @override
    def render(self) -> None:
        """ Main render loop 
                Renders the environment grid and things
        """
        self.screen.fill(self.environment.color)  # write background color
        self.render_grid()  # render grid
        self.render_things()  # render things


    def render_grid(self) -> None:
        """ Render environment grid """
        nx,ny = self.environment.width, self.environment.height
        self.tile_size = self.width // nx  # size of each tile
        tile_origin = (0, 0)

        tiles:list[list[pygame.Rect]] = []  # 2D list of tile rects

        for i in range(ny):  # for each row
            row = [] 
            for j in range(nx):  # for each column
                tileRect = pygame.Rect(  # define tile rectangle
                    tile_origin[0] + j * self.tile_size,
                    tile_origin[1] + i * self.tile_size,
                    self.tile_size, self.tile_size)
                # draw tile border
                pygame.draw.rect(self.screen, COLOR_WHITE, tileRect, 1)
                # add tile render object to row
                row.append(tileRect)
            tiles.append(row)  # add row to tiles

        self.tiles = tiles  # store tiles for later use


    def render_things(self) -> None:
        """ Render things in environment """
        locations:dict = {}  # map of locations to things

        # build location map
        for thing in self.environment.things:
            if thing.location in locations:
                locations[thing.location].append(thing)
            else:
                locations[thing.location] = [thing]

        # render things at each location
        for location, things in locations.items():
            n_things = len(things)
            if n_things > 1:  # multiple things, pick one at random per render
                thing = things[random.randint(0,n_things-1)]
            elif n_things == 1:  # single thing
                thing = things[0]
            else:  # no things to render at this location
                continue
            # determine render location
            renderLoc = self.tiles[location[1]][location[0]].center
            thingRender = self.thing_font.render(str(thing), True, COLOR_WHITE)
            thingRect = thingRender.get_rect()
            thingRect.center = renderLoc
            # blit thing to screen
            self.screen.blit(thingRender, thingRect)