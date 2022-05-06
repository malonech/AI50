"""
Tic Tac Toe Player
"""

import copy
import math

X = "X"
O = "O"
EMPTY = None


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board.
    """
    x_count = 0
    y_count = 0

    for row in board:
        for column in row:
            if column == X:
                x_count += 1
            elif column == O:
                y_count += 1
    if x_count > y_count:
        return O
    else:
        return X


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    moves = []

    for i in range(3):
        for j in range(3):
            if board[i][j] == EMPTY:
                moves.append((i, j))
    return moves


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """

    #Copy Board
    board_copy = copy.deepcopy(board)

    turn = player(board)
    (i, j) = action

    if board[i][j] != EMPTY:
        raise NameError("Invalid Move")
    else:
        board_copy[i][j] = turn

    return board_copy


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    #Counters
    x_count = 0
    o_count = 0

    #Check X diagonal
    if board[0][0] == X:
        if board[1][1] == X:
            if board[2][2] == X:
                return X
    if board[0][2] == X:
        if board[1][1] == X:
            if board[2][0] == X:
                return X

    #Check O diagonal
    if board[0][0] == O:
        if board[1][1] == O:
            if board[2][2] == O:
                return O
    if board[0][2] == O:
        if board[1][1] == O:
            if board[2][0] == O:
                return O

    #Check Rows
    for i in range(3):
        for j in range(3):
            if board[i][j] == X:
                x_count += 1
            if board[i][j] == O:
                o_count += 1
        if x_count == 3:
            return X
        elif o_count == 3:
            return O
        x_count = 0
        o_count = 0

    #Check columns
    for i in range(3):
        for j in range(3):
            if board[j][i] == X:
                x_count += 1
            if board[j][i] == O:
                o_count += 1
        if x_count == 3:
            return X
        elif o_count == 3:
            return O
        x_count = 0
        o_count = 0

    return None


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    if winner(board) == X or winner(board) == O:
        return True
    for i in range(3):
        for j in range(3):
            if board[i][j] == EMPTY:
                return False
    return True

def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    if winner(board) == X:
        return 1
    if winner(board) == O:
        return -1
    if winner(board) == None:
        return 0


def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    #Check board for empty square
    empty_square = 0

    if terminal(board):
        return None

    #Check whose turn it is
    current_player = player(board)

    #Run Minimax for X
    if current_player == X:
        v = -math.inf
        for action in actions(board):
            if Min_Value(result(board, action)) > v:
                v = Min_Value(result(board, action))
                best_action = action
        return best_action
    # Run Minimax for O
    elif current_player == O:
        v = math.inf
        for action in actions(board):
            if Max_Value(result(board, action)) < v:
                v = Max_Value(result(board, action))
                best_action = action
        return best_action






def Max_Value(board):
    '''
    Determines maximum value of a gameboard state
    '''
    if terminal(board) == True:
        return utility(board)

    v = -math.inf

    for action in actions(board):
        v = max(v,Min_Value(result(board, action)))
    return v


def Min_Value(board):
    '''
    Determines minimum value of a gameboard state
    '''
    if terminal(board) == True:
        return utility(board)

    v = math.inf

    for action in actions(board):
        v = min(v,Max_Value(result(board, action)))
    return v
