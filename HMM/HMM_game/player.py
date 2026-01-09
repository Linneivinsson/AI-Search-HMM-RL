#!/usr/bin/env python3

from player_controller_hmm import PlayerControllerHMMAbstract
from constants import *
import random
import math


class PlayerControllerHMM(PlayerControllerHMMAbstract):
    def init_parameters(self):
        """
        In this function you should initialize the parameters you will need,
        such as the initialization of models, or fishes, among others.
        """
        self.fish_observations = [[] for _ in range(N_FISH)]
        self.fish_known_type = [None] * N_FISH
        self.guessed_fish = [False] * N_FISH
        self.total_guesses = 0

        self.emission_counts = [{} for _ in range(N_SPECIES)]
        self.emission_total = [0] * N_SPECIES
        self.species_counts = [0] * N_SPECIES
        self.all_obs = set()

        self.min_seq_len = 5
        self.confidence_threshold = 0.25
        self.force_guess_step = 150
        self.initial_random_guesses = N_SPECIES
        self.initial_wait_steps = 10
        pass

    def _update_emission(self, species, obs):
        d = self.emission_counts[species]
        d[obs] = d.get(obs, 0) + 1
        self.emission_total[species] += 1
        self.all_obs.add(obs)

    def _posterior_probs(self, seq):
        if not self.all_obs:
            v_size = 1
        else:
            v_size = len(self.all_obs)
        alpha = 1.0
        total_fish = sum(self.species_counts) + N_SPECIES
        scores = []
        for s in range(N_SPECIES):
            total = self.emission_total[s]
            counts = self.emission_counts[s]
            prior = (self.species_counts[s] + 1) / total_fish
            logp = math.log(prior)
            denom = total + alpha * v_size
            if denom == 0.0:
                prob = 1.0 / v_size
                logp += len(seq) * math.log(prob)
            else:
                for obs in seq:
                    c = counts.get(obs, 0)
                    num = c + alpha
                    logp += math.log(num / denom)
            scores.append(logp)
        max_score = max(scores)
        exps = [math.exp(s - max_score) for s in scores]
        total = sum(exps)
        return [e / total for e in exps]

    def guess(self, step, observations):
        """
        This method gets called on every iteration, providing observations.
        Here the player should process and store this information,
        and optionally make a guess by returning a tuple containing the fish index and the guess.
        :param step: iteration number
        :param observations: a list of N_FISH observations, encoded as integers
        :return: None or a tuple (fish_id, fish_type)
        """
        for fish_id, obs in enumerate(observations):
            self.fish_observations[fish_id].append(obs)
            species = self.fish_known_type[fish_id]
            if species is not None:
                self._update_emission(species, obs)

        if self.total_guesses >= N_FISH:
            return None

        if step >= self.initial_wait_steps and self.total_guesses < self.initial_random_guesses:
            candidates = [i for i in range(N_FISH) if not self.guessed_fish[i]]
            if candidates:
                fish_id = max(candidates, key=lambda i: len(self.fish_observations[i]))
                guess_type = random.randint(0, N_SPECIES - 1)
                self.guessed_fish[fish_id] = True
                self.total_guesses += 1
                return (fish_id, guess_type)

        if any(self.emission_total[s] > 0 for s in range(N_SPECIES)):
            best_fish = None
            best_species = None
            best_margin = 0.0
            for fish_id in range(N_FISH):
                if self.guessed_fish[fish_id]:
                    continue
                if len(self.fish_observations[fish_id]) < self.min_seq_len:
                    continue
                probs = self._posterior_probs(self.fish_observations[fish_id])
                p1 = 0.0
                p2 = 0.0
                best_s = 0
                for s, p in enumerate(probs):
                    if p > p1:
                        p2 = p1
                        p1 = p
                        best_s = s
                    elif p > p2:
                        p2 = p
                margin = p1 - p2
                if margin > best_margin:
                    best_margin = margin
                    best_fish = fish_id
                    best_species = best_s
            if best_fish is not None and best_margin >= self.confidence_threshold:
                self.guessed_fish[best_fish] = True
                self.total_guesses += 1
                return (best_fish, best_species)

        if step >= self.force_guess_step:
            candidates = [i for i in range(N_FISH) if not self.guessed_fish[i]]
            if candidates:
                fish_id = max(candidates, key=lambda i: len(self.fish_observations[i]))
                if any(self.emission_total[s] > 0 for s in range(N_SPECIES)):
                    probs = self._posterior_probs(self.fish_observations[fish_id])
                    best_species = max(range(N_SPECIES), key=lambda s: probs[s])
                else:
                    best_species = random.randint(0, N_SPECIES - 1)
                self.guessed_fish[fish_id] = True
                self.total_guesses += 1
                return (fish_id, best_species)

        # This code would make a random guess on each step:
        # return (step % N_FISH, random.randint(0, N_SPECIES - 1))

        return None

    def reveal(self, correct, fish_id, true_type):
        """
        This methods gets called whenever a guess was made.
        It informs the player about the guess result
        and reveals the correct type of that fish.
        :param correct: tells if the guess was correct
        :param fish_id: fish's index
        :param true_type: the correct type of the fish
        :return:
        """
        self.fish_known_type[fish_id] = true_type
        self.species_counts[true_type] += 1
        for obs in self.fish_observations[fish_id]:
            self._update_emission(true_type, obs)
        pass