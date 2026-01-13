# ailab.py - Simple library to print ML algorithm codes

code_1 = '''# Tic-Tac-Toe using Minimax Algorithm

def printBoard(board):
    for row in board:
        print(" ".join(row))

def isWinner(board, p):
    for i in range(3):
        if all(board[i][j] == p for j in range(3)):
            return True
        if all(board[j][i] == p for j in range(3)):
            return True
        
    if all(board[i][i] == p for i in range(3)):
        return True
    if all(board[2-i][i] == p for i in range(3)):
        return True

def isFull(board):
    for i in range(3):
        for j in range(3):
            if board[i][j] == ' ':
                return False
    return True

def minimax(d, board, isMax):
    if isWinner(board,'O'):
        return 1
    if isWinner(board,'X'):
        return -1
    if isFull(board):
        return 0
    
    if isMax:
        best = -1000
        for i in range(3):
            for j in range(3):
                if board[i][j] == ' ':
                    board[i][j] = 'O'
                    val = minimax(d+1, board, False)
                    best = max(val, best)
                    board[i][j] = ' '
        return best
    else:
        best = 1000
        for i in range(3):
            for j in range(3):
                if board[i][j] == ' ':
                    board[i][j] = 'X'
                    val = minimax(d+1, board, True)
                    best = min(val, best)
                    board[i][j] = ' '
        return best

def bestMove(board):
    best = -1000
    best_move = None
    for i in range(3):
        for j in range(3):
            if board[i][j] == ' ':
                board[i][j] = 'O'
                val = minimax(0, board, False)
                if val > best:
                    best = val
                    best_move = (i,j)
                board[i][j] = ' '
    return best_move

def playGame():
    board = [
        [' ',' ',' '],
        [' ',' ',' '],
        [' ',' ',' ']
    ]
    
    while True:
        while True:
            i,j = map(int, input("move: ").split())
            if 0 <= i < 3 and 0 <= j < 3 and board[i][j] == ' ':
                break
            else:
                print("retry")
        board[i][j] = 'X'
        printBoard(board)
        if isWinner(board,'X') or isFull(board):
            break
        
        x,y = bestMove(board)
        board[x][y] = 'O'
        printBoard(board)
        if isWinner(board, 'O') or isFull(board):
            break

playGame()
'''

code_2 = '''# Alpha-Beta Pruning Algorithm

MAX,MIN=1000,-1000

def minmax(depth,nodeIndex,maximizing_player,values,alpha,beta):
    if depth==3:
        return values[nodeIndex]
    if maximizing_player:
        best=MIN
        for i in range(0,2):
            val=minmax(depth+1,nodeIndex*2+i,False,values,alpha,beta)
            best=max(best,val)
            alpha=max(alpha,best)
            if beta<=alpha:
                break
        return best
    else:
        best=MAX
        for i in range(0,2):
            val=minmax(depth+1,nodeIndex*2+i,True,values,alpha,beta)
            best=min(best,val)
            beta=min(beta,best)
            if beta<=alpha:
                break
        return best
        

if __name__=='__main__':
    values=[3, 5, 6, 9, 1, 2, 0, -1]  # CHANGE VALUES HERE
    print("The optimal value is ",minmax(0,0,True,values,MIN,MAX))
'''

code_3 = '''# A* Search Algorithm (8-Puzzle Problem)

initial_state = [
    [1,2,3],
    [8,0,4],
    [7,6,5]
]

# CHANGE GOAL STATE HERE
goal_state = [
    [1,2,3],
    [8,4,5],
    [7,6,0]
]

def find_zero(state):
    for i in range(3):
        for j in range(3):
            if(state[i][j] == 0):
                return i,j

def move_up(state):
    i,j = find_zero(state)
    if i > 0:
        new_state = [row[:] for row in state]
        new_state[i][j], new_state[i-1][j] = new_state[i-1][j], new_state[i][j]
        return new_state
    return None

def move_down(state):
    i,j = find_zero(state)
    if i < 2:
        new_state = [row[:] for row in state]
        new_state[i][j], new_state[i+1][j] = new_state[i+1][j], new_state[i][j]
        return new_state
    return None
        
def move_right(state):
    i,j = find_zero(state)
    if j < 2:
        new_state = [row[:] for row in state]
        new_state[i][j], new_state[i][j+1] = new_state[i][j+1], new_state[i][j]
        return new_state
    return None

def move_left(state):
    i,j = find_zero(state)
    if j > 0:
        new_state = [row[:] for row in state]
        new_state[i][j], new_state[i][j-1] = new_state[i][j-1], new_state[i][j]
        return new_state
    return None

def heuristic(state):
    count = 0
    for i in range(3):
        for j in range(3):
            if state[i][j] != 0 and state[i][j] != goal_state[i][j]:
                count += 1
    return count

def astar_search():
    OPEN = [(heuristic(initial_state), 0, initial_state)]
    CLOSED = []
    
    found = False
    while OPEN:
        OPEN.sort(key=lambda x: x[0])
        f, g, current = OPEN.pop(0)
        
        if current == goal_state:
            print("Solution found!")
            print(current)
            found = True
            break
        
        CLOSED.append(current)
        
        neighbors = [move_up(current), move_right(current), move_left(current), move_down(current)]
        
        for s in neighbors:
            if s is not None and s not in CLOSED:
                h = heuristic(s)
                new_g = g + 1
                new_f = new_g + h
                
                if not any(x[2] == s for x in OPEN):
                    OPEN.append((new_f, new_g, s))

    if not found:
        print("solution not found")

astar_search()
'''

code_4 = '''# Hill Climbing Algorithm

def f(x):
    return -x**2 + 10*x + 5  # CHANGE FUNCTION HERE

def hillClimb(fn , initial_x, step_size = 0.1, max_iteration = 1000):
    curr_x = initial_x
    curr_value = fn(curr_x)

    for i in range(max_iteration):
        px = curr_x + step_size
        nx = curr_x - step_size

        pv = fn(px)
        nv = fn(nx)

        best_x = curr_x
        best_value = curr_value

        if nv > best_value:
            best_value = nv
            best_x = nx
        if pv > best_value:
            best_value = pv
            best_x = px

        if best_value > curr_value:
            curr_x = best_x
            curr_value = best_value
        else:
            print(f"--- Stopping: Local maximum found at iteration {i+1} ---")
            break
    return curr_x, curr_value

start_point = 1  # CHANGE START POINT HERE

final_x, final_val = hillClimb(f, start_point)

print("\\n-------------------------")
print(f"FINAL RESULT:")
print(f"   Local Maximum found at x = {final_x:.4f}")
print(f"   Maximum Function Value f(x) = {final_val:.4f}")
print("-------------------------")
'''

code_5 = '''# Logistic Regression from Scratch

import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from sklearn.datasets import load_iris
from sklearn.preprocessing import StandardScaler

# CHANGE DATASET HERE
iris = load_iris()
Xx = iris.data[:, :2]
y = (iris.target != 0).astype(int)

sc = StandardScaler()
Xx = sc.fit_transform(Xx)

xtr, xts, ytr, yts = train_test_split(Xx,y,test_size=0.2, random_state=42)

class LogisticRegression:
    def _sigmoid(self, z):
        return 1 / (1 + np.exp(-z))
    
    def train(self, X, y, lr=0.01, maxn = 100):
        self.weights = np.zeros(X.shape[1])
        for i in range(maxn):
            z = np.dot(X, self.weights)
            yh = self._sigmoid(z)
            er = yh - y

            grad = np.dot(X.T, er)/y.shape[0]
            self.weights = self.weights - lr*grad

    def test(self,X):
        z = np.dot(X, self.weights)
        y_h = self._sigmoid(z)
        return (y_h > 0.5).astype(int)


model = LogisticRegression()
model.train(xtr, ytr)

yp = model.test(xts)

print(classification_report(yp, yts))
'''

code_6 = '''# Naive Bayes Classifier from Scratch

import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from sklearn.datasets import load_iris

# CHANGE DATASET HERE
iris = load_iris()
Xx = iris.data
y = iris.target

xtr, xts, ytr, yts = train_test_split(Xx,y,test_size=0.2, random_state=42)

class NaiveBayes:
    def train(self, X, y):
        self.classes = np.unique(y)
        self.priors = {}
        self.parameters = {}

        for c in self.classes:
            X_c = X[y == c]

            self.priors[c] = len(X_c)/len(X)
            self.parameters[c] = {
                'mean': np.mean(X_c, axis=0),
                'var': np.var(X_c, axis=0)
            }
        return self

    def _gaussian(self, x, mean, var):
        ex = -(x - mean)**2/(2*var)
        de = np.sqrt(2*np.pi*var)

        return 1/de * np.exp(ex)

    def _calculate_posteriors(self, x):
        posteriors = {}

        for c in self.classes:
            log_pos = np.log(self.priors[c])

            mean = self.parameters[c]['mean']
            var = self.parameters[c]['var']
            for i in range(len(x)):
                log_pos += self._gaussian(x[i], mean[i], var[i])
            posteriors[c] = log_pos
        return posteriors

    def _predict_one(self, x):
        posteriors = self._calculate_posteriors(x)
        return max(posteriors, key=posteriors.get)

    def predict(self, X):
        return [self._predict_one(x) for x in X]

model = NaiveBayes()
model.train(xtr, ytr)

yp = model.predict(xts)

print(classification_report(yp, yts))
'''

code_7 = '''# k-Nearest Neighbors (kNN) from Scratch

import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from sklearn.datasets import load_iris
from collections import Counter

# CHANGE DATASET HERE
iris = load_iris()
Xx = iris.data
y = iris.target

xtr, xts, ytr, yts = train_test_split(Xx,y,test_size=0.2, random_state=42)

class kNN:
    def __init__(self, k):
        self.k = k

    def train(self, X, y):
        self.classes = y
        self.points = X

    def _predict_one(self, x):
        distances = [np.linalg.norm(x - i) for i in self.points]
        k_indices = np.argsort(distances)[:self.k]
        k_labels = [self.classes[i] for i in k_indices]

        ctr = Counter(k_labels)
        return ctr.most_common(1)[0][0]

    def predict(self, X):
        return [ self._predict_one(x) for x in X ]

model = kNN(3)  # CHANGE k VALUE HERE
model.train(xtr, ytr)

yp = model.predict(xts)

print(classification_report(yp, yts))
'''

code_8 = '''# k-Means Clustering from Scratch

import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from sklearn.datasets import make_blobs

import matplotlib.pyplot as plt

class kMeans:
    def __init__(self, k, maxn = 100):
        self.k = k
        self.maxn = maxn

    def fit(self, X):
        random_indices = np.random.permutation(X.shape[0])
        self.centroids = X[random_indices[:self.k]]

        for i in range(self.maxn):
            distances = np.array([ np.linalg.norm(X - c, axis=1) for c in self.centroids ])
            self.labels = np.argmin(distances, axis=0)

            new_centroids = np.array([ X[self.labels == k].mean(axis=0) for k in range(self.k) ])

            if np.all(self.centroids == new_centroids):
                break

            self.centroids = new_centroids

# CHANGE DATASET HERE
X, y = make_blobs(n_samples=300, centers=3)

model = kMeans(k=3)  # CHANGE k VALUE HERE
model.fit(X)

plt.scatter(X[:, 0], X[:, 1], c=model.labels, cmap = 'viridis')
plt.scatter(model.centroids[:,0], model.centroids[:,1], c='red')
plt.show()
'''


# Helper function to list all codes
def list_all():
    """Print list of all available codes"""
    print("Available codes:")
    print("code_1 - Tic-Tac-Toe (Minimax)")
    print("code_2 - Alpha-Beta Pruning")
    print("code_3 - A* Search")
    print("code_4 - Hill Climbing")
    print("code_5 - Logistic Regression")
    print("code_6 - Naive Bayes")
    print("code_7 - k-Nearest Neighbors")
    print("code_8 - k-Means Clustering")