from ..agent.things import Thing


#= Formatting
def _balanced(s:str) -> bool:
    """ checks whether a string has balanced parantheses """
    counter:int = 0
    for c in s:
        if c == "(":
            counter += 1
        elif c == ")":
            if counter <= 0:
                return False
            counter -= 1
    return counter == 0


def format(formula: str) -> str:
    """ formats a formula by wrapping in parantheses if not already.
        will not put parenthesis around symbols or their negation
    """
    if not len(formula) or formula.isalpha() or (
        formula[0] == "(" and formula[-1] == ")" and _balanced(formula[1:-1])
    ) or (formula[0] == "¬" and formula[1:].isalpha()):
        return formula
    else:
        return f"({formula})"
    

#= Classes
class Sentence(Thing):
    """ base class of a sentence, empty """
    def __repr__(self) -> str:
        return self.formula
    

    def evaluate(self, model: dict) -> bool:
        return True

    @property
    def formula(self) -> str:
        return ""


    def __contains__(self, x) -> bool:
        return False


    @property
    def symbols(self) -> set:
        return set()

    
class Proposition(Sentence):
    """ Logical proposition representing logical statement """
    def __init__(self, name:str) -> None:
        self._name:str = name

    
    def __eq__(self, x:Sentence) -> bool:
        return (self is x)
    
    
    def __hash__(self) -> int:
        return hash(self.formula)
    
    
    def __bool__(self) -> None:
        """ prevents evaluation of boolean logic using, e.g. and and or, to avoid confusion """
        raise TypeError(f"cannot evaluate {type(self)}: use Proposition.evaluate(model)")
    
    @property
    def formula(self) -> str:
        """ the string representation of the proposition """
        return self._name
    
    @property
    def symbols(self) -> set:
        """ set of logical symbols in proposition """
        return {self}
    
    
    def __call__(self, model) -> bool:
        return self.evaluate(model)
    
    def evaluate(self, model: dict) -> bool:
        """ evaluates a model containing self """
        if self in model:
            return bool(model[self])
        else:
            raise IndexError(f"{self} not in model {model}")

               
    def __contains__(self, x:Sentence) -> bool:
        if type(x) not in (Proposition,Not):
            raise TypeError(
                f"Cannot evaluate if type {type(x).__name__} is in {type(self).__name__}")
        return (x in self.symbols) if type(x) is Proposition else False
        
    
    def __invert__(self) -> Sentence:
        """ returns negation of self (¬self)"""
        return Not(self)
    
    
    def __and__(self, x:Sentence) -> Sentence:
        """ returns conjunction (self ∧ input) """
        return And(self, x)
    
    
    def __or__(self, x:Sentence) -> Sentence:
        """ returns disjunction (self ∨ input) """
        return Or(self, x)
    
    def onlyif(self, x:Sentence) -> Sentence:
        """ 'self only if input', converse of 'input if self'
            returns implication (self -> input)
        """
        return Implication(self, x)
    
    def implies(self, x:Sentence) -> Sentence:
        """ returns implication (self -> input)"""
        return Implication(self, x)

    def iff(self, x:Sentence) -> Sentence:
        """ 'if and only if' , returns biconditional (self <-> input)"""
        return Biconditional(self, x)

                             
class Not(Proposition):
    """ Logical proposition representing negation or 'not' """
    def __init__(self, symbol: Proposition):
        super().__init__("¬"+format(symbol.formula))
        self.operand:Proposition = symbol
    
    
    def evaluate(self, model: dict) -> bool:
        """ evaluates a model containing operand """
        return not self.operand(model)

    @property
    def symbols(self) -> set:
        return self.operand.symbols
    
    
    def __contains__(self, x: Proposition) -> bool:
        if type(x) is Not and type(x.operand) is Proposition:
            return x.operand == self.operand
        return x in self.operand

    
    def __invert__(self) -> Sentence:
        """ returns ¬(¬operand), so operand"""
        return self.operand


class Conjunction(Proposition):
    """ Logical conjunction (∧) of two or more propositions """
    def __init__(self, operand0:Proposition, operand1:Proposition, *operands):
        _operands:list = self._expand(operand0) + self._expand(operand1)
        for operand in operands:
            _operands.extend(self._expand(operand))

        formula:str = format(_operands[0].formula)
        for operand in _operands[1:]:
            formula += " ∧ " + format(operand.formula)

        super().__init__(formula)
        self.operands:tuple = tuple(_operands)
        
    def _expand(self, operand:Proposition) -> list:
        """ returns individual operands in a conjunction
            (P ∧ Q) becomes [P, Q]
            R becomes [R]
        """
        if isinstance(operand, Conjunction):
            return list(operand.operands)
        else:
            return [operand]
    
    
    def __and__(self, operand: Proposition):
        return Conjunction(*self.operands, operand)

    
    def evaluate(self, model: dict) -> bool:
        return all(operand.evaluate(model) for operand in self.operands)
    
    
    def __contains__(self, x:Proposition) -> bool:
        return any(x in operand for operand in self.operands)

    @property
    def symbols(self) -> set:
        return set.union(*[operand.symbols for operand in self.operands])

And = Conjunction  # alias


class Disjunction(Proposition):
    """ Logical disjunction (∨) of two or more propositions """
    def __init__(self, operand0:Proposition, operand1:Proposition, *operands):
        
        _operands:list = self._expand(operand0) + self._expand(operand1)
        for operand in operands:
            _operands.extend(self._expand(operand))

        formula:str = format(_operands[0].formula)
        for operand in _operands[1:]:
            formula += " ∨ " + format(operand.formula)

        super().__init__(formula)
        self.operands:tuple = tuple(_operands)

        
    def _expand(self, operand:Proposition) -> list:
        """ returns individual operands in a disjunction
            (P ∨ Q) becomes [P, Q]
            R becomes [R]
        """
        if isinstance(operand, Disjunction):
            return list(operand.operands)
        else:
            return [operand]
    
    
    def __or__(self, operand: Proposition):
        return Disjunction(*self.operands, operand)
    
    
    def evaluate(self, model: dict) -> bool:
        return any(operand.evaluate(model) for operand in self.operands)
    
    
    def __contains__(self, x:Proposition) -> bool:
        return any(x in operand for operand in self.operands)

    @property
    def symbols(self) -> set:
        return set.union(*[operand.symbols for operand in self.operands])
    
Or = Disjunction  # alias


class Implication(Proposition):
    """ Logical implication (->) of two propositions """
    def __init__(self, left:Proposition, right:Proposition):
        self.antecedent:Proposition = left
        self.consequent:Proposition = right
        self.left:Proposition = self.antecedent
        self.right:Proposition = self.consequent

    @property
    def formula(self): 
        return f"{format(self.antecedent.formula)} -> {format(self.consequent.formula)}"
    
    
    def evaluate(self, model: dict) -> bool:
        return ((not self.antecedent.evaluate(model)) or 
                    self.consequent.evaluate(model))

    @property
    def symbols(self) -> set:
        return set.union(self.antecedent.symbols, self.consequent.symbols)
    

class Biconditional(Implication):
    """ Logical biconditional (<->) of two propositions """
    @property
    def formula(self):
        return f"{format(self.left.formula)} <-> {format(self.right.formula)}"

    
    def evaluate(self, model: dict):
        left = self.left.evaluate(model)
        right = self.right.evaluate(model)
        return (left and right) or (not left and not right)
    

#= Utility functions
def simplify(statement:Proposition) -> Proposition:
    """ Simplifies propositions into logical ands and ors"""
    match statement:
        case Biconditional():
            l, r = statement.antecedent, statement.consequent
            return simplify(l.implies(r) & r.implies(l))
        case Implication():
            return simplify(~statement.antecedent | statement.consequent)
        case Not():
            proposition = simplify(statement.operand)
            match proposition:
                case Conjunction() | Disjunction():
                    return Conjunction(*[~p for p in proposition.operands])
                case _:
                    return ~proposition
        case Conjunction():
            out = Conjunction(
                *[simplify(p) for p in statement.operands if p is not None])
            return out
        case Disjunction():
            out = Disjunction(
                *[simplify(p) for p in statement.operands if p is not None])
            return out
        case _:
            return statement


def distribute(sentence:Disjunction) -> Sentence:
    """ Distributes disjunctions """
    if type(sentence) is Conjunction:
        return Conjunction(
            *[distribute(operand) for operand in sentence.operands])
    if type(sentence) is not Disjunction:
        return sentence
    if not any([type(p) is Conjunction for p in sentence.operands]):
        return sentence
    distr = []
    for proposition in sentence.operands:
        if type(proposition) is Conjunction:
            for operand in proposition.operands:
                conj = Disjunction(operand,*[p for p in sentence.operands if p is not proposition])
                distr.append(conj)
    return Conjunction(*distr)


def cnf(sentence:Sentence) -> Sentence:
    """ returns the conjunctive normal form of a logical sentence"""
    return distribute(simplify(sentence))