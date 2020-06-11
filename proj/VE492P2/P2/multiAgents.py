from util import manhattanDistance
from game import Directions
import random, util

from game import Agent


class ReflexAgent(Agent):
    """
    A reflex agent chooses an action at each choice point by examining
    its alternatives via a state evaluation function.

    The code below is provided as a guide.  You are welcome to change
    it in any way you see fit, so long as you don't touch our method
    headers.
    """

    def getAction(self, gameState):
        """
        You do not need to change this method, but you're welcome to.

        getAction chooses among the best options according to the evaluation function.

        Just like in the previous project, getAction takes a GameState and returns
        some Directions.X for some X in the set {NORTH, SOUTH, WEST, EAST, STOP}
        """
        # Collect legal moves and successor states
        legalMoves = gameState.getLegalActions()

        # Choose one of the best actions
        scores = [self.evaluationFunction(gameState, action) for action in legalMoves]
        bestScore = max(scores)
        bestIndices = [index for index in range(len(scores)) if scores[index] == bestScore]
        chosenIndex = random.choice(bestIndices)  # Pick randomly among the best

        "Add more of your code here if you want to"

        return legalMoves[chosenIndex]

    def evaluationFunction(self, currentGameState, action):
        """
        Design a better evaluation function here.

        The evaluation function takes in the current and proposed successor
        GameStates (pacman.py) and returns a number, where higher numbers are better.

        The code below extracts some useful information from the state, like the
        remaining food (newFood) and Pacman position after moving (newPos).
        newScaredTimes holds the number of moves that each ghost will remain
        scared because of Pacman having eaten a power pellet.

        Print out these variables to see what you're getting, then combine them
        to create a masterful evaluation function.
        """
        # Useful information you can extract from a GameState (pacman.py)
        successorGameState = currentGameState.generatePacmanSuccessor(action)
        newPos = successorGameState.getPacmanPosition()
        newFood = successorGameState.getFood()
        newGhostStates = successorGameState.getGhostStates()
        newScaredTimes = [ghostState.scaredTimer for ghostState in newGhostStates]

        utility = successorGameState.getScore()
        food_reward = 10
        ghost_reward = -15
        die_reward = -500

        distance_to_ghost = [manhattanDistance(newPos, ghost.getPosition()) for ghost in newGhostStates]
        if len(distance_to_ghost):
            min_ghost_dist = min(distance_to_ghost)
            if min_ghost_dist == 0:
                utility += die_reward
            else:
                utility += ghost_reward / min_ghost_dist

        distance_to_food = [manhattanDistance(newPos, x) for x in newFood.asList()]
        if len(distance_to_food):
            min_food_dist = min(distance_to_food)
            utility += food_reward / min_food_dist
        return utility


def scoreEvaluationFunction(currentGameState):
    """
    This default evaluation function just returns the score of the state.
    The score is the same one displayed in the Pacman GUI.

    This evaluation function is meant for use with adversarial search agents
    (not reflex agents).
    """
    return currentGameState.getScore()


class MultiAgentSearchAgent(Agent):
    """
    This class provides some common elements to all of your
    multi-agent searchers.  Any methods defined here will be available
    to the MinimaxPacmanAgent, AlphaBetaPacmanAgent & ExpectimaxPacmanAgent.

    You *do not* need to make any changes here, but you can if you want to
    add functionality to all your adversarial search agents.  Please do not
    remove anything, however.

    Note: this is an abstract class: one that should not be instantiated.  It's
    only partially specified, and designed to be extended.  Agent (game.py)
    is another abstract class.
    """

    def __init__(self, evalFn='scoreEvaluationFunction', depth='2'):
        self.index = 0  # Pacman is always agent index 0
        self.evaluationFunction = util.lookup(evalFn, globals())
        self.depth = int(depth)

    def is_goal_state(self, state, depth):
        return state.isWin() or state.isLose() or \
               depth == self.depth


class MinimaxAgent(MultiAgentSearchAgent):
    """
    Your minimax agent (question 2)
    """

    def getAction(self, gameState):
        """
        Returns the minimax action from the current gameState using self.depth
        and self.evaluationFunction.

        Here are some method calls that might be useful when implementing minimax.

        gameState.getLegalActions(agentIndex):
        Returns a list of legal actions for an agent
        agentIndex=0 means Pacman, ghosts are >= 1

        gameState.generateSuccessor(agentIndex, action):
        Returns the successor game state after an agent takes an action

        gameState.getNumAgents():
        Returns the total number of agents in the game

        gameState.isWin():
        Returns whether or not the game state is a winning state

        gameState.isLose():
        Returns whether or not the game state is a losing state
        """
        "*** YOUR CODE HERE ***"
        pacman_agent = 0
        initial_depth = 0

        def next_agent(agent, agent_number):
            return (agent + 1) % agent_number

        def max_value(agent, state, depth):
            if self.is_goal_state(state, depth):
                return self.evaluationFunction(state)
            actions = state.getLegalActions(agent)
            agent_number = state.getNumAgents()
            return max([min_value(next_agent(agent, agent_number), state.generateSuccessor(agent, action), depth)
                        for action in actions])

        def min_value(agent, state, depth):
            if self.is_goal_state(state, depth):
                return self.evaluationFunction(state)
            actions = state.getLegalActions(agent)
            agent_number = state.getNumAgents()

            if next_agent(agent, agent_number) == pacman_agent:
                return min(
                    [max_value(pacman_agent, state.generateSuccessor(agent, action), depth + 1) for action in actions])
            else:
                return min(
                    [min_value(next_agent(agent, agent_number), state.generateSuccessor(agent, action), depth) for
                     action in actions])

        return max(gameState.getLegalActions(pacman_agent),
                   key=lambda action: min_value(next_agent(pacman_agent, gameState.getNumAgents()),
                                                gameState.generateSuccessor(pacman_agent, action), initial_depth))


class AlphaBetaAgent(MultiAgentSearchAgent):
    """
    Your minimax agent with alpha-beta pruning (question 3)
    """

    def getAction(self, gameState):
        """
        Returns the minimax action using self.depth and self.evaluationFunction
        """
        pacman_agent = 0

        def next_agent(agent, agent_number):
            return (agent + 1) % agent_number

        def max_value(agent, state, depth, alpha, beta):
            if self.is_goal_state(state, depth):
                return self.evaluationFunction(state)
            actions = state.getLegalActions(agent)
            agent_number = state.getNumAgents()
            value = -float('inf')
            for action in actions:
                next_state = state.generateSuccessor(agent, action)
                value = max(value, min_value(next_agent(agent, agent_number), next_state, depth, alpha, beta))
                if value > beta:
                    return value
                alpha = max(alpha, value)
            return value

        def min_value(agent, state, depth, alpha, beta):
            if self.is_goal_state(state, depth):
                return self.evaluationFunction(state)
            actions = state.getLegalActions(agent)
            agent_number = state.getNumAgents()
            value = float('inf')
            if next_agent(agent, agent_number) == pacman_agent:
                for action in actions:
                    next_state = state.generateSuccessor(agent, action)
                    value = min(value, max_value(next_agent(agent, agent_number), next_state, depth + 1, alpha, beta))
                    if value < alpha:
                        return value
                    beta = min(value, beta)
            else:
                for action in actions:
                    next_state = state.generateSuccessor(agent, action)
                    value = min(value, min_value(next_agent(agent, agent_number), next_state, depth, alpha, beta))
                    if value < alpha:
                        return value
                    beta = min(value, beta)
            return value

        initial_actions = gameState.getLegalActions(pacman_agent)
        taken_action = initial_actions[0]
        initial_value = -float('inf')
        initial_depth = 0
        initial_alpha = -float('inf')
        initial_beta = float('inf')
        for first_action in initial_actions:
            action_successor_value = min_value(next_agent(pacman_agent, gameState.getNumAgents()),
                                               gameState.generateSuccessor(pacman_agent, first_action), initial_depth,
                                               initial_alpha, initial_beta)
            if initial_value < action_successor_value:
                taken_action = first_action
                initial_value = action_successor_value
            if initial_value > initial_beta:
                return initial_value, taken_action
            initial_alpha = max(initial_value, initial_alpha)
        # todo: i don't know
        return taken_action


class ExpectimaxAgent(MultiAgentSearchAgent):
    """
      Your expectimax agent (question 4)
    """

    def getAction(self, gameState):
        """
        Returns the expectimax action using self.depth and self.evaluationFunction

        All ghosts should be modeled as choosing uniformly at random from their
        legal moves.
        """
        "*** YOUR CODE HERE ***"
        util.raiseNotDefined()


def betterEvaluationFunction(currentGameState):
    """
    Your extreme ghost-hunting, pellet-nabbing, food-gobbling, unstoppable
    evaluation function (question 5).

    DESCRIPTION: <write something here so we know what you did>
    """
    "*** YOUR CODE HERE ***"
    util.raiseNotDefined()


# Abbreviation
better = betterEvaluationFunction
