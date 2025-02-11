import numpy as np
from numpy import save, load
import calendar
import time

class ReplayBuffer:
    def __init__(self, batch_size, save_dir="./tmp/"):
        self.imageStates = []
        self.mousePositionStates = []
        self.mousePressStates = []
        self.actions = []
        self.probs = []
        self.rewards = []

        self.save_dir = save_dir
        self.batch_size = batch_size

    def generate_batches(self):
        n_states = len(self.imageStates)
        batch_start = np.arange(0, n_states, self.batch_size)
        indices = np.arange(n_states, dtype=np.int64)
        np.random.shuffle(indices)
        batches = [indices[i:i+self.batch_size] for i in batch_start]

        return np.array(self.imageStates),\
            np.array(self.mousePositionStates), \
            np.array(self.mousePressStates), \
            np.array(self.actions), \
            np.array(self.probs), \
            np.array(self.rewards), \
            batches

    def store_memory(self, image, mousePosition, mousePress, actions, probs, reward):
        self.imageStates.append(np.copy(image))
        self.mousePositionStates.append(np.copy(mousePosition))
        self.mousePressStates.append(np.copy(mousePress))
        self.actions.append(np.copy(actions))
        self.probs.append(np.copy(probs))
        self.rewards.append(reward)

    def clear_memory(self):
        self.imageStates = []
        self.mousePositionStates = []
        self.mousePressStates = []
        self.actions = []
        self.probs = []
        self.rewards = []
    
    def length(self):
        return len(self.imageStates)