# 📘 Machine Learning Snippet Generator (lerl)

A lightweight Python library that generates **ready-to-run Machine Learning code snippets** for students, beginners, and researchers working with AI algorithms.

This library does **not** run AI algorithms internally — instead, it returns **formatted, complete Python scripts** for:
- Monte Carlo Prediction  
- Temporal Difference (TD(0))  
- Policy Iteration  
- Value Iteration (coming soon)  
- + more upcoming AI algorithms  

You can copy the output, paste it into a Jupyter Notebook, Colab, VS Code, or PyCharm, and run it directly.

---

## 🚀 Features
✔ Generates complete RL scripts as strings  
✔ Code always follows correct RL implementations  
✔ Uses `format_snippet()` to return clean, properly formatted code  
✔ Ideal for learning, assignments, and quick experimentation  
✔ Zero dependencies for running the library itself  
✔ Works in: Jupyter Notebook, Google Colab, VS Code, Spyder, PyCharm  

---

## 📦 Installation

Install the package using pip:

```bash
pip install lerl

---
```

## Upgrade:

```bash
pip install --upgrade lerl
```

---

## 🧠 Available Code Snippet Functions

| Function Name                      | Algorithm                  | Description                                                         |
| ---------------------------------- | -------------------------- | ------------------------------------------------------------------- |
| `monte_carlo_code()`               | Monte Carlo Prediction     | Returns a full script for MC value estimation on FrozenLake         |
| `td_code()`                        | Temporal Difference (TD-0) | Generates complete TD learning code with convergence plots          |
| `complete_policy_iteration_code()` | Policy Iteration           | Returns policy evaluation + improvement + convergence visualization |
| `complete_value_iteration_code()`  | Value Iteration            | *(Coming soon — ready function placeholder)*                        |

---

## 📝 Example Usage

### ▶️ Generate Monte Carlo Snippet

```python
from lerl import monte_carlo_code

print(monte_carlo_code())
```

### ▶️ Generate TD(0) Snippet

```python
from lerl import td_code

print(td_code())
```

### ▶️ Generate Policy Iteration Code

```python
from lerl import complete_policy_iteration_code

print(complete_policy_iteration_code())
```

Each function returns a **complete runnable script** containing:

* Gym environment setup
* Algorithm implementation
* Value function updates
* Convergence plots
* Printed results

---

## 📚 Example Output (Short Preview)

```
import numpy as np
import gymnasium as gym
import matplotlib.pyplot as plt

env = gym.make('FrozenLake-v1', is_slippery = 'False')

def monte_carlo(env, policy, episodes = 10000, df = 0.99):
    ...
```

(Full script provided when calling the function.)

---

## 🏗 Internal Architecture

```
lerl/
│
├── __init__.py
├── qrl.py                # Main snippet-generating functions
├── utils.py              # format_snippet() helper
└── README.md
```

---

## 📜 License

This project is licensed under the MIT License.
Feel free to use it in academic or commercial projects.

---

## ⭐ Support

If this library helps you learn or build RL assignments, give it a ⭐ on GitHub and share it with your friends!

```

