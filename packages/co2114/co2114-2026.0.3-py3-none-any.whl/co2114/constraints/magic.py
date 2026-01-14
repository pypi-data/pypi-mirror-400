import numpy as np

from .csp import *

class MagicTile(Variable):
    def __add__(self, y):
        x = self.value if self.value else 0
        y = (y.value if y.value else 0) if isinstance(y, Variable) else y
        return x+y
    
    def __radd__(self, y):
        return self + y  # symmetric add


class MagicSquare(ConstraintSatisfactionProblem):
    def __init__(self, size=4):
        variables, constraints = self.initialise_state(size)
        super().__init__(variables, constraints)

    @property
    def n(self):
        return self.__n
    
    @property
    def M(self):
        """ Magic constant """
        return self.n*(1+self.n**2)/2
    
    def __repr__(self):
        return str(self.__grid)

    def initialise_state(self, size):
        assert isinstance(size, int), f"{self}: value size ({size}) must be int"
        assert size > 0, f"{self}: size ({size}) must be greater than 0"
        self.__n = size
        domain = set(range(1,self.n**2+1))
        grid = np.matrix([
            [MagicTile(domain, str((i,j))) for j in range(self.n)] 
                for i in range(self.n)])
        self.__grid = grid
        variables = np.array(grid).ravel().tolist()
        
        def magic_constraint(*variables):
            return (np.sum(variables) <= self.M)

        row_constraints = {Factor(magic_constraint, grid[i,:])
                                for i in range(self.n)}
        col_constraints = {Factor(magic_constraint, grid[:,i])
                                for i in range(self.n)}
        diag_constraints = {Factor(magic_constraint, np.diag(grid)),
                            Factor(magic_constraint, np.diag(np.fliplr(grid)))}
        alldiff_constraint = {Factor(alldiff, variables)}

        constraints = row_constraints \
                        | col_constraints \
                            | diag_constraints \
                                | alldiff_constraint
        return  variables, constraints
        




# class __MagicSquareEnvironment(CSPEnvironment, GraphicEnvironment):
#     def __init__(self, n:int, *args, **kwargs):
#         csp = MagicSquare(n)
#         super().__init__(*args, problem=csp, height=n, width=n, **kwargs)
#         for i in range(n):
#             for j in range(n):
#                 self.add_thing(self.csp.state[i,j], location=(i,j))

#     @property
#     def is_done(self):
#         if len(self.agents) == 0: return True
#         return super().is_done

#     def percept(self, agent):
#         return self.csp
    
#     def add_agent(self, agent):
#         # self.things.add(agent)
#         self.agents.add(agent)

#     def execute_action(self, agent, action):
#         command, state = action

#         match command:
#             case "done":
#                 # should end naturally
#                 print("all good")
#             case "explore":
#                 agent.explore(self.csp)
#             case "backtrack":
#                 _variables = agent.backtrack()
#                 for variable, _variable in zip(self.csp.variables, _variables):
#                     variable.value = _variable.value
