from __future__ import annotations

import math
import warnings
import json

from typing import Iterable, Iterator, override, Callable, Collection, TypeVar

from matplotlib import pyplot as plt
from matplotlib.figure import Figure  # for type hinting

from ..agent.environment import Environment
from .things import Thing, Agent, UtilityBasedAgent, Action

Numeric = int |  float | None
Location = Thing | Iterable
Label = str
# Weight = Numeric

# Example graph dictionary representing UK cities and distances between them
UK_CITIES_GRAPH:dict[str, Iterable[str | tuple[str,str] | tuple[Numeric, Numeric] | int]] = {
    "nodes": ["Edinburgh", "Glasgow", "Manchester", "Liverpool",
             "Newcastle", "York", "Sheffield", "Leicester", 
             "London", "Bath", "Bristol", "Exeter", "Cardiff", "Birmingham"],
    "edges": [("Edinburgh", "Glasgow"), ("Glasgow", "Newcastle"),
             ("Edinburgh", "Newcastle"), ("Newcastle", "York"),
             ("Glasgow", "Manchester"), ("Manchester", "Liverpool"),
             ("York", "Sheffield"), ("York", "Leicester"),
             ("Sheffield", "Leicester"), ("Sheffield", "Birmingham"),
             ("Sheffield", "London"), ("Manchester", "Sheffield"),
             ("Manchester", "Birmingham"),  ("Birmingham", "Liverpool"),
             ("Birmingham", "Cardiff"), ("Leicester", "London"),
              ("Birmingham", "Leicester"),
             ("Birmingham", "London"), ("Birmingham", "Bristol"),
             ("London", "Bristol"), ("Cardiff", "Bristol"), ("Bristol", "Bath"), ("Exeter", "Bristol"), ("Exeter", "London")],
    "weights": [2,4,1,1,4,1,1,2,1,3,3,2,1,2,5,1,2,2,3,2,1,1,2,5],
    "locations": [(55.9533, -3.1883), (55.8617, -4.2583), (53.4808, -2.2426),
                  (53.4084, -2.9916), (54.9783, -1.6178), (53.9614, -1.0739),
                  (53.3811, -1.4701), (52.6369, -1.1398), (51.5072, -0.1276),
                  (51.3781, -2.3597), (51.4545, -2.5879), (50.7260, -3.5275),
                  (51.4837, -3.1681), (52.4823, -1.8900)]
}


class Node(Thing):
    """ A node in a graph structure."""
    def __init__(self, label:Label = "") -> None:
        """ Create a node with given label. """
        self.label:Label = label  # identifier for node
        self.neighbours:set[Node] = set()  # set of neighbouring nodes
        self.weights:dict[Node, Numeric] = {}  # mapping of neighbouring nodes to edge weights
        self.location:Location | None = None  # optional location attribute

    @override
    def __repr__(self) -> str:
        """ String representation of node, returning its label. """
        return self.label
    

    def add_neighbour(self, node:Node, weight:Numeric = None) -> None:
        """ Add a neighbouring node with optional edge weight. 
        
        :param   node: Node to be added as a neighbour.
        :param weight: Weight of edge to neighbour (default None).
        """
        if not isinstance(node, Node):  # type check
            raise TypeError(f"{self}: {node} is not a Node")
        
        if node not in self.neighbours:  # avoid duplicate edges
            self.neighbours.add(node)
            self.weights[node] = weight
            node.add_neighbour(self, weight)  # undirected graph



Edge = tuple[Node, Node, Numeric]  # edge type alias


class Graph:
    """ A graph structure comprising nodes and edges. """
    def __init__(self) -> None:
        """ Create an empty graph. """
        self.nodes:set[Node] = set()

    
    def __iter__(self) -> Iterator[Node]:
        """ Iterate over nodes in the graph. """
        return iter(self.nodes)


    def add_node(self, node:Node) -> None:
        """ Add a node and its neighbours to the graph.
        
        :param node: Node to be added to the graph.
        """
        if not isinstance(node, Node):  # type check
            raise TypeError(f"{self}: {node} is not a Node")
        
        if node not in self.nodes:  # avoid duplicate nodes
            self.nodes.add(node)
            for neighbour in node.neighbours:  # add neighbours recursively
                self.add_node(neighbour)


    def plot_nodes(
            self,
            condition:Callable | None = None,
            init:Node | Label | None = None,
            labels:Iterable[Label] | None = None) -> Figure:
        """ Plot the nodes in the graph
        
        :param condition: Function to filter nodes to be plotted. If None, all nodes are plotted.
        :param init:     Node to use as the root of the plot. If None, a random node is used.
        :param labels:   Iterable of labels for the nodes. If None, node labels are used.
        """

        # filter nodes based on condition
        nodes = self.nodes if condition is None else \
            {node for node in self.nodes if condition(node)}
        
        # handle empty graph
        if len(nodes) == 0:
            return plt.figure(figsize=(8,8))
        
        # determine initial node for layout
        _init = Node()  # placeholder
        if not isinstance(init, Node):
            if init is None:
                _init = next(iter(nodes))  # random node
            elif isinstance(init, Label): # label provided
                _flag = True
                for node in nodes: # find node with matching label
                    if init == node.label:
                        _init = node
                        _flag = False
                        break
                if _flag:
                    _init = next(iter(nodes))
            else:
                raise TypeError(f"{self}: {init} is not a Node or label")
        elif init not in nodes: # node not in filtered set
            _init = next(iter(nodes)) # random node
        
        locs = {_init: (0.,0.)} # locations of nodes
        tree = {0: {_init}} # nodes at each distance from init
        dist = 1  # dist from init
        tree[dist] = _init.neighbours & nodes  # set intersection
        for i, node in enumerate(tree[dist]):
            locs[node] = (dist, i-0.5*len(tree[dist])) # initial layout

        while len(tree[dist]) > 0:  # expand tree
            tree[dist+1] = set()
            # find new nodes at dist+1 from init
            for node in tree[dist]:
                neighbours = node.neighbours & nodes # set intersection
                for _node in neighbours:
                    if _node not in locs and _node not in tree[dist+1]:
                        tree[dist+1].add(_node)
            dist += 1  # increment distance
            # layout new nodes
            for i, node in enumerate(tree[dist]):
                offset = i-0.5*len(tree[dist])
                locs[node] = (dist + 0.1*offset, offset)
        
        edges:set[Edge] = set()
        for node in nodes:
            for _node in (node.neighbours & nodes):
                forward:Edge = (node, _node, node.weights[_node])
                backward:Edge = (_node, node, _node.weights[node])
                if forward not in edges and backward not in edges:
                    edges.add(forward)

        fig, ax = plt.subplots(figsize=(8,8))
        for node, loc in locs.items():  # plot nodes and labels
            name = str(node) if labels is None else labels[node]
            ax.plot(*loc, 'ko', ms=20)
            ax.text(loc[0]+0.1, loc[1]+0.1, name)
        
        for edge in edges:  # plot edges and weights
            a,b, weight = locs[edge[0]], locs[edge[1]], edge[2]
            ax.plot(*[[i,j] for i,j in zip(a,b)],'k')
            if weight is not None:
                ax.text(*[i+(j-i)/2 for i,j in zip(a,b)], str(weight))
        ax.axis("off")  # turn off axes
        return fig



class GraphEnvironment(Environment):
    """ An environment based on a graph structure. """
    def __init__(self, graph:Graph | None = None, *args, **kwargs) -> None:
        """ Create a graph environment."""
        super().__init__(*args, **kwargs)  # initialize base Environment
        self.graph = graph if isinstance(graph, Graph) else Graph() 

    
    def add_node(self, node:Node, location:None | tuple = None) -> None:
        """ Add a node to the graph environment.
        
        :param node: Node to be added to the graph.
        :param location: Optional location information of node, default None
        """
        self.graph.add_node(node)
        if location is not None:
            node.location = location


    @override
    def percept(self, agent:Agent) -> list[tuple[Node, Numeric]]:
        """ Return the percepts for the agent based on its location in the graph."""
        node:Node = agent.location  # type: ignore
        if len(node.weights) == 0:
            return [(n, 1) for n in node.neighbours]
        else:
            return [(n, node.weights[n]) for n in node.neighbours]


    @override
    def add_agent(self, 
                  agent:Agent, 
                  location:Location | None = None,
                  node:Node | None = None) -> None:
            """ Add an agent to the graph environment at a specified location or node.
            
            :param agent:    Agent to be added to the environment.
            :param location: Location where the agent should be added (default None).
            :param node:     Node where the agent should be added (default None).
            """
            if not isinstance(agent, Agent):  # type check
                raise TypeError("f{self}: {agent} is not an Agent")
            
            if node is not None:  # assign to specified node
                if not isinstance(node, Node):
                    print(f"{self}: {node} is not a valid Node")

                if node in self.graph:  
                    super().add_agent(agent, node)
                else:
                    print(f"{self}: {node} is not in graph")

            elif location is not None:  # assign to node with matching location
                _flag = True

                for node in self.graph:  # find node with matching location
                    if location == node.location:
                        super().add_agent(agent, node)
                        _flag = False
                        break
                    
                if _flag:  # location not found
                    print(f"{self}: {location} was not found in environment")

            else:  # default to random node
                super().add_agent(agent)


    def show(self, *args, **kwargs):
        """ Show a plot of the graph environment. """
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            self.graph.plot_nodes(*args, **kwargs).show()


    @classmethod
    def from_dict(cls,
                  graph_dict: dict[str, Iterable[str | tuple[str,str] | int]]
                  )-> GraphEnvironment:
        """ Create a GraphEnvironment from a dictionary representation of a graph."""
        if "vertices" not in graph_dict and "edges" not in graph_dict:
            raise ValueError(f"No vertices in json string {graph_dict}")
        
        if "edges" not in graph_dict: 
            raise ValueError(f"No edges in json string {graph_dict}")
        
        vertices = graph_dict[  # support 'nodes' or 'vertices'
                            'vertices' if 'vertices' in graph_dict else 'nodes']
        edges = graph_dict['edges']

        for edge in edges:
            if len(edge) != 2:  # type: ignore
                raise ValueError(
                        f"Edges must comprise two nodes, {edge} does not")
            if any(v not in vertices for v in edge):  # type: ignore
                raise ValueError(
                    f"Edges must map between valid vertices, {edge} does not")
        
        nodes = {v: Node(f"{v}") for v in vertices}
        
        if 'weights' in graph_dict:
            weights = graph_dict['weights']
        else:
            weights = [None]*len(edges) # type: ignore
        for edge, weight in zip(edges, weights):
            a, b = edge  # type: ignore
            nodes[a].add_neighbour(nodes[b], weight)  # add edge with weight

        if 'locations' in graph_dict:
            locations = graph_dict['locations']
        else:
            locations = [(0,0)]*len(nodes)
        for key, location in zip(nodes, locations):
            nodes[key].location = location # type: ignore

        # create environment and add nodes
        environment = cls()
        for _,node in nodes.items():
            environment.add_node(node)

        return environment
    
    @classmethod
    def from_json(cls, json_str: str) -> GraphEnvironment:
        """ Create a GraphEnvironment from a JSON string representation 
        of a graph."""
        return cls.from_dict(json.loads(json_str))


class ShortestPathEnvironment(GraphEnvironment):
    """ A graph environment for shortest path finding agents. """
    def get_node(self, node: Node | Label) -> Node:
        """ Retrieve a node from the graph by Node or label.

        :param node: Node or label of the node to retrieve.
        """
        if isinstance(node, Node):
            assert node in self.graph
        else:
            for vertex in self.graph:
                if node == vertex.label:
                    node = vertex
                    break
            assert isinstance(node, Node)
        return node
    

    @override
    def add_agent(self,
                  agent:ShortestPathAgent,
                  init: Node | Label,
                  target: Node | Label) -> None:
        """ Add a shortest path agent to the environment.
        
        :param agent:  Agent to be added to the environment.
        :param init:   Initial node or label for the agent.
        :param target: Target node or label for the agent, if applicable.
        """
        # retrieve nodes from labels if necessary
        init = self.get_node(init)
        target = self.get_node(target)
        # add agent to environment
        super().add_agent(agent, node=init)
        # initialise agent with init and target nodes
        agent.initialise(init, target)


    @property  # override
    def is_done(self) -> bool:
        """ Check if all agents have delivered their paths. """
        return (hasattr(self, "delivered") and self.delivered)


    @override
    def execute_action(self,
                       agent: ShortestPathAgent,
                       action: tuple[str, Node]) -> None:
        """ Execute an action for the shortest path agent.
        
        Commands:
        - "explore": move to a neighbouring node
        - "deliver": deliver the shortest path to the target node

        :param  agent:  Agent executing the action.
        :param action: Action to be executed, format (command, node).
        """
        command, node = action
        match command:
            case "explore":
                agent.explore(node)
            case "deliver":
                if not hasattr(self, "shortest_path"):
                    self.shortest_path = {}
                self.shortest_path[agent.init] = {node: agent.deliver(node)}
                self.delivered = True


class ShortestPathAgent(UtilityBasedAgent):
    """ An agent that finds the shortest path in a graph environment.
    
    Needs implementation of methods:
        `program(self, percepts:list[tuple[Node, Numeric]]) -> tuple[str, Node]`
        `utility(action:tuple[str, Node]) -> Numeric`
        `explore(node:Node) -> None`
        `deliver(node:Node) -> tuple[list[Node], Numeric]`
    
    Has attributes:
        `init`:   Initial node of the agent.
        `target`: Target node of the agent.
        `location`: Current location of the agent.
        `dist`:   Dictionary mapping nodes to their distance from the initial node.
        `prev`:   Dictionary mapping nodes to their previous node in the shortest path.
    """
    def __init__(self):
        """ Initialise the shortest path agent. """
        super().__init__()

        # attributes for shortest path finding
        self.__init = self.__target = None
        self.location:Node | None = None
        self.dist:dict[Node, Numeric] = {}
        self.prev:dict[Node, Node | None] = {}
        self.visited:set[Node] = set()


    @property
    def at_goal(self) -> bool:
        """ Check if the agent is at the target node. """
        return self.location is self.target
    

    @property
    def init(self) -> Node | None:
        """ Get the initial node of the agent. """
        return self.__init
    

    @property
    def target(self) -> Node | None:
        """ Get the target node of the agent. """
        return self.__target


    def initialise(self, node:Node, target:Node | None) -> None:
        """ Initialise the agent with its starting and target nodes.
        
        :param node:   Initial node for the agent.
        :param target: Target node for the agent, if applicable.
        """
        self.__init = self.location = node
        self.__target = target
        self.dist[node] = 0  # distance from initial node
        self.prev[node] = None  # previous node in path


    def explore(self, node:Node) -> None:
        """ Explore a new node. The actuator of the agent. Needs to be implemented.
        
        :param node: Node to be explored.
        """
        raise NotImplementedError
    

    def deliver(self, node:Node) -> tuple[list[Node], Numeric]:
        """ Deliver the shortest path to the specified node, 
        and distance to node. Needs to be implemented
        
        :param            node: Node to deliver the shortest path to.
        :return path, distance: Tuple of (shortest path as list of nodes, distance to node).
        """
        raise NotImplementedError