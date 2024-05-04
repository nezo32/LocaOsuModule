import os
from agent import Agent
from buffer import ReplayBuffer

cwd = os.getcwd()
train_data_path = os.path.join(cwd, "tmp")
timestamp = os.listdir(train_data_path)[1].split("_")[1].split(".")[0]

memory = ReplayBuffer(64)
memory.load(timestamp)

agent = Agent((202, 260, 1), memory, n_epochs=50)
agent.load_models()

agent.learn()
agent.save_models()