from collections.abc import Iterable
import warnings
from matplotlib import pyplot as plt
from collections import deque

with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    import pygame

from ..engine import App
from ..util.colours import (
    COLOR_BLACK, COLOR_WHITE,
    COLOR_RED, COLOR_RED_DARK, COLOR_RED_LIGHT,
    COLOR_YELLOW, COLOR_BLUE, COLOR_GREEN_LIGHT
)

from .graph import Node, Graph, GraphEnvironment
from .things import Thing, Agent

PRESET_MAZES = {
    0: [" xxx o",
        "    x ",
        "x x   ",
        "  x xx"],
    1: [" xx  o",
        "    x ",
        "x x   ",
        "    xx"],
    2: ["           o",
        "x xxxxxxxxx ",
        "x x       x ",
        "x x xxxxx x ",
        "  x x     x ",
        "x   x xx xx ",
        "xxx x  xxxx ",
        "    xx      "],
    4: ["xxx                 xxxxxxxxx",
        "x   xxxxxxxxxxxxxxxxxxx   x x",
        "x xxxx                x x x x",
        "x xxxxxxxxxxxxxxxxxxx x x x x",
        "x                     x x x x",
        "xxxxxxxxxxxxxxxxxxxxx x x x x",
        "x   xx                x x x x",
        "x x xx xxx xx xxxxxxxxx x x x",
        "x x    x   xxox         x x x",
        "x x xx xxxxxxxxxxxxxxxx x x x",
        "xxx xx             xxxx x x x",
        "xxx xxxxxxxxxxxxxx xx x x x x",
        "xxx             xx    x x x x",
        "xxxxxx xxxxxxxx xxxxxxx x x x",
        "xxxxxx xxxx             x   x",
        "       xxxxxxxxxxxxxxxxxxxxxx"]
}

PRESET_STARTS = {
    0: (3, 0),
    1: (3, 0),
    2: (7, 0),
    4: (15, 0)
}

class MazeTile(Node):
    def __init__(self, passable:bool):
        super().__init__()
        self.is_passable = passable
        self.is_goal = False
        self.visited = False

    def __repr__(self):
        repr =  "⬜" if self.is_passable else "⬛"
        if hasattr(self, "location"):
            repr += str(self.location)
        return repr


class Maze(Graph):
    def __init__(self, template=None, size=None):
        super().__init__()
        if template is not None:
            if not self._is_valid_template(template):
                raise ValueError(f"{self}: template provided is not valid")
            self.template = template
            self.height, self.width = len(template), len(template[0])
            self.size = self.width, self.height
            self._generate_from_template()

    def __repr__(self):
        return "ꡙ‍"

    def _is_valid_template(self, template):
        def valid(row, size):
            return False if len(row) != size else not any(
                c not in (' ','o','x') for c in row)

        if isinstance(template, Iterable):
            if all(isinstance(row, Iterable) for row in template):
                width = len(template[0])
                return all(valid(row,width) for row in template)
        return False

    def _generate_from_template(self):
        self.grid = []
        w,h = self.width, self.height
        print(f"{self}: generating {w}x{h} maze from template")
        for i, row in enumerate(self.template):
            grid_row = []
            for j, tile in enumerate(row):
                node = MazeTile(tile != "x")  # True is passable
                if tile == "o":
                    node.is_goal = True
                node.location = (i, j)
                grid_row.append(node)
                if i > 0:
                    node.add_neighbour(self.grid[i-1][j])
                if j > 0:
                    node.add_neighbour(grid_row[j-1])
            self.grid.append(grid_row)
        self.add_node(self.grid[0][0])  # cascade adding nodes


    def plot_nodes(self, init=None):
        labels = {self.grid[i][j]: f"({i},{j})" 
                    for i in range(self.width)
                        for j in range(self.height)}
        condition = lambda node: node.is_passable
        return super().plot_nodes(init=init, labels=labels, condition=condition)


class MazeEnvironment(GraphEnvironment):
    def __init__(self, maze, *args, **kwargs):
        if not isinstance(maze, Maze):
            raise TypeError(f"{self}: maze must be valid Maze")
        super().__init__(maze, *args, **kwargs)
        self.size = self.width, self.height = maze.size
        self.success = False  # maze is solved
    def __repr__(self):
        return self.maze.__repr__()

    @property
    def maze(self):
        return self.graph

    @property
    def grid(self):
        return self.maze.grid

    @property
    def is_done(self):
        if len(self.agents) == 0: return True
        return self.success

    @property
    def goal(self):
        goal = {node for node in self.maze.nodes if node.is_goal}
        if len(goal) == 1:
            goal = next(iter(goal))
        return goal

    def show_graph(self, *args, **kwargs):
        return self.show(*args, **kwargs)

    def percept(self, agent):
        node = agent.location
        return node.neighbours

    def execute_action(self, agent, action):
        """ """
        command, node = action
        if command == "move":
            if node in self.maze:
                self.success = agent.move_to(node)
    
    def run(self, track_agent=False, *args, **kwargs):
        super().run(10000, *args, **kwargs)

    @classmethod
    def from_template(MazeEnvironment, template):
        maze = Maze(template)
        return MazeEnvironment(maze)


class GraphicMaze(MazeEnvironment):
    def run(self, graphical=True, lps=2, *args, **kwargs):
        if graphical:
            MazeApp(self, *args, name=f"{self}", lps=lps, **kwargs).run()
        else:
            super().run(*args, **kwargs)

  
class MazeApp(App):
    """ MazeApp
            Graphical version of Maze """
    def __init__(self, environment:MazeEnvironment=None, track_agent=False,**kwargs):
        if environment is None:
            print(f"{self}: building new MazeEnvironment from template")
            environment = MazeEnvironment.from_template(PRESET_MAZES[0])
        if not isinstance(environment, MazeEnvironment):
            raise TypeError(f"{self}: environment must be MazeEnvironment")
        
        self.environment = environment
        self._fit_to_environment()
        super().__init__(**kwargs)

        nx = self.environment.width
        fs = min(35, max(10, self.width//nx))
        self.thing_font = pygame.font.SysFont("segoe-ui-symbol", fs)
        self.counter = -1
        self._flag = True
        self.track = track_agent

    def _fit_to_environment(self):
        """ Fit width and height ratios to match environment """
        _flag = self.environment.width > self.environment.height
        if _flag:
            xy_ratio = self.environment.width/self.environment.height
            a, b = self.height, self.width
        else:
            xy_ratio = self.environment.height/self.environment.width
            b, a = self.height, self.width

        a = b // xy_ratio
        b = int(a*xy_ratio)
        # a = int(a)

        self.height, self.width = (a,b) if _flag else (b,a)
        self.size = self.width, self.height


    def update(self):
        if self.counter < 0:
            self.counter += 1
            return
        if not self.environment.is_done:
            self.environment.step()
            self.counter += 1
        elif self._flag:
            print(f"{self.environment}: Maze complete after {self.counter} iterations.")
            self._flag = False

    def render(self):
        # self.screen.fill(self.environment.color)
        self.render_grid()
        self.render_things()

    def render_grid(self):
        nx,ny = self.environment.width, self.environment.height
        self.tile_size = self.width / nx
        tile_origin = (0,0)
        grid = self.environment.grid
        tiles = []
        for i in range(ny):
            i_ = i# ny - i - 1
            
            row = []
            for j in range(nx):
                tileRect = pygame.Rect(
                    tile_origin[0] + j * self.tile_size,
                    tile_origin[1] + i * self.tile_size,
                    self.tile_size, self.tile_size)
                
                node = grid[i_][j]
                if node.is_goal:
                    color = COLOR_RED
                elif self.track and hasattr(node, "visited") and node.visited:
                    color = COLOR_GREEN_LIGHT
                elif node.is_passable:
                    color = COLOR_RED_LIGHT
                else:
                    color = COLOR_RED_DARK
                
                pygame.draw.rect(self.screen, color, tileRect)
                pygame.draw.rect(self.screen, COLOR_WHITE, tileRect, 1)
                row.append(tileRect)
            tiles.append(row)
        self.tiles = tiles
            
    def label_tile(self, node, string, color=COLOR_WHITE):
        i,j = node.location
        renderLoc = self.tiles[i][j].center
        thingRender = self.thing_font.render(string, True, color)
        thingRect = thingRender.get_rect()
        thingRect.center = renderLoc
        self.screen.blit(thingRender, thingRect)
    
    def render_things(self):
        locations = {}
        for node in self.environment.maze:
            if node.is_goal:
                self.label_tile(node, "👑", COLOR_YELLOW)

        for agent in self.environment.agents:
            location = agent.location
            self.label_tile(agent.location, str(agent), COLOR_BLUE)
            
            if self.track:
                if hasattr(agent, "frontier"):
                    for node in agent.frontier:
                        self.label_tile(node, "?", COLOR_WHITE)
                