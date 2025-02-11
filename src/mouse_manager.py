from threading import Thread
import time
import pyautogui
from pyclick.humancurve import HumanCurve
from pyclick.humanclicker import HumanClicker
from pynput.mouse import Controller, Button

class MouseManager():
    def __init__(self):
        self.__humanClicker = HumanClicker()
        self.__mouse = Controller()
        
        self.__leftButton = 0.0
        self.__rightButton = 0.0
    
    def __getCurve(self, x, y, target_points = 10):
        return HumanCurve(pyautogui.position(), (x, y), targetPoints=target_points)
    
    def GetButtonsState(self):
        return self.__leftButton, self.__rightButton

    def GetMousePosition(self):
        return pyautogui.position()
    
    def Reset(self):
        self.MouseClick(0)
    
    def MouseClick(self, click):
        if click == 0:
            self.__mouse.release(Button.left)
            self.__mouse.release(Button.right)
            self.__leftButton, self.__rightButton = 0.0, 0.0
        elif click == 1:
            self.__mouse.press(Button.left)
            self.__mouse.release(Button.right)
            self.__leftButton, self.__rightButton = 1.0, 0.0
        elif click == 2:
            self.__mouse.release(Button.left)
            self.__mouse.press(Button.right)
            self.__leftButton, self.__rightButton = 0.0, 1.0
    
    def MouseMove(self, x, y, t = 0.05):
        time.sleep(0.005)
        self.thread = Thread(target=self.__mouseMoveThread, args=[x, y, t])
        self.thread.start()
    
    def __mouseMoveThread(self, x, y, t):
        curve = self.__getCurve(x, y)
        self.__humanClicker.move((x, y), t, curve)
    
    def __del__(self):
        if self.thread is not None:
            self.thread.join()
        del self.__humanClicker
        del self.__mouse
        