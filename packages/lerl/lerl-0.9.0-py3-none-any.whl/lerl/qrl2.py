from .utils import format_snippet

def q_learning_code():
    code = '''
# Off-Policy QLearning
import gymnasium as gym
import numpy as np

env = gym.make("FrozenLake-v1", is_slippery=False)
Q = np.zeros((env.observation_space.n, env.action_space.n))

def epsilon_greedy(state):
    if np.random.random() < epsilon:
        return env.action_space.sample()
    return np.argmax(Q[state])

alpha = 0.8
gamma = 0.95
epsilon = 0.1
episodes = 2000
rewards = []

for ep in range(episodes):
    state = env.reset()[0]
    done = False
    total_reward = 0

    while not done:
        action = epsilon_greedy(state)
        next_state, reward, done, _, _ = env.step(action)

        best_next = np.max(Q[next_state])
        Q[state, action] += alpha * (reward + gamma * best_next - Q[state, action])

        state = next_state
        total_reward += reward

    rewards.append(total_reward)

plt.plot(rewards, label="Q-Learning")
plt.legend()
plt.show()

'''
    return format_snippet(code)

def sarsa_code():
    code = '''
# On-Policy SARSA
import gymnasium as gym
import numpy as np

env = gym.make("FrozenLake-v1", is_slippery=False)
Q = np.zeros((env.observation_space.n, env.action_space.n))

def epsilon_greedy(state):
    if np.random.random() < epsilon:
        return env.action_space.sample()
    return np.argmax(Q[state])

alpha = 0.8
gamma = 0.95
epsilon = 0.1
episodes = 2000
rewards = []

for ep in range(episodes):
    state = env.reset()[0]
    action = epsilon_greedy(state)
    done = False
    total_reward = 0

    while not done:
        next_state, reward, done, _, _ = env.step(action)
        next_action = epsilon_greedy(next_state)

        Q[state, action] += alpha * (reward + gamma * Q[next_state, next_action] - Q[state, action])

        state = next_state
        action = next_action
        total_reward += reward

    rewards.append(total_reward)

plt.plot(rewards, label="SARSA")
plt.legend()
plt.show()

'''
    return format_snippet(code)

def mc_is_code():
    code = '''
# Off-Policy Monte Carlo With Importance Sampling
import gymnasium as gym
import numpy as np

env = gym.make("Blackjack-v1")
Q = {}
C = {}
gamma = 1.0

def init(state):
    if state not in Q:
        Q[state] = np.zeros(2)
        C[state] = np.zeros(2)

def behavior_policy():
    return np.random.choice([0, 1])

def target_policy(q):
    return np.argmax(q)

episodes = 200000

for _ in range(episodes):
    episode = []
    state = env.reset()[0]
    done = False

    while not done:
        action = behavior_policy()
        next_state, reward, done, _, _ = env.step(action)
        episode.append((state, action, reward))
        state = next_state

    G = 0
    W = 1.0

    for (s, a, r) in reversed(episode):
        G = gamma * G + r
        init(s)

        C[s][a] += W
        Q[s][a] += (W / C[s][a]) * (G - Q[s][a])


        if target_policy(Q[s]) != a:
            break


        W *= (1.0 / 0.5)

print("Estimated Q-values:")
print(Q)


'''
    return format_snippet(code)

def qlearning_tdcontrol_code():
    code = '''
# Q-Learning Off-Policy TD control
import gymnasium as gym
import numpy as np

env = gym.make("FrozenLake-v1", is_slippery=False)

Q = np.zeros((env.observation_space.n, env.action_space.n))
alpha = 0.1
gamma = 0.99
epsilon = 0.1

def behavior_policy(s):
    if np.random.rand() < epsilon:
        return env.action_space.sample()
    return np.argmax(Q[s])

episodes = 5000

for _ in range(episodes):
    s = env.reset()[0]
    done = False

    while not done:
        a = behavior_policy(s)
        s2, r, done, _, _ = env.step(a)

        best_next = np.max(Q[s2])
        Q[s, a] += alpha * (r + gamma * best_next - Q[s, a])
        s = s2


print(Q)

'''
    return format_snippet(code)

def linear_approximation_code():
    code = '''
# Linear Approximation of Value Function
import gymnasium as gym
import numpy as np
import matplotlib.pyplot as plt

def features(state):
    return np.array([1, state])

w = np.zeros(2)
alpha = 0.01
gamma = 0.99

def update(w, s, r, s_next):
    td_error = r + gamma * np.dot(w, features(s_next)) - np.dot(w, features(s))
    w += alpha * td_error * features(s)
    return w

env = gym.make('CartPole-v1')

for episode in range(200):
    state, _ = env.reset()
    done = False

    while not done:
        action = env.action_space.sample()
        next_state, reward, terminated, truncated, _ = env.step(action)
        done = terminated or truncated

        s = state[0]
        s_next = next_state[0]

        w = update(w, s, reward, s_next)
        state = next_state


print("Learned weights (w) for linear value function approximation:", w)

'''
    return format_snippet(code)

def non_linear_approximation_nn_code():
    code = '''
# Non Linear Using NN Approximation of neural networks
import gymnasium as gym
import numpy as np
import torch
import torch.nn as nn
import matplotlib.pyplot as plt

def features(state):
    return np.array([1, state])

class ValueNet(nn.Module):
    def __init__(self):
        super().__init__()
        self.fc = nn.Sequential(
            nn.Linear(1, 64),
            nn.ReLU(),
            nn.Linear(64, 1)
        )

    def forward(self, x):
        return self.fc(x)

model = ValueNet()
optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
loss_fn = nn.MSELoss()
gamma = 0.99

env = gym.make('CartPole-v1')

for episode in range(200):
    state, _ = env.reset()
    done = False

    while not done:
        state_tensor = torch.tensor([state[0]], dtype=torch.float32)
        value = model(state_tensor)

        action = env.action_space.sample()
        next_state, reward, terminated, truncated, _ = env.step(action)
        done = terminated or truncated

        with torch.no_grad():
            next_state_tensor = torch.tensor([next_state[0]], dtype=torch.float32)
            target = reward + gamma * model(next_state_tensor)

        loss = loss_fn(value, target)

        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        state = next_state


with torch.no_grad():
    sample_state = torch.tensor([0.0], dtype=torch.float32)
    sample_value = model(sample_state).item()
print(f"Sample estimated value (NN) for state 0.0: {sample_value}")

'''
    return format_snippet(code)

def batch_monte_carlo_code():
    code = '''
# Batch MonteCarlo
import numpy as np
import matplotlib.pyplot as plt

episodes = [
    [(0, 1), (1, 1), (2, 0)],
    [(0, 1), (1, 0), (2, 1)],
    [(0, 0), (1, 1), (2, 1)]
]

V = np.zeros(3)
returns = {s: [] for s in range(3)}
gamma = 0.9

for episode in episodes:
    G = 0
    for state, reward in reversed(episode):
        G = reward + gamma * G
        returns[state].append(G)

for state in returns:
    V[state] = np.mean(returns[state])

print("Monte Carlo Value Function:", V)

'''
    return format_snippet(code)

def batch_td_code():
    code = '''
# BATCH TD(0)
import numpy as np
import matplotlib.pyplot as plt

transitions = [
    (0, 1, 1),
    (1, 1, 2),
    (2, 0, 2),
    (0, 1, 1),
    (1, 0, 2)
]

num_states = 3
V = np.zeros(num_states)
gamma = 0.9
alpha = 0.1
epochs = 50

for epoch in range(epochs):
    td_sums = np.zeros(num_states)
    td_counts = np.zeros(num_states)

    for s, r, s_next in transitions:
        td_error = r + gamma * V[s_next] - V[s]
        td_sums[s] += td_error
        td_counts[s] += 1

    for s in range(num_states):
        if td_counts[s] > 0:
            V[s] += alpha * (td_sums[s] / td_counts[s])

print("Batch TD(0) Value Function:", V)

'''
    return format_snippet(code)

def batch_td_lambda_code():
    code = '''
# Batch TD(lambda)
import numpy as np
import matplotlib.pyplot as plt

V = np.zeros(3)
eligibility = np.zeros(3)

alpha = 0.1
gamma = 0.9
lam = 0.8

transitions = [
    (0, 1, 1),
    (1, 1, 2),
    (2, 0, 2)
]

for epoch in range(50):
    eligibility[:] = 0

    for s, r, s_next in transitions:
        td_error = r + gamma * V[s_next] - V[s]
        eligibility[s] += 1
        V += alpha * td_error * eligibility
        eligibility *= gamma * lam

print("Batch TD(λ) Value Function:", V)

'''
    return format_snippet(code)

def dqn_batch_code():
    code = '''
#Deep Q-Network (DQN) with Batch Updates
import gymnasium as gym
import torch
import torch.nn as nn
import torch.optim as optim
import random
import numpy as np
from collections import deque
import matplotlib.pyplot as plt

class QNetwork(nn.Module):
    def __init__(self, state_dim, action_dim):
        super(QNetwork, self).__init__()
        self.fc1 = nn.Linear(state_dim, 64)
        self.fc2 = nn.Linear(64, 64)
        self.fc3 = nn.Linear(64, action_dim)

    def forward(self, x):
        x = torch.relu(self.fc1(x))
        x = torch.relu(self.fc2(x))
        return self.fc3(x)

env = gym.make('CartPole-v1')

state_dim = env.observation_space.shape[0]
action_dim = env.action_space.n

q_net = QNetwork(state_dim, action_dim)
target_net = QNetwork(state_dim, action_dim)
target_net.load_state_dict(q_net.state_dict())

optimizer = optim.Adam(q_net.parameters(), lr=0.001)
memory = deque(maxlen=2000)

batch_size = 64
gamma = 0.99
target_update = 10
episodes = 200

def select_action(state, epsilon):
    if random.random() < epsilon:
        return env.action_space.sample()
    state = torch.FloatTensor(state).unsqueeze(0)
    return q_net(state).argmax().item()

def replay():
    if len(memory) < batch_size:
        return

    batch = random.sample(memory, batch_size)
    states, actions, rewards, next_states, dones = zip(*batch)

    states = torch.FloatTensor(states)
    actions = torch.LongTensor(actions).unsqueeze(1)
    rewards = torch.FloatTensor(rewards).unsqueeze(1)
    next_states = torch.FloatTensor(next_states)
    dones = torch.FloatTensor(dones).unsqueeze(1)

    q_values = q_net(states).gather(1, actions)
    next_q_values = target_net(next_states).max(1)[0].unsqueeze(1)

    targets = rewards + gamma * next_q_values * (1 - dones)

    loss = nn.MSELoss()(q_values, targets)
    optimizer.zero_grad()
    loss.backward()
    optimizer.step()

epsilon = 1.0
epsilon_decay = 0.995
epsilon_min = 0.01

rewards_list = []

for ep in range(episodes):
    state, _ = env.reset()
    total_reward = 0
    terminated = False
    truncated = False

    while not terminated and not truncated:
        action = select_action(state, epsilon)
        next_state, reward, terminated, truncated, _ = env.step(action)
        done = terminated or truncated

        memory.append((state, action, reward, next_state, done))
        state = next_state
        total_reward += reward

        replay()

    rewards_list.append(total_reward)
    epsilon = max(epsilon_min, epsilon * epsilon_decay)

    if ep % target_update == 0:
        target_net.load_state_dict(q_net.state_dict())

plt.plot(rewards_list)
plt.xlabel("Episode")
plt.ylabel("Reward")
plt.title("DQN Learning Curve")
plt.show()

def moving_average(data, window=10):
    return np.convolve(data, np.ones(window)/window, mode='valid')

avg_rewards = moving_average(rewards_list, 10)

plt.plot(avg_rewards)
plt.xlabel("Episode")
plt.ylabel("Average Reward")
plt.title("Moving Average Reward")
plt.show()

'''
    return format_snippet(code)