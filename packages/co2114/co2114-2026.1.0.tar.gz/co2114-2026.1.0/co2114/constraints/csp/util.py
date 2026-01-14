from collections.abc import Iterable
from collections import deque
from copy import deepcopy

import numpy as np

def alldiff(*variables):
    if len(variables) == 1:
        if not isinstance(variables[0], Iterable):
            return True
        variables = variables[0]
    # variables = [
    #     variable.value for variabl in variable if variable.is_assigned]
    values = [
        variable.value for variable in variables 
            if variable.is_assigned]
    return len(set(values)) == len(values)


def aslist(npcol):
    return np.array(npcol).ravel().tolist()


def revise(factor, A, B):
    is_revised = False
    if A.is_assigned: return False
    for value in A.domain.copy():
        A.value = value
        is_valid_B = False
        for _value in B.domain:
            B.value = _value
            if factor.is_satisfied:
                is_valid_B = True
            B.value = None
        if not is_valid_B:
            A.domain.remove(value)
            is_revised = True
        A.value = None
    return is_revised


def ac3(csp, log=False, inplace=True):
    if not inplace: csp = deepcopy(csp)
    arcs = deque(csp.arcs)
    while len(arcs) > 0:
        f, A, B = arcs.popleft()  # end of queue
        if log:
            print(f"considering arc from {A.name} to {B.name}")
            print(f"  before: {A.name} in {A.domain}, {B.name} in {B.domain}")
        if revise(f, A, B):
            if log:
                print(f"  after: {A.name} in {A.domain}, {B.name} in {B.domain}")
            if len(A.domain) == 0: return False if inplace else None
            for constraint in csp.constraints:
                if log:
                    print(f"  do we need to check constraint {constraint}")
                    print(f"   is binary? {constraint.is_binary}")
                    print(f"   contains {A.name}? {A in constraint}")
                    print(f"   doesn't contain {B.name}? {B not in constraint}")
                if constraint.is_binary \
                        and A in constraint\
                            and B not in constraint:
                    for arc in constraint.arcs:
                        if arc[-1] is A:
                            if arc not in arcs:
                                if log:
                                    print(f"    adding {arc} to arcs frontier")
                                arcs.append(arc)
                            elif log:
                                print(f"    arc {arc} already in frontier")
        elif log:
            print(f"  after: {A.name} in {A.domain}, {B.name} in {B.domain} (no change)")
    return True if inplace else csp


def make_node_consistent(csp, inplace=True):
    if not inplace: csp = deepcopy(csp)
    for variable in csp.variables:
        if variable.is_assigned: continue  # ignore any assigned variables
        domain = variable.domain.copy()  # copy this to avoid set size change errors 
        for value in domain:
            variable.value = value
            for constraint in csp.constraints:
                if constraint.is_unary and variable in constraint:
                    if not constraint.is_satisfied:
                        variable.domain.remove(value)
                        break
            variable.value = None
    if not inplace: return csp