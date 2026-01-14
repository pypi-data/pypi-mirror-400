from .logic import *

from copy import copy

def is_literal(x: Proposition) -> bool:
    return type(x) in [Proposition, Not]

class KnowledgeBase(Proposition):
    """ Represents the knowledge base of an agent """
    def __init__(self, *args):
        match len(args):
            case 0:
                self._conjunction =  Sentence()
            case 1:
                self._conjunction = args[0]
            case _:
                self._conjunction: Conjunction = Conjunction(*args)
        self._entails = set()

    def __repr__(self) -> str:
        return f"KB: {self._conjunction}"


    def evaluate(self, model: dict) -> bool:
        """ evalutes a model over the knowledge base """
        return self._conjunction.evaluate(model)
    
    def __call__(self, model: dict) -> bool:
        """ evaluates a model """
        return self.evaluate(model)

    @property
    def symbols(self) -> set:
        """ returns the set of symbols that exist in the knowledge base """
        return self._conjunction.symbols

    def to_cnf(self) -> None:
        """ converts knowledge base into conjunctive normal form """
        self._conjunction = cnf(self._conjunction)
        
    def as_cnf(self):
        """ returns a new knowledge base in conjunctive form """
        KB = copy(self)
        KB.to_cnf()
        return KB

    def __invert__(self) -> Proposition:
        if isinstance(self._conjunction, Proposition):
            return KnowledgeBase(~self._conjunction)
        else:
            return self
    
    def __and__(self, x:Proposition) -> Proposition:
        if not isinstance(x, Proposition):
            raise TypeError(f"input must be Proposition, was type {type(x)}")
        if isinstance(self._conjunction, Proposition):
            return Conjunction(self._conjunction, x)
        else:
            return x

    def __or__(self, x:Proposition) -> Proposition:
        if not isinstance(x, Proposition):
            raise TypeError(f"input must be Proposition, was type {type(x)}")
        if isinstance(self._conjunction, Proposition):
            return Disjunction(self._conjunction, x)
        else:
            return x

    def __contains__(self, x:Proposition) -> bool:
        """ returns if symbol is in knowledge base 
             - symbols and their negations (P, ~P only)
        """
        return (x in self._conjunction)
    
    def entails(self, x:Proposition) -> bool:
        """ returns if knowledge base entails proposition """
        if is_literal(x) and x in self._entails: return True
        entailment = model_check(self, x)
        if entailment and (type(x) in [Proposition, Not]):
            self._entails.add(x)
        return entailment
    
    def models(self, x:Proposition) -> bool:
        """ alias for entails """
        return self.entails(x)

    def _add(self, x: Proposition, validate: bool = False) -> None:
        """ add a new proposition to the knowledge base """
        if not isinstance(x, Proposition):
            raise TypeError(f"input must be Proposition, was type {type(x)}")
        if isinstance(self._conjunction, Proposition):
            if validate and self.entails(~x):
                raise ValueError(
                    f"cannot add contradiction to Knowledge Base, KB ⊨ {~x}")
                return
            self._conjunction &= x
        else:
            self._conjunction = x  # add symbol for first time

    def add(self, *xs:tuple[Proposition], validate: bool = False) -> None:
        """ add new proposition(s) to the knowledge base """
        for x in xs:
            self._add(x, validate)  # add other arguments



def model_check(knowledge:KnowledgeBase, sentence:Proposition):
    """ run model checking algorithm """
    symbols = set.union(knowledge.symbols, sentence.symbols)
    return _check_all(knowledge, sentence, symbols, {})



def _check_all(knowledge, query, symbols, model):
    """
        enumerates all models in knowledge base and 
        checks if query is entailed
    """
    if not symbols:
        if knowledge.evaluate(model):
            return query.evaluate(model)
        return True
    else:
        remaining = symbols.copy()
        p = remaining.pop()

        model_true = model.copy()
        model_true[p] = True
        model_false = model.copy()
        model_false[p] = False
    return (
        _check_all(knowledge, query, remaining, model_true)
             and _check_all(knowledge, query, remaining, model_false))
