# Reinforcement Learning Dino Game

A [`gymnasium`](https://gymnasium.farama.org/)-compatible reinforcement learning environment built on top of the classic offline **Chrome T-Rex Rush** game, used to train a **PPO** agent (via [Stable-Baselines3](https://stable-baselines3.readthedocs.io/)) to play the game on its own — no keyboard, no human input.

![Trained agent playing the Dino game](screenshot.gif)

## Watching the network think

The clip below plays a real episode from the trained agent side by side with its actual policy network — the same weights extracted from `dino_agente.zip`, live: 5 input sensors, two hidden layers (a real sample of the 64 neurons in each), and the 3 output actions with their softmax probabilities, updating frame by frame as the dino plays.

![Real PPO policy network playing the Dino game](dino_agent_demo.gif)

*(higher quality / real-time speed version: [dino_agent_demo.mp4](dino_agent_demo.mp4))*

## What this project is

The original game — [`T-Rex Rush`](https://github.com/shivamshekhar/Chrome-T-Rex-Rush) by Shivam Shekhar — is a Pygame clone of the dinosaur game that appears in Chrome when you're offline. That game itself was **not written for this project**; the sprites, physics, scoring and obstacle-spawning logic in `main.py` are the original, unmodified source.

What this project adds is everything needed to turn that human-controlled game into something an RL agent can train on:

- A decoupled **game engine** (`jogo.py`) that can be advanced one frame at a time from outside, instead of being driven by a `while` loop that reads real keyboard events and is locked to 60 FPS.
- A **Gymnasium environment wrapper** (`env.py`) that exposes the game through the standard `reset()` / `step()` / `render()` / `close()` interface expected by RL libraries.
- **Training, evaluation and inspection scripts** that use Stable-Baselines3's PPO implementation to learn a jumping/ducking policy purely from trial and error.

In short: the dinosaur no longer waits for `SPACE` or `↓` from a person — it waits for an action produced by a neural network.

## How it works

### 1. `jogo.py` — the game engine, decoupled from I/O

This is a rewrite of the original game's core loop (`Dino`, `Cactus`, `Ptera`, `Chao`/ground, collision detection, scoring/speed progression) exposed through a `Jogo` class with two key methods:

- `reiniciar()` — resets the game state for a new episode.
- `passo(acao)` — advances exactly **one frame**, applying `acao` (0 = do nothing, 1 = jump, 2 = duck) instead of a real key press, and returns whether the dino died on that frame.

Rendering and the 60 FPS clock are optional (`Jogo(renderizar=False)`), so during training the game can be simulated far faster than real time. A third method, `obter_estado()`, exposes the raw game state needed to build an observation:

- distance to the next obstacle
- height of the next obstacle
- current game speed
- dino's vertical position
- dino's vertical velocity

### 2. `env.py` — the Gymnasium wrapper

`DinoEnv(gym.Env)` translates the raw game state above into the standard RL vocabulary:

- **Action space**: `Discrete(3)` — do nothing / jump / duck.
- **Observation space**: `Box(5,)` — the five state values described above.
- **Reward**: `+1` for every frame survived, `-100` when the dino collides with an obstacle.

This is the layer that makes the game "pluggable" into any Gymnasium-compatible RL algorithm, including Stable-Baselines3's PPO used here.

### 3. Training, testing and watching the agent

| Script | Purpose |
|---|---|
| `testar_ambiente.py` | Sanity-checks the environment by running a few episodes with **random** actions (no learning) — useful to confirm `env.py`/`jogo.py` behave correctly. |
| `treinar_agente.py` | Trains a `PPO` agent (`MlpPolicy`) on `DinoEnv` for 10,000,000 timesteps and saves the result as `dino_agente` (shipped in this repo as `dino_agente.zip`). |
| `ver_agente.py` | Loads the trained `dino_agente` model, renders the game window, and lets the agent play a full episode on its own. |

`main.py` is kept in the repo as the original, playable, human-controlled version of the game for reference/comparison. `main.exe` is a compiled build of it.

## Main tools used

- **[Python](https://www.python.org/)** — project language.
- **[Pygame](https://www.pygame.org/)** — game engine/rendering, inherited from the original T-Rex Rush implementation.
- **[Gymnasium](https://gymnasium.farama.org/)** — standard RL environment API (`gym.Env`, action/observation spaces).
- **[Stable-Baselines3](https://stable-baselines3.readthedocs.io/)** — RL algorithm implementations; this project uses **PPO** (Proximal Policy Optimization) with a simple `MlpPolicy` (since observations are a small numeric vector, not pixels).
- **[NumPy](https://numpy.org/)** — building the observation arrays passed to the agent.

## Getting started

```bash
pip install -r requirements.txt

# 1. Sanity-check the environment with random actions
python testar_ambiente.py

# 2. Train a new agent from scratch (this took the full 10M timesteps for the included dino_agente model)
python treinar_agente.py

# 3. Watch a trained agent play
python ver_agente.py
```

## Credits

- Original game (`main.py` and all sprites/sounds): [T-Rex Rush](https://github.com/shivamshekhar/Chrome-T-Rex-Rush) by **Shivam Shekhar**.
- RL environment, engine refactor and agent training (`jogo.py`, `env.py`, `treinar_agente.py`, `testar_ambiente.py`, `ver_agente.py`): this repository.
