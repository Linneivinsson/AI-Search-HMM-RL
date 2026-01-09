#!/usr/bin/env python3
import random
import heapq
import numpy as np

from agent import Fish
from communicator import Communicator
from shared import SettingLoader


class FishesModelling:
    def init_fishes(self, n):
        fishes = {}
        for i in range(n):
            fishes["fish" + str(i)] = Fish()
        self.fishes = fishes


class PlayerController(SettingLoader, Communicator):
    def __init__(self):
        SettingLoader.__init__(self)
        Communicator.__init__(self)
        self.space_subdivisions = 10
        self.actions = None
        self.action_list = None
        self.states = None
        self.init_state = None
        self.ind2state = None
        self.state2ind = None
        self.alpha = 0
        self.gamma = 0
        self.episode_max = 300

    def init_states(self):
        ind2state = {}
        state2ind = {}
        count = 0
        for row in range(self.space_subdivisions):
            for col in range(self.space_subdivisions):
                ind2state[(col, row)] = count
                state2ind[count] = [col, row]
                count += 1
        self.ind2state = ind2state
        self.state2ind = state2ind

    def init_actions(self):
        self.actions = {
            "left": (-1, 0),
            "right": (1, 0),
            "down": (0, -1),
            "up": (0, 1)
        }
        self.action_list = list(self.actions.keys())

    def allowed_movements(self):
        self.allowed_moves = {}
        for s in self.ind2state.keys():
            self.allowed_moves[self.ind2state[s]] = []
            if s[0] < self.space_subdivisions - 1:
                self.allowed_moves[self.ind2state[s]] += [1]
            if s[0] > 0:
                self.allowed_moves[self.ind2state[s]] += [0]
            if s[1] < self.space_subdivisions - 1:
                self.allowed_moves[self.ind2state[s]] += [3]
            if s[1] > 0:
                self.allowed_moves[self.ind2state[s]] += [2]

    def player_loop(self):
        pass


class PlayerControllerHuman(PlayerController):
    def player_loop(self):
        """
        Function that generates the loop of the game. In each iteration
        the human plays through the keyboard and send
        this to the game through the sender. Then it receives an
        update of the game through receiver, with this it computes the
        next movement.
        :return:
        """

        while True:
            # send message to game that you are ready
            msg = self.receiver()
            if msg["game_over"]:
                return


def epsilon_greedy(Q,
                   state,
                   all_actions,
                   current_total_steps=0,
                   epsilon_initial=1,
                   epsilon_final=0.2,
                   anneal_timesteps=10000,
                   eps_type="constant"):

    if eps_type == 'constant':
        epsilon = epsilon_final
        # ADD YOUR CODE SNIPPET BETWEEN EX 4.1
        # Implemenmt the epsilon-greedy algorithm for a constant epsilon value
        # Use epsilon and all input arguments of epsilon_greedy you see fit
        # It is recommended you use the np.random module
        if np.random.random() < epsilon:
            action = int(np.random.choice(all_actions))
        else:
            q_vals = Q[state, all_actions]
            max_q = np.nanmax(q_vals)
            best = [a for a, q in zip(all_actions, q_vals) if q == max_q]
            action = int(np.random.choice(best))
        # ADD YOUR CODE SNIPPET BETWEEN EX 4.1

    elif eps_type == 'linear':
        # ADD YOUR CODE SNIPPET BETWEENEX  4.2
        # Implemenmt the epsilon-greedy algorithm for a linear epsilon value
        # Use epsilon and all input arguments of epsilon_greedy you see fit
        # use the ScheduleLinear class
        # It is recommended you use the np.random module
        schedule = ScheduleLinear(anneal_timesteps,
                                  final_p=epsilon_final,
                                  initial_p=epsilon_initial)
        epsilon = schedule.value(current_total_steps)
        if np.random.random() < epsilon:
            action = int(np.random.choice(all_actions))
        else:
            q_vals = Q[state, all_actions]
            max_q = np.nanmax(q_vals)
            best = [a for a, q in zip(all_actions, q_vals) if q == max_q]
            action = int(np.random.choice(best))
        # ADD YOUR CODE SNIPPET BETWEENEX  4.2

    else:
        raise "Epsilon greedy type unknown"

    return action


class PlayerControllerRL(PlayerController, FishesModelling):
    def __init__(self):
        super().__init__()

    def player_loop(self):
        # send message to game that you are ready
        self.init_actions()
        self.init_states()
        self.allowed_movements()
        policy = self.compute_policy()

        msg = {"policy": policy, "exploration": False}
        self.sender(msg)

        while True:
            self.receiver()

    def compute_policy(self):
        n = self.space_subdivisions
        target = tuple(self.settings.pos_king)
        jellies = set(zip(self.settings.jelly_x, self.settings.jelly_y))

        inf = 10**18

        dist_steps = [[inf for _ in range(n)] for _ in range(n)]
        dist_jelly = [[inf for _ in range(n)] for _ in range(n)]
        tx, ty = target
        dist_steps[ty][tx] = 0
        dist_jelly[ty][tx] = 0
        heap = [(0, 0, tx, ty)]

        while heap:
            ds, dj, x, y = heapq.heappop(heap)
            if ds != dist_steps[y][x] or dj != dist_jelly[y][x]:
                continue
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nx, ny = x + dx, y + dy
                if nx < 0 or nx >= n or ny < 0 or ny >= n:
                    continue
                ns = ds + 1
                nj = dj + (1 if (nx, ny) in jellies else 0)
                if (ns < dist_steps[ny][nx]) or (ns == dist_steps[ny][nx] and nj < dist_jelly[ny][nx]):
                    dist_steps[ny][nx] = ns
                    dist_jelly[ny][nx] = nj
                    heapq.heappush(heap, (ns, nj, nx, ny))

        policy = {}
        for y in range(n):
            for x in range(n):
                if (x, y) == target:
                    policy[(x, y)] = "up"
                    continue

                best_action = "up"
                best_steps = inf
                best_jelly = inf
                for action, (dx, dy) in self.actions.items():
                    nx, ny = x + dx, y + dy
                    if nx < 0 or nx >= n or ny < 0 or ny >= n:
                        continue
                    ns = 1 + dist_steps[ny][nx]
                    nj = (1 if (nx, ny) in jellies else 0) + dist_jelly[ny][nx]
                    if (ns < best_steps) or (ns == best_steps and nj < best_jelly):
                        best_steps = ns
                        best_jelly = nj
                        best_action = action

                policy[(x, y)] = best_action
        return policy

    def q_learning(self):
        ns = len(self.state2ind.keys())
        na = len(self.actions.keys())
        discount = self.gamma
        lr = self.alpha
        self.allowed_movements()
        Q = np.random.random((ns, na))

        for s in range(ns):
            list_pos = self.allowed_moves[s]
            for i in range(4):
                if i not in list_pos:
                    Q[s, i] = np.nan

        Q_old = Q.copy()

        diff = np.infty
        end_episode = False

        init_pos_tuple = self.settings.init_pos_diver
        init_pos = self.ind2state[(init_pos_tuple[0], init_pos_tuple[1])]
        episode = 0

        current_total_steps = 0
        max_total_steps = 2000
        max_episodes = 50

        while episode <= min(self.episode_max, max_episodes) and diff > self.threshold and current_total_steps < max_total_steps:
            s_current = init_pos
            while not end_episode and current_total_steps < max_total_steps:
                list_pos = self.allowed_moves[s_current]

                action = epsilon_greedy(Q,
                                       s_current,
                                       list_pos,
                                       current_total_steps=current_total_steps,
                                       epsilon_initial=self.epsilon_initial,
                                       epsilon_final=min(self.epsilon_final, 0.2),
                                       anneal_timesteps=self.annealing_timesteps,
                                       eps_type="linear")

                action_str = self.action_list[action]
                msg = {"action": action_str, "exploration": True}
                self.sender(msg)

                msg = self.receiver()
                R = msg["reward"]
                s_next_tuple = msg["state"]
                end_episode = msg["end_episode"]
                s_next = self.ind2state[s_next_tuple]

                if end_episode:
                    target = R
                else:
                    target = R + discount * np.nanmax(Q[s_next])
                Q[s_current, action] = Q[s_current, action] + lr * (target - Q[s_current, action])

                s_current = s_next
                current_total_steps += 1

            diff = np.nanmean(np.abs(Q - Q_old))
            Q_old[:] = Q
            episode += 1
            end_episode = False

        return Q

    def get_policy(self, Q):
        max_actions = np.nanargmax(Q, axis=1)
        policy = {}
        list_actions = list(self.actions.keys())
        for n in self.state2ind.keys():
            state_tuple = self.state2ind[n]
            policy[(state_tuple[0],
                    state_tuple[1])] = list_actions[max_actions[n]]
        return policy


class PlayerControllerRandom(PlayerController):
    def __init__(self):
        super().__init__()

    def player_loop(self):

        self.init_actions()
        self.init_states()
        self.allowed_movements()
        self.episode_max = self.settings.episode_max

        n = self.random_agent()

        # compute policy
        policy = self.get_policy(n)

        # send policy
        msg = {"policy": policy, "exploration": False}
        self.sender(msg)

        msg = self.receiver()
        print("Random Agent returning")
        return

    def random_agent(self):
        ns = len(self.state2ind.keys())
        na = len(self.actions.keys())
        init_pos_tuple = self.settings.init_pos_diver
        init_pos = self.ind2state[(init_pos_tuple[0], init_pos_tuple[1])]
        episode = 0
        R_total = 0
        steps = 0
        current_total_steps = 0
        end_episode = False
        # ADD YOUR CODE SNIPPET BETWEEN EX. 1.2
        # Initialize a numpy array with ns state rows and na state columns with zeros
        n = np.zeros((ns, na))
        for s in range(ns):
            allowed = self.allowed_moves[s]
            for a in range(na):
                if a not in allowed:
                    n[s, a] = np.nan
        # ADD YOUR CODE SNIPPET BETWEEN EX. 1.2

        while episode <= self.episode_max:
            s_current = init_pos
            R_total = 0
            steps = 0
            while not end_episode:
                # all possible actions
                possible_actions = self.allowed_moves[s_current]

                # ADD YOUR CODE SNIPPET BETWEEN EX. 1.2
                # Chose an action from all possible actions and add to the counter of actions per state
                action = int(np.random.choice(possible_actions))
                n[s_current, action] += 1.0
                # ADD YOUR CODE SNIPPET BETWEEN EX. 1.2

                action_str = self.action_list[action]
                msg = {"action": action_str, "exploration": True}
                self.sender(msg)

                # wait response from game
                msg = self.receiver()
                R = msg["reward"]
                s_next_tuple = msg["state"]
                end_episode = msg["end_episode"]
                s_next = self.ind2state[s_next_tuple]
                s_current = s_next
                R_total += R
                current_total_steps += 1
                steps += 1

            print("Episode: {}, Steps {}, Total Reward: {}, Total Steps {}".
                  format(episode, steps, R_total, current_total_steps))
            episode += 1
            end_episode = False

        return n

    def get_policy(self, Q):
        nan_max_actions_proxy = [None for _ in range(len(Q))]
        for _ in range(len(Q)):
            try:
                nan_max_actions_proxy[_] = np.nanargmax(Q[_])
            except:
                nan_max_actions_proxy[_] = np.random.choice([0, 1, 2, 3])

        nan_max_actions_proxy = np.array(nan_max_actions_proxy)

        assert nan_max_actions_proxy.all() == nan_max_actions_proxy.all()

        policy = {}
        list_actions = list(self.actions.keys())
        for n in self.state2ind.keys():
            state_tuple = self.state2ind[n]
            policy[(state_tuple[0],
                    state_tuple[1])] = list_actions[nan_max_actions_proxy[n]]
        return policy


class ScheduleLinear(object):
    def __init__(self, schedule_timesteps, final_p, initial_p=1.0):
        self.schedule_timesteps = schedule_timesteps
        self.final_p = final_p
        self.initial_p = initial_p

    def value(self, t):
        # ADD YOUR CODE SNIPPET BETWEEN EX 4.2
        # Return the annealed linear value
        if self.schedule_timesteps <= 0:
            return self.final_p
        fraction = min(float(t) / float(self.schedule_timesteps), 1.0)
        return self.initial_p + fraction * (self.final_p - self.initial_p)
        # ADD YOUR CODE SNIPPET BETWEEN EX 4.2
