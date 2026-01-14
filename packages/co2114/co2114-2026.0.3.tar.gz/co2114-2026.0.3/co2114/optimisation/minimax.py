from ..agent.environment import XYEnvironment
from ..search.things import *
from numpy import inf, min, max

from copy import deepcopy

class Tile(Thing):
    def __init__(self, player=None):
        self.player = player
        self.min_val, self.max_val = inf, -inf
    
    def __repr__(self):
        return self.player if self.player else " "


class TicTacToeGame(XYEnvironment):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, width=3, height=3, **kwargs)
        self.board = [[Tile() for j in range(3)] for i in range(3)]
        self.in_play = True

    @property
    def is_done(self):
        if len(self.agents) == 0: return True
        return not self.in_play

    def step(self):
        if self.is_done: return
        def get_position():
            print(self)
            i = int(input("choose move row [1-3]"))-1
            j = int(input("choose move column [1-3]"))-1
            return i,j
        i,j = get_position()
        placed = False
        if not self.board[i][j].player:
            self.board[i][j].player = "X" if self.agent.player == "O" else "O"
            placed = True
        while(not placed):
            print("not a valid move !")
            i,j = get_position()
            if (i < 0 or i > 2 or j < 0 or j > 2):
                continue
            if not self.board[i][j].player:
                self.board[i][j].player = "X" if self.agent.player == "O" else "O"
                placed = True
        print(self)
        super().step()
    
    def __repr__(self):
        board = ""
        for i in (0,1):
            board += f"_{self.board[i][0]}_|_{self.board[i][1]}_|_{self.board[i][2]}_"
            board += "\n"
        board += f" {self.board[2][0]} | {self.board[2][1]} | {self.board[2][2]} "
        return board[:-1]
    
    def add_agent(self, agent, player="X"):
        if not isinstance(agent, Agent):
            raise TypeError(f"{self}: {agent} is not an Agent")
        self.agents.add(agent)
        self.agent = agent
        self.agent.player = "X"

    def percept(self, agent):
        return self.board

    def execute_action(self, agent, action):
        command, state = action
        print(action)
        match command:
            case "move":
                self.board = agent.move(state)
            case "done":
                self.in_play = False


class MinimaxAgent(UtilityBasedAgent):

    def to_move(self, state):
        NotImplemented

    def moves(self, state):
        NotImplemented

    def score(self, state):
        NotImplemented
    
    def minimax_utility(self, state):
        match self.to_move(state):
            case "min":
                return min(
                    [self.minimax_utility(move) for move in self.moves(state)])
            case "max":
                return max(
                    [self.minimax_utility(move) for move in self.moves(state)])
            case "terminal":
                return self.score(state)

    def utility(self, action):
        _, state = action
        return self.minimax_utility(state)
    
    def program(self,percepts):
        print(f"{self}: thinking ...")
        state = percepts
        if self.to_move(state) == "terminal":
            return ("done", state)
        
        max_objective = -inf
        action = self.maximise_utility(
            [("move", move) for move in self.moves(state)])
        
        return action
    

class TicTacToeAgent(MinimaxAgent):
    def __repr__(self):
        if hasattr(self, "player"):
            return self.player
        return super().__repr__()
        
    def score(self, state):
        draw = True  # check
        index = lambda x,i,j: x[i][j]
        def is_win(check):
            if all(index(state, *idx).player == tile.player for idx in check):
                return True
            return False
        
        for i in range(3):
            for j in range(3):
                tile = index(state,i,j)
                if not tile.player:  # is empty
                    draw = False
                    continue
                check = [
                    [((i_+1)%3, j) for i_ in range(i, i+2)],
                    [(i,(j_+1)%3) for j_ in range(j, j+2)]]
                if i==j:
                    check.append([((i_+1)%3, (i_+1)%3) for i_ in range(i, i+2)])
                if i+j == 2:
                    check.append([((i_+1)%3, (2-(i_+1)%3)%3) for i_ in range(i, i+2)])
                if any(is_win(idxs) for idxs in check):
                    return 1 if tile.player == self.player else -1
        
        return 0 if draw else None

    def move(self, state):
        return state
    
    def moves(self, state):
        to_move = self.to_move(state)
        if self.player == "X":
            player = "X" if to_move == "max" else "O"
        else:
            player = "O" if to_move == "max" else "X"
        possible_moves = []
        for i in range(3):
            for j in range(3):
                if not state[i][j].player:
                    move = deepcopy(state)#.copy()
                    move[i][j] = Tile(player)
                    possible_moves.append(move)
        return possible_moves

    def to_move(self, state):
        if self.score(state) is not None:
            return "terminal"
        moves_made = {"X":0, "O":0}
        for i in range(3):
            for j in range(3):
                if state[i][j].player:
                    moves_made[state[i][j].player] += 1
        match self.player:
            case "X":
                return "max" if moves_made["X"] < moves_made["O"] else "min"
            case "O":
                return "max" if moves_made["O"] < moves_made["X"] else "min"


if __name__ == "__main__":
    env = TicTacToeGame()
    env.add_agent(TicTacToeAgent())
    env.run()