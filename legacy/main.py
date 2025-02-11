import ctypes
import pyautogui
import win32con
import time
import numpy as np
from win32 import win32api
import threading
import argparse
from copy import deepcopy
from agent import Agent
from env import Environment
from buffer import ReplayBuffer
from constants import MARGIN_LEFT, MARGIN_TOP, PLAYGROUND_WIDTH, PLAYGROUND_HEIGHT, THREAD_CLOSE_EVENT, REWARD_PRICE

from memory.functions import GetAcc, GetOsuHandle, CloseOsuHandle, GetBaseAddress, GetStateData, \
                             GetHitsData, ClearHitsData, GetH300, GetH100, GetH50, GetHMiss, \
                             GetCombo, GetMaxCombo, GetRulesetsSigPage, GetStatusSigPage, ClearSigPage, CreateHitsData, ResumeProcess, SuspendProcess


parser = argparse.ArgumentParser()
parser.add_argument('--load-models', default=False, action=argparse.BooleanOptionalAction)
args = parser.parse_args()

TRAIN_FLAG = False
END_FLAG = False
TERMINATE_FLAG = False
CLEAR_FLAG = False

def keyThread():
    global TRAIN_FLAG, END_FLAG, TERMINATE_FLAG, CLEAR_FLAG
    while True:
        if win32api.GetAsyncKeyState(win32con.VK_RCONTROL) < 0: 
            if END_FLAG:
                END_FLAG = False
            else:
                END_FLAG = True
            time.sleep(0.7)
            
        if win32api.GetAsyncKeyState(win32con.VK_END) < 0:
            TERMINATE_FLAG = True
        
        if win32api.GetAsyncKeyState(win32con.VK_HOME) < 0:
            if CLEAR_FLAG:
                CLEAR_FLAG = False
            else:
                CLEAR_FLAG = True
            time.sleep(0.7)
            
        if win32api.GetAsyncKeyState(win32con.VK_F11) < 0:
            if TRAIN_FLAG:
                TRAIN_FLAG = False
            else:
                TRAIN_FLAG = True
            time.sleep(0.7)
        if THREAD_CLOSE_EVENT.is_set():
            break


def calculateReward(currentHits, hitsCounter):
    hitsArray = np.asarray(hitsCounter)
    currentArray = np.asarray(currentHits)
    
    diff = np.subtract(currentArray, hitsArray)
    
    reward = diff[0] * REWARD_PRICE[0] + diff[1] * REWARD_PRICE[1] + \
             diff[2] * REWARD_PRICE[2] + diff[3] * REWARD_PRICE[3] + \
             diff[4] * REWARD_PRICE[3] - 0.1
    
    return reward
    
def getHitsData(hits, hitsCounter, sbCount):
    h300 = GetH300(hits)
    h100 = GetH100(hits)
    h50 = GetH50(hits)
    hMiss = GetHMiss(hits)
    combo = GetCombo(hits)
    maxCombo = GetMaxCombo(hits)
    acc = GetAcc(hits)
    
    if hitsCounter[-1] > maxCombo:
        hitsCounter[-1] = 0
    
    if combo < hitsCounter[-2] and hMiss == hitsCounter[3]:
        sbCount[0] += 1
        
    return [h300, h100, h50, hMiss, sbCount[0], combo, maxCombo, acc]
    
def main(handle, pid: ctypes.c_ulong):
    global TRAIN_FLAG, END_FLAG, args
    
    sigPageR = GetRulesetsSigPage(handle)
    sigPageS = GetStatusSigPage(handle)
    hits = CreateHitsData()
    
    memory = ReplayBuffer(64)
    agent = Agent((202, 260, 1), memory)
    
    if (args.load_models):
        agent.load_models()
    
    def save_data():
        print('\n... saving data ...')
        agent.save_models()
        print('... saved...\n')
    
    keyHandler = threading.Thread(target=keyThread)
    keyHandler.start()
    
    print('\nRCTRL save data without exiting')
    print('F11 start training loop (need to be in map)')
    print('END save data and exit the program\n')
    
    hitsCounter = [0, 0, 0, 0, 0, 0, 0]
    sbCount = [0]

    print('\n... starting main loop ...')
    baseAddressR = GetBaseAddress(handle, sigPageR)
    baseAddressS = GetBaseAddress(handle, sigPageS)
    """ pyautogui.screenshot("failed.png", region=(832, 95, 180, 40))
    pyautogui.screenshot("paused.png", region=(832, 95, 250, 40))
    pyautogui.screenshot("score.png", region=(1610, 7, 300, 88)) """
    
    while True:
        
        image, _ = Environment.grabScreen((MARGIN_LEFT, MARGIN_TOP, PLAYGROUND_WIDTH, PLAYGROUND_HEIGHT))
        mousePosition = Environment.grabMousePosition()
        mousePress = Environment.getMousePressState()
        
        inGameState = GetStateData(handle, baseAddressS)
        hits = GetHitsData(handle, baseAddressR, hits)
        currentHits = getHitsData(hits, hitsCounter, sbCount)
        print("InGameState: " + str(inGameState) + " currentHits: " + str(currentHits))
        
        #agent.sample_action(image, mousePosition, mousePress)
        """ if (TRAIN_FLAG and inGameState == 2):
            # Action
            actions, log_prob = agent.sample_action(image, mousePosition, mousePress)
            Environment.step(actions)
            
            # Reward
            hits = GetHitsData(handle, baseAddressR, hits)
            currentHits = getHitsData(hits, hitsCounter, sbCount)
            reward = calculateReward(currentHits, hitsCounter)
            
            # Store memory
            memory.store_memory(image, mousePosition, mousePress, actions, log_prob, reward)
            
            if (memory.length() % 64 == 0):
                SuspendProcess(handle)
                agent.learn()
                ResumeProcess(handle)

            # Save current & clear memory
            hitsCounter = deepcopy(currentHits)
            
        else:
            sbCount = [0]
            hitsCounter = [0, 0, 0, 0, 0, 0, 0] """
        
        if END_FLAG:
            save_data()
            memory.clear_memory()
            END_FLAG = False
            
        if CLEAR_FLAG:
            agent.learn()
            
        
        if TERMINATE_FLAG:
            save_data()
            memory.clear_memory()
            break
    ClearHitsData(hits)
    ClearSigPage(sigPageR)
    ClearSigPage(sigPageS)      
        

if __name__=='__main__':
    pid = ctypes.c_ulong()
    handle = GetOsuHandle(ctypes.byref(pid))
    try:
        main(handle, pid)
    finally:
        print("Exiting program. Clearing threads...\n")
        ResumeProcess(handle)
        CloseOsuHandle(handle)
        THREAD_CLOSE_EVENT.set()