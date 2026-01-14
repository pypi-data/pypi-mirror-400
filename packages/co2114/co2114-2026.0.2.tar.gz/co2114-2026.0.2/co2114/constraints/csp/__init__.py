import numpy as np
import random
from ...agent.things import Thing, Agent
from collections.abc import Callable, Iterable
from copy import deepcopy

from .util import alldiff

__all__ = [
    'util',
    'CSPAgent',
    'ConstraintSatisfactionProblem',
    'Variable',
    'Factor']

class CSPAgent(Agent):
    def __repr__(self):
        return "🤖"
    
    def program(self, percept):
        pass

    def solve(self):
        raise NotImplementedError


class ConstraintSatisfactionProblem:
    def __init__(self, variables, constraints):
        self.__variables = variables
        self.__constraints = constraints

    @property
    def variables(self):
        return self.__variables
    
    @property
    def domains(self):
        return {variable: variable.domain for variable in self.variables}

    @property
    def constraints(self):
        return self.__constraints
    
    @property
    def is_consistent(self):
        return all(constraint.is_satisfied for constraint in self.constraints)
    
    @property
    def is_complete(self):
        return all(variable.is_assigned for variable in self.variables) \
                    and self.is_consistent
    
    @property
    def arcs(self):
        return [arc for constraint in self.constraints if constraint.is_binary
                        for arc in constraint.arcs]
    
    def __repr__(self):
        return str({v.name: v for v in self.variables})
    

class __Variable(Thing):
    @property
    def value(self):
        return self.__value
    
    @property
    def is_assigned(self):
        return hasattr(self, '__value') and self.__value is not None

    def __eq__(self, x):
        return (x == self.value)
    
    def __ne__(self, x):
        return (x != self.value)
    
    def __lt__(self, x):
        return self.value < x if self.is_assigned else True

    def __gt__(self, x):
        return self.value > x if self.is_assigned else True
    
    def __le__(self, x):
        return self.__eq__(x) or self.__lt__(x)
    
    def __ge__(self, x):
        return self.__eq__(x) or self.__gt__(x)
    
    def __add__(self, x):
        return self.value + x if self.is_assigned else self
    
    def __sub__(self, x):
        return self.value - x if self.is_assigned else self

    def __mul__(self, x):
        return self.value * x if self.is_assigned else self
    
    def __truediv__(self, x):
        return self.value / x if self.is_assigned else self
    
    def __rtruediv__(self, x):
        return x / self.value if self.is_assigned else self
    
    def __mod__(self, x):
        return self.value % x if self.is_assigned else self

    def __or__(self, x):
        return self.value | x if self.is_assigned else self
    
    def __and__(self, x):
        return self.value & x if self.is_assigned else self
    
    def __pow__(self, x):
        return self.value ** x if self.is_assigned else self

    def __neg__(self):
        return -self.value if self.is_assigned else self

    def __truediv__(self, x):
        return self.value/x if self.is_assigned else self
    
    def __floordiv__(self, x):
        return self.value//x if self.is_assigned else self
    
    def __abs__(self):
        return abs(self.value) if self.is_assigned else self


class Variable(__Variable):
    def __init__(self, domain, name=None):
        self.__domain = deepcopy(domain)  # domain belongs only to one variable
        self.__value = None
        self.name = name
        self.__hash = random.random()

    def __hash__(self):
        return hash(self.__hash)

    @property
    def is_assigned(self):
        return self.__value is not None

    @property
    def value(self):
        return self.__value
    
    @value.setter
    def value(self, x):
        if x in self.domain or x is None:
            self.__value = x
        else:
            raise ValueError(f"{self.name}: {x} not in domain {self.domain}")

    @property
    def domain(self):
        return self.__domain
    
    def __repr__(self):
        return f"{self.name}({str(self.value) if self.is_assigned else '?'})"


class Factor(Thing):
    def __init__(self, constraint, variables):
        assert isinstance(constraint, Callable), "constraint must be callable"
        self.__function = constraint
        if not isinstance(variables, Iterable):
            variables = [variables]
        self.__variables = np.array(variables).ravel().tolist()
        if self.__xnary < 1:
            raise ValueError(f"{self}: number of variables must be >1")

    def __call__(self, *args, **kwargs):
        return self.__function(*args, **kwargs)

    def __iter__(self):
        return iter(self.__variables)
    
    def __contains__(self, variable):
        """
            overrides in keyword behaviour because variable equality 
            is checked by value rather than hash
        """
        return any(variable is _variable for _variable in self)
        

    @property
    def is_satisfied(self):
        if all(v.is_assigned for v in self.__variables):
            return self(*self.__variables) 
        elif self.is_global:
            return self.__function(*self.__variables)
        else:
            return True
    
    def __repr__(self):
        return str(tuple([str(v.name) for v in self.variables]))

    @property
    def __xnary(self):
        return len(self.variables)
    
    @property
    def is_unary(self):
        return self.__xnary == 1
    
    @property
    def is_binary(self):
        return self.__xnary == 2
    
    @property
    def is_global(self):
        return self.__xnary > 2

    @property
    def arcs(self):
        if not self.is_binary:
            raise TypeError(f"{self}: constraint is not binary")
        L,R = self.variables
        return [(self, L, R), (self, R, L)]

    @property
    def variables(self):
        return self.__variables
    

class Constraint(Factor):
    pass


## NOT CURRENTLY VIABLE DO NOT USE
# from agent.environment import Environment 

# class __CSPEnvironment(Environment):
#     def __init__(self, problem, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.__csp = problem

#     @property
#     def csp(self):
#         return self.__csp

#     @property
#     def variables(self):
#         return self.csp.variables
    
#     @property
#     def constraints(self):
#         return self.csp.constraints

#     @property
#     def domains(self):
#         return self.csp.domains

#     @property
#     def is_done(self):
#         return all(variable.is_assigned for variable in self.variables) and \
#                  all(constraint.is_satisfied for constraint in self.constraints)

