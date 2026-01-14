from ..agent.things import Agent, RationalAgent
from ..agent.environment import Environment

from .logic import *
from .inference import *

import random
from collections import deque
from typing import Union, TypeVar
T = TypeVar("T")


def permute_indices(n: int, i: int) -> tuple[int]:
    """ returns ordered permutation of indices from 0 to n-1 starting at i """
    if i < 0 or i >= n:
        raise ValueError(f"i must be in [0, {n-1}] for n = {n}. i = {i}")
    return (i, *list(range(i+1,n)), *list(range(0, i)))

def choice(bag: set[T]) -> T:
    """ returns a random element from a set """
    # return next(iter(bag))
    return random.choice(list(bag))

def sample(bag: set[T], n: int) -> set[T]:
    """ returns a sample of _n_ items from a set """
    if n < 1 or n > len(bag):
        raise ValueError(f"n must be between 1 and {len(bag)}, n = {n}")
    i, _sample = 0, set()
    while i < n:
        _sample.add(choice(bag - _sample))
        i+=1
    return _sample


WEAPON_NAMES = {
    "candlestick", "dagger", 
    "lead piping", "revolver", 
    "rope", "spanner"
}

CHARACTER_NAMES = {
    "scarlett", "mustard",
    "white", "green",
    "peacock", "plum"
}

ROOM_NAMES = {
    "kitchen", "ballroom", "conservatory",
    "dining room", "billiard room", "library",
    "study", "hall", "lounge"
}


def create_symbols() \
        -> tuple[set[Proposition],set[Proposition],set[Proposition]]:
    """ returns set of proposition for cluedo game (characters, rooms, weapons)
    """
    # characters_names = 

    characters : set[Proposition] = {
        Proposition(name) for name in CHARACTER_NAMES}
    rooms      : set[Proposition] = {
        Proposition(name) for name in ROOM_NAMES     }
    weapons    : set[Proposition] = {
        Proposition(name) for name in WEAPON_NAMES   }
    return characters, rooms, weapons


class LogicalAgent(RationalAgent):
    knowledge : KnowledgeBase = KnowledgeBase()


Card = Proposition
CluedoSymbols = dict[str, set[Card]] 
Guess = tuple[
        Union[Card,None],
        Union[Card,None],
        Union[Card,None]
    ]  # type alias


class CluedoAgent(RationalAgent):
    """ a cluedo player, but not necessary a logical one """
    def __init__(self, symbols: CluedoSymbols, name: Union[str, None] = None):
        self.symbols : CluedoSymbols = symbols
        self.__name = name

    def guess(self) -> Guess:
        """ makes a random guess (character, room, weapon) """
        _guess = []
        for key in ["characters", "rooms", "weapons"]:
            card = choice(self.symbols[key])
            _guess.append(card)

        return tuple(_guess)

    def receive_hand(self, hand: set[Card]) -> None:
        """ receives hand of cards """
        self.hand : set[Card] = hand

    def reveal_in_hand(self, guess: Guess) -> Union[Card, None]:
        """ reveals card in hand if guessed """
        if not hasattr(self, "hand"):
            raise KeyError(f"player {self} has no hand")
        for symbol in guess:
            if symbol in self.hand:
                return symbol  # return symbol

    def program(self,
                percepts : tuple[Agent, Guess, Union[Card, None]]
            ) -> Union[Guess, Card, None]:
        """ reveals a card if in hand or makes a guess """
        agent, guess, revealed = percepts

        if agent is not self:  # not my turn
            if revealed is None:  # noone revealed anything yet
                return self.reveal_in_hand(guess)
            return None  # does not contain in hand
        elif all(card is not None for card in guess) :
            return  # already made a guess this turn
        return self.guess()  # random guess
    
    def __repr__(self) -> str:
        return self.__name if self.__name else super().__repr__()


# class CluedoLogicalAgent(CluedoAgent, LogicalAgent):
#     """ a logical cluedo player """
#     def __init__(self, symbols: CluedoSymbols):
#         super().__init__(symbols)

#         # Must be at least one character, one room and one weapon
#         self.knowledge.add(
#             Disjunction(*self.symbols["characters"]),
#             Disjunction(*self.symbols["rooms"]),
#             Disjunction(*self.symbols["weapons"])) 

#         self.solution: Guess = (None, None, None)
#         self.is_not: set[Card] = set()


#     def receive_hand(self, hand: set[Card]) -> None:
#         """ receives hand of cards """
#         super().receive_hand(hand)
#         for card in self.hand:
#             self.knowledge.add(~card)  # solution cannot cards in hand
#             self.is_not.add(card)  # set of ruled out cards
#         print(f"{self.knowledge}")


#     @property
#     def insight(self) -> str:
#         outstr = f"{self}:\n"
#         for key in ["characters", "rooms", "weapons"]:
#             outstr += f"{key}:" + "{\n"
#             for symbol in self.symbols[key]:
#                 if self.knowledge.entails(symbol):
#                     outstr += f"\t{symbol}: YES!\n"
#                 elif self.knowledge.entails(~symbol):
#                     outstr += f"\t{symbol}: No.\n"
#                 else:
#                     outstr += f"\t{symbol}: maybe...\n"
#             outstr += "      }\n"
#         return outstr

#     def guess(self) -> Guess:
#         valid_characters = [
#             card for card in self.symbols["characters"] 
#                 if card not in self.is_not]
#         valid_rooms = [
#             card for card in self.symbols["rooms"] 
#                 if card not in self.is_not]
#         valid_weapons = [
#             card for card in self.symbols["weapons"] 
#                 if card not in self.is_not]
#         guess = (random.choice(valid_characters),
#                  random.choice(valid_rooms),
#                  random.choice(valid_weapons))
#         return guess

#     def program(self,
#                 percepts: tuple[Agent, Guess, Union[Card,None]]
#             ) -> Union[Guess, Proposition, None]:
#         """ agent program takes agent, proposition and returns a guess
#             (character, room, weapon)
#         """
#         agent, guess, revealed = percepts
#         if all(card is not None for card in guess):
#             if revealed is not None:
#                 if agent is self:  # if revealed to agent
#                     print(f"{self}: adding {~revealed} to knowledge")
#                     self.knowledge.add(~revealed)
#                     self.is_not.add(revealed)
#                 else:              # unseen reveal
#                     character, room, weapon = guess
#                     clause = ~character | ~room | ~weapon  # one must be wrong !
#                     print(f"{self}: adding {clause} to knowledge")
#                     self.knowledge.add(clause)
#             elif agent is self:  # no card was revealed on own guess
#                 character, room, weapon = guess
#                 if character not in self.hand:
#                     print(f"{self} : adding {character} to knowledge")
#                     self.solution=(character,self.solution[1],self.solution[2])
#                     self.knowledge.add(character)
#                     self.is_not |= self.symbols["characters"] - {character}
#                 if room not in self.hand:
#                     print(f"{self} : adding {room} to knowledge")
#                     self.solution = (self.solution[0], room, self.solution[2])
#                     self.knowledge.add(room)
#                     self.is_not |= self.symbols["rooms"] - {room}
#                 if weapon not in self.hand:
#                     print(f"{self} : adding {weapon} to knowledge")
#                     self.solution = (self.solution[0], self.solution[1], weapon)
#                     self.knowledge.add(weapon)
#                     self.is_not |= self.symbols["weapons"] - {weapon}

#             if agent is not self:
#                 if revealed is None:
#                     return self.reveal_in_hand(guess)
#                 return None  # does not contain in hand

#         print(f"{self}: checking knowledge")
#         if self.solution[0] is None:
#             for symbol in self.symbols["characters"] - self.is_not:
#                 if self.knowledge.entails(symbol):  # character must be in solution
#                     self.solution = (symbol, self.solution[1], self.solution[2])
#                     self.is_not |= self.symbols["characters"] - {symbol}
#                     break
#         if self.solution[1] is None:
#             for symbol in self.symbols["rooms"] - self.is_not:
#                 if self.knowledge.entails(symbol):  # room must be in solution
#                     self.solution = (self.solution[0], symbol, self.solution[2])
#                     self.is_not |= self.symbols["rooms"] - {symbol}
#                     break
#         if self.solution[2] is None:
#             for symbol in self.symbols["weapons"] - self.is_not:
#                 if self.knowledge.entails(symbol):  # weapon must be in solution
#                     self.solution = (self.solution[0], self.solution[1], symbol)
#                     self.is_not |= self.symbols["weapons"] - {symbol}
#                     break
    
#         if any(card is None for card in self.solution):
#             return self.guess()  # makes a guess
#         else:
#             return self.solution

#     def __repr__(self) -> str:
#         return "🕵️"


class CluedoGame(Environment):
    def __init__(self, partial: bool = False):
        super().__init__()

        characters, rooms, weapons = create_symbols()
        if partial:
            characters = sample(characters, 4)
            rooms      = sample(rooms,      4)
            weapons    = sample(weapons,    4)
        
        self.cards   : dict[str, Card]          = {
                "characters": characters,
                "rooms": rooms,
                "weapons": weapons
            }
        self.players  : list[CluedoAgent] = []
        self.player   : int               = -1
        self.guess    : Guess             = (None, None, None)
        self.revealed : Union[Card, None] = None

        
    def __repr__(self) -> str:
        return "♟️"
        
    def add_agent(self, agent: CluedoAgent, *args, **kwargs) -> None:
        """ adds agent to player list and environment """
        if agent in self.players:
            raise ValueError(f"agent {agent} already signed up to play")
        self.players.append(agent)
        return super().add_agent(agent, *args, **kwargs)


    def add_player(self, player: CluedoAgent) -> None:
        """ adds player, alias for add_agent """
        return self.add_agent(player)

    @property
    def deck(self) -> set[Card]:
        """ returns all cards in the deck """
        return set.union(*self.cards.values())


    def deal(self) -> None:
        """ deal cards to agents """
        n_players = len(self.players)
        deck = deque(self.deck - set(self.__solution))
        hands = {player: set() for player in range(n_players)}
        player = 0
        random.shuffle(deck)
        while len(deck) > 0:
            hands[player].add(deck.pop())
            player = (player + 1) % n_players
        print(f"dealing hands {hands}")
        for player in range(n_players):
            self.players[player].receive_hand(hands[player])


    def step(self) -> None:
        """ a single turn in cluedo """
        n_players = len(self.players)
        
        if self.player < 0:  # first turn
           self.__solution = (
                choice(self.cards["characters"]),
                choice(self.cards["rooms"]),
                choice(self.cards["weapons"])
            )
           self.deal()
        self.player = (self.player + 1) % n_players
        self.guess, self.revealed = (None, None, None), None
        
        order = permute_indices(n_players, self.player)
        for i in order:
            agent = self.players[i]
            self._take_turns(agent)
            if self.revealed is not None:
                for _agent in self.players:
                    if isinstance(_agent, LogicalAgent) and  \
                            (agent is not _agent 
                                or agent is not self.players[self.player]):
                        self._take_turns(_agent)
                break  # card revealed, show to player
        # reveal card, if any, to player
        agent = self.players[self.player]
        self._take_turns(agent)

        if self.is_done:
            print(f"{self}: {agent} won with guess {self.guess}")
            print(f"{self}: Task environment complete. No further actions.")
            return

    def _take_turns(self, agent: CluedoAgent):
        print(f"{agent} <- {self.state}")
        action = agent.program(self.percept(agent))
        self.execute_action(agent, action)

    def percept(self, agent: CluedoAgent):
        return self.state
    
    def execute_action(self, 
                       agent: CluedoAgent,
                       action: Union[Guess, Card, None]) -> None:
        match action:
            case tuple():  # Guess
                print(f"{agent} guessed {action}")
                self.guess = action
            case Proposition():  # Card
                print(f"{agent} revealed {action} to {self.state[0]}")
                self.revealed = action
            case None: 
                if agent is not self.state[0]:  # no card revealed
                    print(f"{agent} didn't have a card to show {self.state[0]}")
            case _:
                raise TypeError(f"action {action} had invalid type, must be Union[tuple, Proposition, None]")

    @property
    def state(self) -> tuple[CluedoAgent, Guess, Union[Card,None]]:
        return (self.players[self.player], self.guess, self.revealed)

    @property
    def is_done(self) -> bool:
        try:
            return (self.guess == self.__solution) | super().is_done
        except:
            return False


if __name__ == "__main__":
    environment = CluedoGame(partial=True)
    cards = environment.cards
    player0 = CluedoAgent(cards, "0")
    # player1 = CluedoLogicalAgent(cards)
    player2 = CluedoAgent(cards, "2")
    player3 = CluedoAgent(cards, "3")

    environment.add_player(player0)
    # environment.add_player(player1)
    environment.add_player(player2)
    # environment.add_player(player3)

    environment.run()