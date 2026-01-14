
from .utils import format_snippet

def monte_carlo_code():
    code = '''
import numpy as np
import gymnasium as gym
import matplotlib.pyplot as plt

env = gym.make('FrozenLake-v1', is_slippery = 'False')

def monte_carlo(env, policy, episodes = 10000, df = 0.99):
  V = np.zeros(env.observation_space.n)
  returns = {s:[] for s in range(env.observation_space.n)}
  V_hist = []

  for ep in range(episodes):
    episode = []
    state, _ = env.reset()
    done = False

    while not done:
      action = policy[state]
      next_state, reward, terminated, truncated, _ = env.step(action)
      done = terminated or truncated
      episode.append((state, reward))
      state = next_state

    G = 0
    visited_states = set()
    for s, r in reversed(episode):
      G = df * G + r
      if s not in visited_states:
        returns[s].append(G)
        V[s] = np.mean(returns[s])
        visited_states.add(s)

    V_hist.append(V.copy())
  return V, V_hist

np.random.seed(42)

policy = {s: np.random.choice([0, 1, 2, 3]) for s in range(env.observation_space.n)}
V_MC, V_MC_hist = monte_carlo(env, policy)
print("Monte Carlo Value: ")
print(V_MC)

def convergence(V_track, title):
  plt.figure(figsize = (8, 5))
  for s in range(env.observation_space.n):
    values = [v[s] for v in V_track]
    plt.plot(values, label = f"State {s}")

  plt.title(title)
  plt.xlabel("Episodes")
  plt.ylabel("Value")
  plt.legend()
  plt.grid(True)
  plt.show()

convergence(V_MC_hist, "Monte Carlo Value Convergence")
'''
    return format_snippet(code)

def td_code():
    code = '''
import numpy as np
import gymnasium as gym
import matplotlib.pyplot as plt

env = gym.make('FrozenLake-v1', is_slippery = 'False')

def temp_diff(env, policy, episodes = 10000, lr = 0.05, df = 0.99):
  V = np.zeros(env.observation_space.n)
  V_hist = []

  for ep in range(episodes):
    episode = []
    state, _ = env.reset()
    done = False

    while not done:
      action  = policy[state]
      next_state, reward, terminated, truncated , _ = env.step(action)
      done = terminated or truncated
      V[state] = V[state] + lr * (reward + df * V[next_state] - V[state])
      state = next_state
    V_hist.append(V.copy())
  return V, V_hist

np.random.seed(42)

policy = {s: np.random.choice([0, 1, 2, 3]) for s in range(env.observation_space.n)}
V_TD, V_TD_hist = temp_diff(env, policy)

print("Temporal Difference Value: ")
print(V_TD)

def convergence(V_track, title):
  plt.figure(figsize = (8, 5))
  for s in range(env.observation_space.n):
    values = [v[s] for v in V_track]
    plt.plot(values, label = f"State {s}")

  plt.title(title)
  plt.xlabel("Episodes")
  plt.ylabel("Value")
  plt.legend()
  plt.grid(True)
  plt.show()

convergence(V_TD_hist, "Temporal Difference Value Convergence")
'''
    return format_snippet(code)

def complete_policy_iteration_code():
    code = '''
import gymnasium as gym
import numpy as np
import matplotlib.pyplot as plt

env = gym.make('FrozenLake-v1', is_slippery=True, render_mode='ansi')
P = env.unwrapped.P
env.reset()

nS = env.observation_space.n
nA = env.action_space.n

print(f'Action space: {nA}')
print(f'Observation space: {nS}')
print(f'Reward range: {env.unwrapped.reward_range}')

print(env.render())
print(P)

random_policy=np.ones([env.observation_space.n, env.action_space.n])/env.action_space.n
gamma=0.9

def policy_evaluation(env, policy, V, gamma=1.0, theta=1e-8):
    V_history = [V.copy()]
    while True:
        delta = 0
        for s in range(env.observation_space.n):
            v = 0
            for a, action_prob in enumerate(policy[s]):
                for prob, next_state, reward, done in P[s][a]:
                    v += action_prob * prob * (reward + gamma * V[next_state])
            delta = max(delta, abs(v - V[s]))
            V[s] = v
        V_history.append(V.copy())

        if delta < theta:
            break

    return V, V_history

def q_from_v(env, V, s, gamma=1):
  q = np.zeros(env.action_space.n)
  for a in range(env.action_space.n):
    for prob, next_state, reward, done in env.unwrapped.P[s][a]:
      q[a] += prob * (reward + gamma * V[next_state])
  return q

def plot_convergence(V_history):
  iterations = len(V_history) - 1
  max_diffs = []
  for i in range(iterations):
    diff = np.max(np.abs(V_history[i+1] - V_history[i]))
    max_diffs.append(diff)

  plt.figure()
  plt.plot(range(1, iterations + 1), max_diffs)
  plt.xlabel("Iteration")
  plt.ylabel("Max Change in V")
  plt.title("Policy Evaluation Convergence")
  plt.show()

def policy_iteration(env, gamma=1.0, theta=1e-8):
    nS = env.observation_space.n
    nA = env.action_space.n

    policy = np.ones([nS, nA]) / nA
    V = np.zeros(nS)

    iteration = 0
    policy_stable = False
    V_history = []

    while not policy_stable:
        iteration += 1

        V, current_V_history = policy_evaluation(env, policy, V, gamma, theta)
        if not V_history:
            V_history.extend(current_V_history)
        else:
             V_history.extend(current_V_history[1:])


        policy_stable = True
        for s in range(nS):
            old_action = np.argmax(policy[s])

            Q = q_from_v(env, V, s, gamma)
            best_action = np.argmax(Q)

            new_policy_s = np.eye(nA)[best_action]

            if not np.array_equal(policy[s], new_policy_s):
                policy_stable = False
                policy[s] = new_policy_s

    return policy, V, iteration, V_history

def plot(V, policy, discount_factor=1.0, draw_vals=True):
  nrow = env.unwrapped.nrow
  ncol = env.unwrapped.ncol
  nA = env.action_space.n
  arrow_symbols = {0: '←', 1: '↓', 2: '→', 3: '↑'}
  grid = np.reshape(V, (nrow, ncol))
  plt.figure(figsize=(6, 6))
  plt.imshow(grid, cmap='cool', interpolation='none')
  for s in range(nrow * ncol):
    row, col = divmod(s, ncol)
    best_action = np.argmax(policy[s])

    if draw_vals:
      plt.text(col, row, f'{V[s]:.2f}', ha='center', va='center', color='white', fontsize=10)
    else:
      plt.text(col, row, arrow_symbols[best_action], ha='center', va='center', color='white',
      fontsize=14)

  plt.title("Value Function" if draw_vals else "Optimal Policy") # Added title here
  plt.axis('off')
  plt.show()

V_random = np.random.rand(env.observation_space.n)
V_random.reshape(4, 4)

old_policy = random_policy
new_policy, latest_V, iterations, _ = policy_iteration(env, gamma=0.9)

print(f'Convergenced in {iterations} steps.')

plot(latest_V, new_policy, 1.0, draw_vals=True) #Value Function
plot(V_random, new_policy, 1.0, draw_vals=False) #Optimal Policy
'''
    return format_snippet(code)   

def complete_value_iteration_code():
    code = '''
import gymnasium as gym
import numpy as np
import matplotlib.pyplot as plt

env = gym.make('FrozenLake-v1', is_slippery=True, render_mode='ansi')
P = env.unwrapped.P
env.reset()

nS = env.observation_space.n
nA = env.action_space.n

print(f'Action space: {nA}')
print(f'Observation space: {nS}')
print(f'Reward range: {env.unwrapped.reward_range}')

print(env.render())
print(P)

random_policy=np.ones([env.observation_space.n, env.action_space.n])/env.action_space.n
gamma=0.9


def q_from_v(env, V, s, gamma=1):
  q = np.zeros(env.action_space.n)
  for a in range(env.action_space.n):
    for prob, next_state, reward, done in env.unwrapped.P[s][a]:
      q[a] += prob * (reward + gamma * V[next_state])
  return q

def plot_convergence(V_history):
  iterations = len(V_history) - 1
  max_diffs = []
  for i in range(iterations):
    diff = np.max(np.abs(V_history[i+1] - V_history[i]))
    max_diffs.append(diff)

  plt.figure()
  plt.plot(range(1, iterations + 1), max_diffs)
  plt.xlabel("Iteration")
  plt.ylabel("Max Change in V")
  plt.title("Policy Evaluation Convergence")
  plt.show()

def value_iteration(env, gamma=1.0, theta=1e-8):
    nS = env.observation_space.n
    nA = env.action_space.n
    
    V = np.zeros(nS)
    V_history = [V.copy()]  # track convergence
    
    while True:
        delta = 0
        
        for s in range(nS):
            # Compute Q(s,a) for each action
            Q = np.zeros(nA)
            for a in range(nA):
                for prob, next_state, reward, done in env.unwrapped.P[s][a]:
                    Q[a] += prob * (reward + gamma * V[next_state])
            
            # Best action value
            v_new = np.max(Q)
            delta = max(delta, abs(v_new - V[s]))
            V[s] = v_new
        
        V_history.append(V.copy())
        
        if delta < theta:
            break
    
    # Extract greedy policy
    policy = np.zeros([nS, nA])
    for s in range(nS):
        Q = q_from_v(env, V, s, gamma)
        best_a = np.argmax(Q)
        policy[s] = np.eye(nA)[best_a]
        
    return policy, V, V_history


def plot(V, policy, discount_factor=1.0, draw_vals=True):
  nrow = env.unwrapped.nrow
  ncol = env.unwrapped.ncol
  nA = env.action_space.n
  arrow_symbols = {0: '←', 1: '↓', 2: '→', 3: '↑'}
  grid = np.reshape(V, (nrow, ncol))
  plt.figure(figsize=(6, 6))
  plt.imshow(grid, cmap='cool', interpolation='none')
  for s in range(nrow * ncol):
    row, col = divmod(s, ncol)
    best_action = np.argmax(policy[s])

    if draw_vals:
      plt.text(col, row, f'{V[s]:.2f}', ha='center', va='center', color='white', fontsize=10)
    else:
      plt.text(col, row, arrow_symbols[best_action], ha='center', va='center', color='white',
      fontsize=14)

  plt.title("Value Function" if draw_vals else "Optimal Policy") # Added title here
  plt.axis('off')
  plt.show()

V_random = np.random.rand(env.observation_space.n)
V_random.reshape(4, 4)

old_policy = random_policy
new_policy, latest_V, iterations, _ = policy_iteration(env, gamma=0.9)

print(f'Convergenced in {iterations} steps.')

plot(latest_V, new_policy, 1.0, draw_vals=True) #Value Function
plot(V_random, new_policy, 1.0, draw_vals=False) #Optimal Policy
'''
    return format_snippet(code) 


def tensor_operations_code():
    code = '''
import torch
print("Pytorch Version:", torch.__version__)

if torch.cuda.is_available():
    print("GPU is available.")
else:
    print("GPU is not available.")

print("\nCreating Tensors")
#-----Scaler-----
t1 = torch.tensor(3)
print("\nScaler Tensor:", t1)
#-----Vector-----
t2 = torch.tensor([1, 2, 3, 4])
print("\nVector Tensor:", t2)
#-----3x3 Matrix-----
t3 = torch.rand(3, 3)
print("\n3x3 Matrix Tensor:", t3)
#-----3D Tensor (2x3x4)-----
t4 = torch.rand(2, 3, 4)
print("\n3D Tensor (2x3x4):\n", t4)

a = torch.tensor([[1., 2.], [4., 5.]])
b = torch.tensor([[7., 8.], [10., 11.]])

#-----Addition-----
sum = a + b
print("Addition:\n", sum)

#-----Multiplication-----
mul = a * b
print("Multiplication:\n", mul)

#-----Matrix Multiplication-----
matmul = torch.matmul(a, b)
print("Matrix Multiplication:\n", matmul)

#-----Mean-----
mean_a = torch.mean(a)
print("Mean 1st:\n", mean_a)

mean_b = torch.mean(b)
print("Mean 2nd:\n", mean_b)

#-----Sum-----
sum_a = torch.sum(a)
print("Matrix Sum 1st:\n", sum_a)

sum_b = torch.sum(b)
print("Matrix Sum 1st:\n", sum_b)

# Reshape a 1-D tensor
print("\n--- Reshaping Tensors ---")
tensor_1d = torch.arange(12)
print("Original 1D tensor (12 elements):", tensor_1d)

# Reshape to 3x4
reshaped_3x4 = tensor_1d.reshape(3, 4)
print("Reshaped to 3x4:\n", reshaped_3x4)

# Reshape to 2x6
reshaped_2x6 = tensor_1d.reshape(2, 6)
print("Reshaped to 2x6:\n", reshaped_2x6)

#Compute gradients for y = x^2
print("\n--- Computing Gradients (Autograd) ---")

# PyTorch Autograd
x_pt = torch.tensor(3.0, requires_grad=True)
y_pt = x_pt**2
y_pt.backward() # Compute gradient
print(f"PyTorch: Gradient of y = x^2 at x = {x_pt.item()} is dy/dx = {x_pt.grad.item()}")
    
'''
    return format_snippet(code)

def perceptron_operations_code():
    code = '''
import numpy
import pandas as pd
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
from sklearn.inspection import DecisionBoundaryDisplay
from sklearn.datasets import make_blobs
from sklearn.linear_model import Perceptron
from sklearn.metrics import accuracy_score, confusion_matrix

#Generate Dataset
X, y = make_blobs(n_samples=250, centers=2, random_state=12)
plt.scatter(X[:, 0], X[:, 1], c=y, s=50, edgecolor='k')
plt.show()

#Preprocessing
scaler = StandardScaler()
X = scaler.fit_transform(X)

plt.scatter(X[:, 0], X[:, 1], c=y, cmap=plt.cm.coolwarm, s=50, edgecolor='k')
plt.show()

# Train Perceptron
percy = Perceptron()
percy.fit(X, y)

#Visualize Boundary
DecisionBoundaryDisplay.from_estimator(percy, X, response_method="predict", cmap=plt.cm.coolwarm, alpha=0.8)
plt.scatter(X[:, 0], X[:, 1], c=y, cmap=plt.cm.coolwarm, s=50, edgecolors='k')
plt.title('Perceptron Decision Boundary (using sklearn.inspection)')
plt.xlabel('Feature 1 (Scaled)')
plt.ylabel('Feature 2 (Scaled)')
plt.show()

import seaborn as sns

# Evaluate performance
y_pred = percy.predict(X)

# Accuracy
accuracy = accuracy_score(y, y_pred)
print(f'Accuracy: {accuracy}')

# Confusion Matrix
conf_matrix = confusion_matrix(y, y_pred)
print('Confusion Matrix:')
print(conf_matrix)

percy_100 = Perceptron(random_state=0, max_iter=1000)
percy_100.fit(X, y)
print(percy_100.n_iter_) # Corrected attribute name
DecisionBoundaryDisplay.from_estimator(percy_100, X, response_method="predict", cmap=plt.cm.coolwarm, alpha=0.8)
plt.scatter(X[:, 0], X[:, 1], c=y, cmap=plt.cm.coolwarm, s=50, edgecolors='k')
plt.title('Perceptron Decision Boundary (using sklearn.inspection)')
plt.xlabel('Feature 1 (Scaled)')
plt.ylabel('Feature 2 (Scaled)')
plt.show()
    
'''
    return format_snippet(code)

def perceptron_manual_code():
    code = '''
#Manual Implementation of Perceptron

import numpy as np

# Perceptron implementation from scratch
class Perceptron:
    def __init__(self, input_size, learning_rate=0.1, epochs=10):
        self.weights = np.zeros(input_size + 1)  # +1 for bias
        self.lr = learning_rate
        self.epochs = epochs

    def activation(self, x):
        return 1 if x >= 0 else 0   # Step function

    def predict(self, x):
        z = np.dot(x, self.weights[1:]) + self.weights[0]  # w·x + bias
        return self.activation(z)

    def train(self, X, y):
        for _ in range(self.epochs):
            for xi, target in zip(X, y):
                update = self.lr * (target - self.predict(xi))
                self.weights[1:] += update * xi
                self.weights[0] += update  # bias update

# Example: Train on OR gate
X = np.array([
    [0, 0],
    [0, 1],
    [1, 0],
    [1, 1]
])
y = np.array([0, 1, 1, 1])  # OR gate output

p = Perceptron(input_size=2, learning_rate=0.1, epochs=10)
p.train(X, y)

print("Trained weights:", p.weights)
print("Predictions:")
for xi in X:
    print(f"{xi} -> {p.predict(xi)}")
    
'''
    return format_snippet(code)


def ADALINE_complete_code():
    code = '''
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, confusion_matrix, precision_score, recall_score, f1_score
from sklearn.datasets import load_iris
from sklearn.preprocessing import StandardScaler

# Optional comparison
try:
  from sklearn.linear_model import Perceptron
  SKLEARN_PERCEPTRON_AVAILABLE = True
except Exception:
  SKLEARN_PERCEPTRON_AVAILABLE = False

np.random.seed(42)

def to01(y_pm1):
  """Map labels from {-1, +1} to {0, 1} for metrics/plots."""
  y_pm1 = np.asarray(y_pm1).ravel()
  return ((y_pm1 + 1) // 2).astype(int)

def from01(y01):
  """Map labels from {0, 1} to {-1, +1}."""
  y01 = np.asarray(y01).ravel()
  return (2*y01 - 1).astype(int)
  
def plot_decision_boundary_2d(model, X, y_pm1, title="Decision boundary"):
  """Plot decision boundary for a 2D dataset.
  model must have: predict_labels_pm1(X) -> {-1,+1}
  """
  x_min, x_max = X[:, 0].min() - 1.0, X[:, 0].max() + 1.0
  y_min, y_max = X[:, 1].min() - 1.0, X[:, 1].max() + 1.0
  xx, yy = np.meshgrid(np.linspace(x_min, x_max, 200),
  np.linspace(y_min, y_max, 200))
  grid = np.c_[xx.ravel(), yy.ravel()]
  Z = model.predict_labels_pm1(grid).reshape(xx.shape)
  plt.figure(figsize=(6,5))
  plt.contourf(xx, yy, Z, alpha=0.2, levels=[-1,0,1])
  plt.scatter(X[:,0], X[:,1], c=to01(y_pm1), s=50)
  plt.title(title)
  plt.xlabel("x1")
  plt.ylabel("x2")
  plt.show()

def print_metrics(y_true_pm1, y_pred_pm1, split_name="Test"):
  y_true = to01(y_true_pm1)
  y_pred = to01(y_pred_pm1)
  acc = accuracy_score(y_true, y_pred)
  cm = confusion_matrix(y_true, y_pred)
  prec = precision_score(y_true, y_pred, zero_division=0)
  rec = recall_score(y_true, y_pred, zero_division=0)
  f1 = f1_score(y_true, y_pred, zero_division=0)
  print(f"=== {split_name} Metrics ===")
  print(f"Accuracy: {acc:.4f}")
  print("Confusion Matrix:\n", cm)
  print(f"Precision: {prec:.4f}")
  print(f"Recall: {rec:.4f}")
  print(f"F1-score: {f1:.4f}")

#ADALINE NUMPY

class ADALINE:
  def __init__(self, lr=0.01, epochs=50):
    self.lr = lr
    self.epochs = epochs
    self.w = None
    self.b = 0.0
    self.sse_history_ = []

  def fit(self, X, y_pm1):
    X = np.asarray(X, dtype=float)
    y_pm1 = np.asarray(y_pm1, dtype=float).ravel()
    n_features = X.shape[1]
    self.w = np.random.randn(n_features) * 0.01
    self.b = 0.0
    self.sse_history_ = []
    for _ in range(self.epochs):
      sse = 0.0
      for xi, yi in zip(X, y_pm1):
        z = np.dot(self.w, xi) + self.b
        a = z # linear activation
        e = yi - a
        # Update (Delta Rule)
        self.w += self.lr * e * xi
        self.b += self.lr * e
        sse += e**2
      self.sse_history_.append(sse)
    return self

  def net_input(self, X):
    X = np.asarray(X, dtype=float)
    return X @ self.w + self.b

  def predict_linear(self, X):
    return self.net_input(X)

  def predict_labels_pm1(self, X):
    z = self.net_input(X)
    return np.where(z >= 0.0, 1, -1)


#Synthetic 2D Dataset, Train/Test Split, ADALINE Training
# 1) Generate separable 2D data
rng = np.random.default_rng(7)
n_per_class = 120
X0 = rng.multivariate_normal([0.0, 0.0], [[0.25, 0.00],[0.00, 0.25]], size=n_per_class)
X1 = rng.multivariate_normal([2.0, 2.0], [[0.25, 0.00],[0.00, 0.25]], size=n_per_class)
X = np.vstack([X0, X1])
y01 = np.hstack([np.zeros(n_per_class, dtype=int), np.ones(n_per_class, dtype=int)])
y_pm1 = from01(y01) # {-1, +1}

# 2) Train/Test split
X_train, X_test, y_train, y_test = train_test_split(X, y_pm1, test_size=0.30, stratify=y_pm1, random_state=42)

# 3) Train ADALINE
model = ADALINE(lr=0.05, epochs=50).fit(X_train, y_train)

# 4) Plot SSE vs epochs
plt.figure(figsize=(6,4))
plt.plot(model.sse_history_)
plt.xlabel("Epoch")
plt.ylabel("SSE (Sum of Squared Errors)")
plt.title("ADALINE Training — SSE vs. Epochs (Synthetic)")
plt.show()

# 5) Evaluation
y_pred_train = model.predict_labels_pm1(X_train)
y_pred_test = model.predict_labels_pm1(X_test)
print_metrics(y_train, y_pred_train, split_name="Train")
print_metrics(y_test, y_pred_test, split_name="Test")

# 6) Decision boundary
plot_decision_boundary_2d(model, X_test, y_test, title="ADALINE Decision Boundary (Synthetic, Test Set)")


#Learning-Rate Effects
lrs = [0.001, 0.01, 0.1, 1.0]
epochs = 50
for lr in lrs:
  m = ADALINE(lr=lr, epochs=epochs).fit(X_train, y_train)
  plt.figure(figsize=(6,4))
  plt.plot(m.sse_history_)
  plt.xlabel("Epoch")
  plt.ylabel("SSE")
  plt.title(f"Learning Rate = {lr} — SSE vs. Epochs")
  plt.show()


#Iris Binary Subset (Real Data)

# 1) Load and prepare Iris binary subset: Setosa (0) vs Versicolor (1)
iris = load_iris()
X_iris = iris.data[:, :2] # two features for 2D viz (sepal length, sepal width)
y_iris_full = iris.target
mask = (y_iris_full == 0) | (y_iris_full == 1)
X_iris = X_iris[mask]
y_iris01 = y_iris_full[mask] # already 0/1
y_iris_pm1 = from01(y_iris01)

# 2) Standardize
scaler = StandardScaler()
X_iris_std = scaler.fit_transform(X_iris)

# 3) Split
Xi_train, Xi_test, yi_train, yi_test = train_test_split(X_iris_std, y_iris_pm1, test_size=0.30, stratify=y_iris_pm1, random_state=17)

# 4) Train ADALINE
adaline_iris = ADALINE(lr=0.05, epochs=80).fit(Xi_train, yi_train)

# 5) Metrics
y_tr_pred = adaline_iris.predict_labels_pm1(Xi_train)
y_te_pred = adaline_iris.predict_labels_pm1(Xi_test)
print_metrics(yi_train, y_tr_pred, split_name="Iris Train")
print_metrics(yi_test, y_te_pred, split_name="Iris Test")


##Comparison with Perceptron (Bonus)
if SKLEARN_PERCEPTRON_AVAILABLE:
  perc = Perceptron(max_iter=1000, tol=1e-3, random_state=0)
  perc.fit(Xi_train, to01(yi_train)) # sklearn expects labels in {0,1}
  y_te_perc = perc.predict(Xi_test)
  acc = accuracy_score(to01(yi_test), y_te_perc)
  cm = confusion_matrix(to01(yi_test), y_te_perc)
  prec = precision_score(to01(yi_test), y_te_perc, zero_division=0)
  rec = recall_score(to01(yi_test), y_te_perc, zero_division=0)
  f1 = f1_score(to01(yi_test), y_te_perc, zero_division=0)
  print("=== Perceptron on Iris (Test) ===")
  print(f"Accuracy: {acc:.4f}")
  print("Confusion Matrix:\n", cm)
  print(f"Precision: {prec:.4f}")
  print(f"Recall: {rec:.4f}")
  print(f"F1-score: {f1:.4f}")
else:
  print("scikit-learn Perceptron not available.")
    
'''
    return format_snippet(code)

def MLP_complete_code():
    code = '''
#MLP on XOR (Manual Backprop using NumPy):
import numpy as np
import matplotlib.pyplot as plt

# --- TASK 1 ---
class MLP_2_2_1:
    def __init__(self):
        # Define weights and biases for a 2->2->1 MLP
        self.weights_input_hidden = np.random.randn(2, 2)
        self.bias_hidden = np.zeros((1, 2))
        self.weights_hidden_output = np.random.randn(2, 1)
        self.bias_output = np.zeros((1, 1))

    def sigmoid(self, x):
        return 1 / (1 + np.exp(-x))

    def sigmoid_derivative(self, x):
        return x * (1 - x)

    def forward(self, X):
        # Compute z1 (hidden layer input)
        self.z1 = np.dot(X, self.weights_input_hidden) + self.bias_hidden

        # Compute a1 (hidden layer output)
        self.a1 = self.sigmoid(self.z1)

        # Compute z2 (output layer input)
        self.z2 = np.dot(self.a1, self.weights_hidden_output) + self.bias_output

        # Compute ŷ (output layer output)
        self.ŷ = self.sigmoid(self.z2)
        return self.ŷ

    def backward(self, X, y, output, learning_rate):
        # Compute the error (E) at the output layer
        output_error = output - y

        # Compute the gradient for the output layer weights and biases
        delta_output = output_error * self.sigmoid_derivative(output)
        d_weights_hidden_output = np.dot(self.a1.T, delta_output)
        d_bias_output = np.sum(delta_output, axis=0, keepdims=True)

        # Compute the error at the hidden layer
        hidden_error = np.dot(delta_output, self.weights_hidden_output.T) * self.sigmoid_derivative(self.a1)

        # Compute the gradient for the hidden layer weights and biases
        d_weights_input_hidden = np.dot(X.T, hidden_error)
        d_bias_hidden = np.sum(hidden_error, axis=0, keepdims=True)

        # Update weights and biases
        self.weights_hidden_output -= learning_rate * d_weights_hidden_output
        self.bias_output -= learning_rate * d_bias_output
        self.weights_input_hidden -= learning_rate * d_weights_input_hidden
        self.bias_hidden -= learning_rate * d_bias_hidden

    def train(self, X, y, epochs, learning_rate):
        for epoch in range(epochs):
            output = self.forward(X)
            self.backward(X, y, output, learning_rate)
            if (epoch+1) % 1000 == 0:
                # Compute and print the Mean Squared Error (MSE)
                loss = np.mean((y - output)**2)
                print(f'Epoch {epoch+1}, Loss: {loss:.4f}')

    def predict(self, X):
        return self.forward(X)


X = np.array([[0, 0], [0, 1], [1, 0], [1, 1]])
y = np.array([[0], [1], [1], [0]])

mlp = MLP_2_2_1()

epochs = 10000
learning_rate = 0.1
mlp.train(X, y, epochs, learning_rate)

predictions = mlp.predict(X)
print("\nPredictions after training:")
print(predictions)

print("\nValidation (comparing predicted output with actual output):")
print(np.round(predictions))



##MLP for XOR Classification (PyTorch):
import torch
import torch.nn as nn
import torch.optim as optim

# Define the MLP architecture (2 -> 2 -> 1)
class MLP_2_2_1_PyTorch(nn.Module):
    def __init__(self):
        super(MLP_2_2_1_PyTorch, self).__init__()
        # Input to Hidden
        self.hidden = nn.Linear(2, 2)
        # Hidden to Output
        self.output = nn.Linear(2, 1)  
        # Activation function  
        self.sigmoid = nn.Sigmoid()      

    def forward(self, x):
        # Hidden layer
        x = self.sigmoid(self.hidden(x)) 
        # Output layer
        x = self.sigmoid(self.output(x)) 
        return x

# XOR dataset
X = torch.tensor([[0., 0.],
                  [0., 1.],
                  [1., 0.],
                  [1., 1.]])

y = torch.tensor([[0.],
                  [1.],
                  [1.],
                  [0.]])

# Create model, define loss function and optimizer
model = MLP_2_2_1_PyTorch()
# Binary Cross-Entropy Loss
criterion = nn.BCELoss()                      
# SGD optimizer
optimizer = optim.SGD(model.parameters(), lr=0.5)  

# Training loop
epochs = 10000
for epoch in range(epochs):
    # Forward pass
    outputs = model(X)
    loss = criterion(outputs, y)

    # Backward pass and optimization
    optimizer.zero_grad()
    loss.backward()
    optimizer.step()

    # Print loss every 1000 epochs
    if (epoch + 1) % 1000 == 0:
        print(f'Epoch [{epoch+1}/{epochs}], Loss: {loss.item():.4f}')

# Testing / Predictions
with torch.no_grad():
    predictions = model(X)
    print("\nPredictions after training:")
    print(predictions)

    print("\nRounded predictions (comparison with actual outputs):")
    print(torch.round(predictions))



##Defining Loss Function and Optimizer:
import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import matplotlib.pyplot as plt

# Creating a Synthetic Dataset
# 2 input features: Study Hours and Attendance
# Target: Pass 1 or Fail 0
np.random.seed(0)

study_hours = np.random.uniform(0, 10, 100)    
attendance = np.random.uniform(40, 100, 100)

labels = np.where((study_hours * 0.5 + attendance * 0.05) > 5.5, 1, 0)

# Convert to PyTorch tensors
X = torch.tensor(np.column_stack((study_hours, attendance)), dtype=torch.float32)
y = torch.tensor(labels.reshape(-1, 1), dtype=torch.float32)

# Define the MLP Model
class StudentPerformanceMLP(nn.Module):
    def __init__(self):
        super(StudentPerformanceMLP, self).__init__()
        self.hidden = nn.Linear(2, 4)   # Input -> Hidden (2 -> 4)
        self.output = nn.Linear(4, 1)   # Hidden -> Output (4 -> 1)
        self.sigmoid = nn.Sigmoid()

    def forward(self, x):
        x = self.sigmoid(self.hidden(x))
        x = self.sigmoid(self.output(x))
        return x

#Initialize Model, Loss, and Optimizer
model = StudentPerformanceMLP()
criterion = nn.BCELoss()
optimizer = optim.SGD(model.parameters(), lr=0.1)

#Training Loop
epochs = 2000
losses = []

for epoch in range(epochs):
    outputs = model(X)
    loss = criterion(outputs, y)

    optimizer.zero_grad()
    loss.backward()
    optimizer.step()

    losses.append(loss.item())

    if (epoch + 1) % 200 == 0:
        print(f'Epoch [{epoch+1}/{epochs}], Loss: {loss.item():.4f}')

#Plot the Loss Curve
plt.plot(losses)
plt.xlabel('Epochs')
plt.ylabel('Loss')
plt.title('Training Loss Curve')
plt.show()

#Model Evaluation
with torch.no_grad():
    predictions = model(X)
    predicted_labels = torch.round(predictions)

    accuracy = (predicted_labels.eq(y).sum().item() / y.shape[0]) * 100
    print(f"\nModel Accuracy: {accuracy:.2f}%")

    print("\nSample Predictions:")
    for i in range(5):
        print(f"Study Hours: {study_hours[i]:.1f}, Attendance: {attendance[i]:.1f}%, Predicted: {int(predicted_labels[i].item())}")



    
'''
    return format_snippet(code)

def MLP_titanic_houses_code():
    code = '''

#Classification on Kaggle Dataset (Titanic):
import torch
import torch.nn as nn
import torch.optim as optim
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
import matplotlib.pyplot as plt

# ----- Step 1: Load the Titanic Dataset -----
file_path = "/content/Titanic-Dataset.csv"
data = pd.read_csv(file_path)

# View first few rows to understand structure (optional)
print(data.head())

# ----- Step 2: Data Preprocessing -----
# Select relevant features (you can modify these based on your file)
features = ['PassengerId', 'Survived', 'Pclass', 'Name', 'Sex', 'Age', 'SibSp', 'Parch', 'Ticket', 'Fare', 'Cabin', 'Embarked']
target = 'Survived'

# Handle missing values
data['Age'].fillna(data['Age'].mean(), inplace=True)
data['Embarked'].fillna(data['Embarked'].mode()[0], inplace=True)

# Convert categorical to numeric (Sex: male=0, female=1)
data['Sex'] = LabelEncoder().fit_transform(data['Sex'])
data['Embarked'] = LabelEncoder().fit_transform(data['Embarked'])
# Extract inputs (X) and labels (y)
X = data[['Pclass', 'Sex', 'Age', 'SibSp', 'Parch', 'Fare', 'Embarked']].values
y = data[target].values.reshape(-1, 1)

# Normalize input features
scaler = StandardScaler()
X = scaler.fit_transform(X)

# Convert to PyTorch tensors
X = torch.tensor(X, dtype=torch.float32)
y = torch.tensor(y, dtype=torch.float32)

# Split into training and testing sets (80-20 split)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# ----- Step 3: Define the MLP Model -----
class TitanicMLP(nn.Module):
    def __init__(self):
        super(TitanicMLP, self).__init__()
        self.hidden1 = nn.Linear(X_train.shape[1], 8)   # Input -> Hidden1
        self.hidden2 = nn.Linear(8, 4)   # Hidden1 -> Hidden2
        self.output = nn.Linear(4, 1)    # Hidden2 -> Output
        self.sigmoid = nn.Sigmoid()

    def forward(self, x):
        x = self.sigmoid(self.hidden1(x))
        x = self.sigmoid(self.hidden2(x))
        x = self.sigmoid(self.output(x))
        return x

# ----- Step 4: Initialize Model, Loss, and Optimizer -----
model = TitanicMLP()
criterion = nn.BCELoss()
optimizer = optim.SGD(model.parameters(), lr=0.1)

# ----- Step 5: Training Loop -----
epochs = 2000
losses = []

for epoch in range(epochs):
    # Forward pass
    outputs = model(X_train)
    loss = criterion(outputs, y_train)

    # Backward pass
    optimizer.zero_grad()
    loss.backward()
    optimizer.step()

    losses.append(loss.item())

    if (epoch + 1) % 200 == 0:
        print(f'Epoch [{epoch+1}/{epochs}], Loss: {loss.item():.4f}')

# ----- Step 6: Plot the Loss Curve -----
plt.plot(losses)
plt.xlabel('Epochs')
plt.ylabel('Loss')
plt.title('Titanic MLP Training Loss')
plt.show()

# ----- Step 7: Model Evaluation -----
with torch.no_grad():
    predictions = model(X_test)
    predicted_labels = torch.round(predictions)
    accuracy = (predicted_labels.eq(y_test).sum().item() / y_test.shape[0]) * 100

print(f"\nModel Accuracy on Test Data: {accuracy:.2f}%")

# Display some sample predictions
for i in range(5):
    print(f"Actual: {int(y_test[i].item())}, Predicted: {int(predicted_labels[i].item())}")


##Regression on Kaggle Dataset (House Prices):
# --- TASK 2 ---
import torch
import torch.nn as nn
import torch.optim as optim
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
import matplotlib.pyplot as plt

# ----- Step 1: Load the Housing Dataset -----
file_path2 = "/content/Housing.csv"
data = pd.read_csv(file_path2)

# View first few rows (optional)
print(data.head())

# ----- Step 2: Data Preprocessing -----
# Separate features (X) and target (y)
X = data.drop(columns=['price'])
y = data['price'].values.reshape(-1, 1)

# Identify categorical and numerical features
categorical_features = ['mainroad', 'guestroom', 'basement', 'hotwaterheating', 'airconditioning', 'prefarea', 'furnishingstatus']
numerical_features = X.select_dtypes(include=['float64', 'int64']).columns.tolist()

# Create preprocessing pipelines for numerical and categorical features
numerical_transformer = StandardScaler()
categorical_transformer = OneHotEncoder(handle_unknown='ignore')
# Create a column transformer to apply different transformations to different columns
preprocessor = ColumnTransformer(
    transformers=[
        ('num', numerical_transformer, numerical_features),
        ('cat', categorical_transformer, categorical_features)])

# Apply preprocessing
X = preprocessor.fit_transform(X)

# Convert to PyTorch tensors
X = torch.tensor(X, dtype=torch.float32)
y = torch.tensor(y, dtype=torch.float32)

# Split into training and test sets (80-20)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# ----- Step 3: Define the MLP Model for Regression -----
class HousingMLP(nn.Module):
    def __init__(self):
        super(HousingMLP, self).__init__()
        self.hidden1 = nn.Linear(X_train.shape[1], 16)
        self.hidden2 = nn.Linear(16, 8)
        self.output = nn.Linear(8, 1)
        self.relu = nn.ReLU()

    def forward(self, x):
        x = self.relu(self.hidden1(x))
        x = self.relu(self.hidden2(x))
        x = self.output(x)
        return x

# ----- Step 4: Initialize Model, Loss, and Optimizer -----
model = HousingMLP()
criterion = nn.MSELoss()                       # For regression
optimizer = optim.Adam(model.parameters(), lr=0.01)

# ----- Step 5: Training Loop -----
epochs = 1000
losses = []

for epoch in range(epochs):
    outputs = model(X_train)
    loss = criterion(outputs, y_train)
    optimizer.zero_grad()
    loss.backward()
    optimizer.step()

    losses.append(loss.item())

    if (epoch + 1) % 100 == 0:
        print(f'Epoch [{epoch+1}/{epochs}], Loss: {loss.item():.4f}')

# ----- Step 6: Plot the Loss Curve -----
plt.plot(losses)
plt.xlabel('Epochs')
plt.ylabel('MSE Loss')
plt.title('Housing Price Prediction Loss Curve')
plt.show()

# ----- Step 7: Model Evaluation -----
with torch.no_grad():
    predictions = model(X_test)
    mse = criterion(predictions, y_test).item()
    mae = torch.mean(torch.abs(predictions - y_test)).item()
    r2 = 1 - (torch.sum((y_test - predictions) ** 2) / torch.sum((y_test - torch.mean(y_test)) ** 2)).item()

print(f"\nModel Evaluation on Test Data:")
print(f"MSE: {mse:.4f}")
print(f"MAE: {mae:.4f}")
print(f"R² Score: {r2:.4f}")
    
'''
    return format_snippet(code)

def CNN_og_code():
    code = '''
import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
from torchvision import datasets, transforms
from torch.utils.data import DataLoader
import matplotlib.pyplot as plt

# 1. Load and Preprocess Data

transform = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize((0.5,), (0.5,))   # normalize to [-1, 1]
])

train_data = datasets.FashionMNIST(root='./data', train=True, download=True, transform=transform)
test_data = datasets.FashionMNIST(root='./data', train=False, download=True, transform=transform)

train_loader = DataLoader(train_data, batch_size=64, shuffle=True)
test_loader = DataLoader(test_data, batch_size=1000, shuffle=False)

# 2. Define CNN Architecture

class FashionCNN(nn.Module):
    def __init__(self):
        super(FashionCNN, self).__init__()
        # Convolutional layers
        self.conv1 = nn.Conv2d(1, 32, kernel_size=3, padding=1)
        self.bn1 = nn.BatchNorm2d(32)
        self.pool1 = nn.MaxPool2d(2, 2)

        self.conv2 = nn.Conv2d(32, 64, kernel_size=3, padding=1)
        self.bn2 = nn.BatchNorm2d(64)
        self.pool2 = nn.MaxPool2d(2, 2)

        # Fully connected layers
        self.fc1 = nn.Linear(64 * 7 * 7, 128)
        self.dropout = nn.Dropout(0.5)
        self.fc2 = nn.Linear(128, 10)  # 10 classes

    def forward(self, x):
        x = self.pool1(F.relu(self.bn1(self.conv1(x))))
        x = self.pool2(F.relu(self.bn2(self.conv2(x))))
        x = x.view(-1, 64 * 7 * 7)
        x = F.relu(self.fc1(x))
        x = self.dropout(x)
        x = self.fc2(x)
        return x

model = FashionCNN()

# 3. Define Loss and Optimizer

criterion = nn.CrossEntropyLoss()
optimizer = optim.SGD(model.parameters(), lr=0.01, momentum=0.9)

# 4. Training Loop

epochs = 10  # set to 100 for full training
train_losses = []
test_accuracies = []
train_accuracies = []

for epoch in range(epochs):
    model.train()
    running_loss = 0.0
    correct_train = 0
    total_train = 0

    for images, labels in train_loader:
        optimizer.zero_grad()
        outputs = model(images)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()

        running_loss += loss.item()
        _, predicted = torch.max(outputs.data, 1)
        total_train += labels.size(0)
        correct_train += (predicted == labels).sum().item()

    # Evaluate on test set
    model.eval()
    correct_test = 0
    total_test = 0
    with torch.no_grad():
        for images, labels in test_loader:
            outputs = model(images)
            _, predicted = torch.max(outputs.data, 1)
            total_test += labels.size(0)
            correct_test += (predicted == labels).sum().item()

    # Record stats
    train_acc = 100 * correct_train / total_train
    test_acc = 100 * correct_test / total_test
    train_losses.append(running_loss / len(train_loader))
    train_accuracies.append(train_acc)
    test_accuracies.append(test_acc)

    print(f"Epoch [{epoch+1}/{epochs}] "
          f"Loss: {running_loss/len(train_loader):.4f} "
          f"Train Acc: {train_acc:.2f}% "
          f"Test Acc: {test_acc:.2f}%")

# 5. Plot Training Loss

plt.plot(train_losses, label='Training Loss')
plt.xlabel('Epoch')
plt.ylabel('Loss')
plt.title('Training Loss per Epoch')
plt.legend()
plt.show()

# 6. Interpretation

print("\n--- Final Results ---")
print(f"Training Accuracy: {train_accuracies[-1]:.2f}%")
print(f"Testing Accuracy: {test_accuracies[-1]:.2f}%")

if train_accuracies[-1] > test_accuracies[-1] + 5:
    print("→ Model might be overfitting.")
else:
    print("→ Model is generalizing well.")

'''
    return format_snippet(code)

def CNN_modified_code():
    code = '''
import torch
import torch.nn as nn
import torch.optim as optim
import torchvision
import torchvision.transforms as transforms
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix
import numpy as np
import random


#Common Setup

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

transform = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize((0.5,), (0.5,))
])

train_dataset = torchvision.datasets.FashionMNIST(root='./data', train=True, transform=transform, download=True)
test_dataset = torchvision.datasets.FashionMNIST(root='./data', train=False, transform=transform, download=True)

train_loader = torch.utils.data.DataLoader(train_dataset, batch_size=64, shuffle=True)
test_loader = torch.utils.data.DataLoader(test_dataset, batch_size=1000, shuffle=False)

# Task 1 — Add a Third Convolutional Block

class DeepCNN(nn.Module):
    def __init__(self):
        super(DeepCNN, self).__init__()
        self.conv1 = nn.Conv2d(1, 32, kernel_size=3, padding='same')
        self.bn1 = nn.BatchNorm2d(32)
        self.conv2 = nn.Conv2d(32, 64, kernel_size=3, padding='same')
        self.bn2 = nn.BatchNorm2d(64)
        self.conv3 = nn.Conv2d(64, 128, kernel_size=3, padding='same')
        self.bn3 = nn.BatchNorm2d(128)
        self.pool = nn.MaxPool2d(2, 2)
        self.fc1 = nn.Linear(128 * 3 * 3, 256)
        self.fc2 = nn.Linear(256, 10)
        self.relu = nn.ReLU()
        self.dropout = nn.Dropout(0.3)

    def forward(self, x):
        x = self.pool(self.relu(self.bn1(self.conv1(x))))
        x = self.pool(self.relu(self.bn2(self.conv2(x))))
        x = self.pool(self.relu(self.bn3(self.conv3(x))))
        x = x.view(-1, 128 * 3 * 3)
        x = self.dropout(self.relu(self.fc1(x)))
        x = self.fc2(x)
        return x

# Initialize model
model = DeepCNN().to(device)
criterion = nn.CrossEntropyLoss()
optimizer = optim.SGD(model.parameters(), lr=0.01, momentum=0.9)

# Training loop (used in multiple tasks)
def train_model(model, optimizer, lr_label, epochs=10):
    train_losses, test_accuracies = [], []
    for epoch in range(epochs):
        model.train()
        running_loss = 0.0
        for images, labels in train_loader:
            images, labels = images.to(device), labels.to(device)
            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            running_loss += loss.item()
        train_losses.append(running_loss / len(train_loader))

        # Evaluate test accuracy
        model.eval()
        correct, total = 0, 0
        with torch.no_grad():
            for images, labels in test_loader:
                images, labels = images.to(device), labels.to(device)
                outputs = model(images)
                _, preds = torch.max(outputs, 1)
                total += labels.size(0)
                correct += (preds == labels).sum().item()
        test_acc = 100 * correct / total
        test_accuracies.append(test_acc)

        print(f"[{lr_label}] Epoch {epoch+1}/{epochs} | Loss: {train_losses[-1]:.4f} | Test Acc: {test_acc:.2f}%")
    return train_losses, test_accuracies

# Train base DeepCNN
train_losses, test_accs = train_model(model, optimizer, "Task1", epochs=10)

# Task 2 — Learning Rate Experiment

# Lower learning rate for stability test
model_lr = DeepCNN().to(device)
optimizer_lr = optim.SGD(model_lr.parameters(), lr=0.1, momentum=0.9)

lr_losses, lr_accs = train_model(model_lr, optimizer_lr, "LR=0.001", epochs=10)

# Plot loss curves for comparison
plt.figure(figsize=(7,4))
plt.plot(train_losses, label='Original LR=0.01')
plt.plot(lr_losses, label='New LR=0.001')
plt.title("Learning Rate Comparison")
plt.xlabel("Epochs")
plt.ylabel("Training Loss")
plt.legend()
plt.show()

# Task 3 — Replace SGD with Adam Optimizer

model_adam = DeepCNN().to(device)
optimizer_adam = optim.Adam(model_adam.parameters(), lr=0.001)

adam_losses, adam_accs = train_model(model_adam, optimizer_adam, "Adam", epochs=30)

plt.figure(figsize=(7,4))
plt.plot(lr_losses, label='SGD (LR=0.001)')
plt.plot(adam_losses, label='Adam')
plt.title("Optimizer Comparison")
plt.xlabel("Epochs")
plt.ylabel("Training Loss")
plt.legend()
plt.show()

# Task 4 — Confusion Matrix & Class-wise Accuracy

classes = train_dataset.classes
y_true, y_pred = [], []

model_adam.eval()
with torch.no_grad():
    for images, labels in test_loader:
        images, labels = images.to(device), labels.to(device)
        outputs = model_adam(images)
        _, preds = torch.max(outputs, 1)
        y_true.extend(labels.cpu().numpy())
        y_pred.extend(preds.cpu().numpy())

cm = confusion_matrix(y_true, y_pred)
plt.figure(figsize=(8,6))
sns.heatmap(cm, annot=False, cmap='Blues', xticklabels=classes, yticklabels=classes)
plt.title("Confusion Matrix (Adam Model)")
plt.xlabel("Predicted")
plt.ylabel("True")
plt.show()

# Class-wise accuracy
class_acc = cm.diagonal() / cm.sum(axis=1)
for i, acc in enumerate(class_acc):
    print(f"{classes[i]:<15}: {acc*100:.2f}%")

# Identify top 3 most confused class pairs
confused_pairs = np.unravel_index(np.argsort(cm, axis=None)[-20:], cm.shape)
pairs = list(zip(confused_pairs[0], confused_pairs[1]))
unique_confused = [(classes[i], classes[j]) for i, j in pairs if i != j][-3:]
print("\nTop 3 Confused Class Pairs:", unique_confused)

# Task 5 — Save & Reload Model + Predictions

torch.save(model_adam.state_dict(), "fashion_cnn_adam.pth")

# Reload model
loaded_model = DeepCNN().to(device)
loaded_model.load_state_dict(torch.load("fashion_cnn_adam.pth"))
loaded_model.eval()

# Predict on 5 random test images
samples = random.sample(range(len(test_dataset)), 5)
plt.figure(figsize=(10,2))
for idx, i in enumerate(samples):
    image, label = test_dataset[i]
    with torch.no_grad():
        output = loaded_model(image.unsqueeze(0).to(device))
        pred = output.argmax(1).item()
    plt.subplot(1,5,idx+1)
    plt.imshow(image.squeeze(), cmap='gray')
    plt.title(f"T:{classes[label]}\nP:{classes[pred]}")
    plt.axis('off')
plt.show()

print("\n Model Saved, Reloaded, and Successfully Used for Inference.")
print(" Model serialization ensures trained weights can be reused for inference or further training without retraining from scratch.")


'''
    return format_snippet(code)

def CNN_filters_code():
    code = '''
import tensorflow as tf
from tensorflow.keras import layers, models
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image

# Define custom filters
edge_filter = np.array([[ -1, -1, -1],
[ -1, 8, -1],
[ -1, -1, -1]])
vertical_filter = np.array([[ 1, 0, -1],
[ 1, 0, -1],
[ 1, 0, -1]])
horizontal_filter = np.array([[ 1, 1, 1],
[ 0, 0, 0],
[-1, -1, -1]])
smoothing_filter = np.array([[ 1, 1, 1],
[ 1, 1, 1],
[ 1, 1, 1]]) / 9.0
sharpening_filter = np.array([[ 0, -1, 0],
[-1, 5, -1],
[ 0, -1, 0]])

# Reshape filters for CNN
edge_filter = edge_filter.reshape((3, 3, 1, 1))
vertical_filter = vertical_filter.reshape((3, 3, 1, 1))
horizontal_filter = horizontal_filter.reshape((3, 3, 1, 1))
smoothing_filter = smoothing_filter.reshape((3, 3, 1, 1))
sharpening_filter = sharpening_filter.reshape((3, 3, 1, 1))

# Load the image
image_path = '/content/2legends1pic.jpg'
img = Image.open(image_path).convert('L') # Convert to grayscale
img_array = np.array(img)
img_array = img_array.astype('float32') / 255.0 # Normalize

# Reshape for CNN (add batch and channel dimensions)
input_image = img_array.reshape((1, img_array.shape[0], img_array.shape[1], 1))

# Resize for CNN
img = img.resize((128, 128))
plt.imshow(input_image[0, :, :, 0], cmap='gray')
plt.title("Original Image")
plt.axis('off')
plt.show()

# Apply Edge Detection Filter
model_edge = models.Sequential()
model_edge.add(layers.Conv2D(1, (3, 3), input_shape=(input_image.shape[1], input_image.shape[2], 1), use_bias=False))
model_edge.layers[0].set_weights([edge_filter])
output_edge = model_edge.predict(input_image)
plt.imshow(output_edge[0, :, :, 0], cmap='gray')
plt.title("Edge Detection")
plt.axis('off')
plt.show()

# Apply Vertical Line Detection Filter
model_vertical = models.Sequential()
model_vertical.add(layers.Conv2D(1, (3, 3), input_shape=(input_image.shape[1], input_image.shape[2], 1), use_bias=False))
model_vertical.layers[0].set_weights([vertical_filter])
output_vertical = model_vertical.predict(input_image)
plt.imshow(output_vertical[0, :, :, 0], cmap='gray')
plt.title("Vertical Lines")
plt.axis('off')
plt.show()

# Apply Horizontal Line Detection Filter
model_horizontal = models.Sequential()
model_horizontal.add(layers.Conv2D(1, (3, 3), input_shape=(input_image.shape[1], input_image.shape[2], 1), use_bias= False))
model_horizontal.layers[0].set_weights([horizontal_filter])
output_horizontal = model_horizontal.predict(input_image)
plt.imshow(output_horizontal[0, :, :, 0], cmap='gray')
plt.title("Horizontal Lines")
plt.axis('off')
plt.show()

# Apply Smoothing Filter
model_smoothing = models.Sequential()
model_smoothing.add(layers.Conv2D(1, (3, 3), input_shape=(input_image.shape[1], input_image.shape[2], 1), use_bias= False))
model_smoothing.layers[0].set_weights([smoothing_filter])
output_smoothing = model_smoothing.predict(input_image)
plt.imshow(output_smoothing[0, :, :, 0], cmap='gray')
plt.title("Smoothing")
plt.axis('off')
plt.show()

# Apply Sharpening Filter
model_sharpening = models.Sequential()
model_sharpening.add(layers.Conv2D(1, (3, 3), input_shape=(input_image.shape[1], input_image.shape[2], 1), use_bias=False))
model_sharpening.layers[0].set_weights([sharpening_filter])
output_sharpening = model_sharpening.predict(input_image)
plt.imshow(output_sharpening[0, :, :, 0], cmap='gray')
plt.title("Sharpening")
plt.axis('off')
plt.show()

# Task 3 - Conceptual CNN Setup
# Apply multiple filters simultaneously and visualize feature maps
# Stack all filters together (each filter becomes one output channel)
combined_filters = np.concatenate(
    [edge_filter, vertical_filter, horizontal_filter, smoothing_filter, sharpening_filter],
    axis=3
)

# Create a CNN model with multiple filters
model_multi = models.Sequential()
model_multi.add(layers.Conv2D(
    filters=5,
    kernel_size=(3, 3),
    input_shape=(input_image.shape[1], input_image.shape[2], 1),
    use_bias=False
))
model_multi.layers[0].set_weights([combined_filters])

# Apply the model to the input image
output_multi = model_multi.predict(input_image)

# Visualize all feature maps side-by-side
titles = ["Edge Detection", "Vertical Lines", "Horizontal Lines", "Smoothing", "Sharpening"]
plt.figure(figsize=(15, 5))
for i in range(5):
    plt.subplot(1, 5, i + 1)
    plt.imshow(output_multi[0, :, :, i], cmap='gray')
    plt.title(titles[i])
    plt.axis('off')
plt.suptitle("Multiple Filters Applied Simultaneously", fontsize=14)
plt.show()

# Task 1 - Multi-Image Experimentation
images = ['/content/Napoleon.jpg', '/content/geometric_pattern.jpg', '/content/textured_scene.jpg']

# Apply the model to the input image
for i in images:
  image_path = i
  img = Image.open(image_path).convert('L') # Convert to grayscale
  img_array = np.array(img)
  img_array = img_array.astype('float32') / 255.0 # Normalize

  # Reshape for CNN (add batch and channel dimensions)
  input_image = img_array.reshape((1, img_array.shape[0], img_array.shape[1], 1))
  # Apply the model to the input image
  output_multi = model_multi.predict(input_image)

  # Visualize all feature maps side-by-side
  titles = ["Edge Detection", "Vertical Lines", "Horizontal Lines", "Smoothing", "Sharpening"]
  plt.figure(figsize=(15, 5))
  for i in range(5):
      plt.subplot(1, 5, i + 1)
      plt.imshow(output_multi[0, :, :, i], cmap='gray')
      plt.title(titles[i])
      plt.axis('off')
  plt.suptitle("Multiple Filters Applied Simultaneously", fontsize=14)
  plt.show()

# --- TASK 4 ---
# --- Define Custom Filters ---
filters = {
    "Smoothing": np.array([[1, 1, 1],
                           [1, 1, 1],
                           [1, 1, 1]]) / 9.0,

    "Sharpening": np.array([[0, -1, 0],
                            [-1, 5, -1],
                            [0, -1, 0]]),

    "Edge Detection": np.array([[-1, -1, -1],
                                [-1, 8, -1],
                                [-1, -1, -1]]),

    "Vertical": np.array([[-1, 0, 1],
                          [-2, 0, 2],
                          [-1, 0, 1]])
}

# --- Function to build a simple CNN with a given filter ---
def build_filter_model(filter_kernel):
    model = models.Sequential()
    model.add(layers.Conv2D(
        filters=1,
        kernel_size=(3, 3),
        activation='relu',
        padding='same',
        input_shape=(img_array.shape[0], img_array.shape[1], 1),
        use_bias=False
    ))
    model.layers[0].set_weights([filter_kernel.reshape((3, 3, 1, 1)),])
    return model

# --- Function to apply two filters sequentially ---
def apply_two_filters(image, first_filter, second_filter):
    model1 = build_filter_model(filters[first_filter])
    output1 = model1.predict(image)
    model2 = build_filter_model(filters[second_filter])
    output2 = model2.predict(output1)
    return output1[0, :, :, 0], output2[0, :, :, 0]

# --- Define filter pairs ---
filter_pairs = [
    ("Smoothing", "Sharpening"),
    ("Sharpening", "Edge Detection"),
    ("Vertical", "Sharpening")
]

# Load the image
image_path = '/content/textured_scene.jpg'
img = Image.open(image_path).convert('L') # Convert to grayscale
img_array = np.array(img)
img_array = img_array.astype('float32') / 255.0 # Normalize

# Reshape for CNN (add batch and channel dimensions)
input_image = img_array.reshape((1, img_array.shape[0], img_array.shape[1], 1))

# Resize for CNN
img = img.resize((128, 128))

# --- Apply combinations and visualize results ---
plt.figure(figsize=(15, 10))
for idx, (f1, f2) in enumerate(filter_pairs):
    _, output_combined = apply_two_filters(input_image, f1, f2)
    plt.subplot(1, 3, idx + 1)
    plt.imshow(output_combined, cmap='gray')
    plt.title(f"{f1} → {f2}")
    plt.axis('off')

plt.suptitle("Task 2 — Sequential Filter Combinations", fontsize=16)
plt.show()
  
'''
    return format_snippet(code)