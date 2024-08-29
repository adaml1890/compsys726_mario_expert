"""
This the primary class for the Mario Expert agent. It contains the logic for the Mario Expert agent to play the game and choose actions.

Your goal is to implement the functions and methods required to enable choose_action to select the best action for the agent to take.

Original Mario Manual: https://www.thegameisafootarcade.com/wp-content/uploads/2017/04/Super-Mario-Land-Game-Manual.pdf
"""

import json
import logging
import random
import time

import cv2
from mario_environment import MarioEnvironment
from pyboy.utils import WindowEvent
from enum import Enum
import numpy as np


class MarioController(MarioEnvironment):
    """
    The MarioController class represents a controller for the Mario game environment.

    You can build upon this class all you want to implement your Mario Expert agent.

    Args:
        act_freq (int): The frequency at which actions are performed. Defaults to 10.
        emulation_speed (int): The speed of the game emulation. Defaults to 0.
        headless (bool): Whether to run the game in headless mode. Defaults to False.
    """
    overRideFlag = False
    prevActions = (0,0)

    def __init__(
        self,
        act_freq: int = 7,
        emulation_speed: int = 1,
        headless: bool = False,
    ) -> None:
        super().__init__(
            act_freq=act_freq,
            emulation_speed=emulation_speed,
            headless=headless,
        )

        self.act_freq = act_freq

        # Example of valid actions based purely on the buttons you can press
        valid_actions: list[WindowEvent] = [
            WindowEvent.PRESS_ARROW_DOWN,
            WindowEvent.PRESS_ARROW_LEFT,
            WindowEvent.PRESS_ARROW_RIGHT,
            WindowEvent.PRESS_ARROW_UP,
            WindowEvent.PRESS_BUTTON_A,
            WindowEvent.PRESS_BUTTON_B,
        ]

        release_button: list[WindowEvent] = [
            WindowEvent.RELEASE_ARROW_DOWN,
            WindowEvent.RELEASE_ARROW_LEFT,
            WindowEvent.RELEASE_ARROW_RIGHT,
            WindowEvent.RELEASE_ARROW_UP,
            WindowEvent.RELEASE_BUTTON_A,
            WindowEvent.RELEASE_BUTTON_B,
        ]

        self.valid_actions = valid_actions
        self.release_button = release_button

    def run_action(self, actions) -> None:
        """
        Executes one or multiple actions at once.

        Args:
            actions: A single action (int) or a list of actions to be performed.
        """

        if isinstance(actions, int):
            actions = [actions]

        # Press each button in the actions list
        for action in actions:
            self.pyboy.send_input(self.valid_actions[action])

        # Hold the buttons for the specified duration
        for _ in range(self.act_freq):
            self.pyboy.tick()

        # Release each button in the actions list
        for action in actions:
            self.pyboy.send_input(self.release_button[action])
        
        self.prevActions = actions













class MarioExpert:
    """
    The MarioExpert class represents an expert agent for playing the Mario game.

    Edit this class to implement the logic for the Mario Expert agent to play the game.

    Do NOT edit the input parameters for the __init__ method.

    Args:
        results_path (str): The path to save the results and video of the gameplay.
        headless (bool, optional): Whether to run the game in headless mode. Defaults to False.
    """
    
    marioLocationX = 0
    marioLocationY = 0
    counter = 0
    
    
    class actions(Enum):
        DOWN_ARROW = 0
        LEFT_ARROW = 1
        RIGHT_ARROW = 2
        UP_ARROW = 3
        BUTTON_A = 4
        BUTTON_B = 5
    
    class icons(Enum):
        GOOMBA = 15
        GROUND = 10
        BLOCK = 12
        POWERUP = 6
        PIPE = 14
        ITEMBLOCK = 13
        MARIO = 1
        EMPTY = 0
        FLY = 18
        ARCHER = 14
        KOOPA = 16
        END_PLATFORM = 11


    def findMario(self, game_area):
        [x,y] = game_area.shape
        for i in range(x-1):
            for j in range(y-1):
                if game_area[i][j] == MarioExpert.icons.MARIO.value:
                    return (i,j)
        else:
            return 5,5
        
    def entityRespondY(self, game_area):
        [marioY,marioX] = self.findMario(game_area) #Finds Mario's coords
        [x,y] = game_area.shape
        if marioX > 14:
            return 1, False
        for i in range(marioY-3,marioY+1): #This loop checks 3 grids ahead of mario on varying y levels.
            # print(i)
            if game_area[i][marioX+3] == MarioExpert.icons.GOOMBA.value: #GOOMBA ON TOP
                # print("Jump")
                self.initialStep = self.stepCount
                actionY = (MarioExpert.actions.LEFT_ARROW.value,2)
                return actionY, True #Action = LEFT.
            if game_area[i][marioX+2] == MarioExpert.icons.GOOMBA.value: #GOOMBA ON TOP
                # print("Left")
                self.initialStep = self.stepCount
                actionY = MarioExpert.actions.LEFT_ARROW.value
                return actionY, True #Action = LEFT.
            if game_area[11][marioX+4] == MarioExpert.icons.FLY.value: #Fly case
                # print("Jump")
                actionY = (MarioExpert.actions.BUTTON_A.value,2)
                return actionY, True       
            if game_area[15][marioX+2] == MarioExpert.icons.EMPTY.value: #Hole   
                # print("Jump")     
                actionY = int(MarioExpert.actions.BUTTON_A.value)
                return (actionY,2),True 
            
            if game_area[i][marioX+3] == MarioExpert.icons.GROUND.value: #GROUND ON TOP
                actionY = (MarioExpert.actions.BUTTON_A.value,2)
                return actionY, True     
            else:
                return 1,False 
    
    def entityRespondX(self, game_area): #override flag for if the Y axis has an input.
        [marioY,marioX] = self.findMario(game_area) #Finds Mario's coords
        [x,y] = game_area.shape
        if marioX > 14:
            return 2

        for i in range(marioX+2,marioX+5): #This loop checks 2 grids ahead of mario on the same y level.
            
            if game_area[marioY+1][i] == MarioExpert.icons.GOOMBA.value: #GOOMBA
                
                return (MarioExpert.actions.BUTTON_A.value,2) #Action = JUMP.
            if game_area[marioY][i] == MarioExpert.icons.ARCHER.value: #ARCHER
                
                return (MarioExpert.actions.BUTTON_A.value,2)
            if game_area[marioY+1][i] == MarioExpert.icons.FLY.value: #FLY
                
                return (MarioExpert.actions.BUTTON_A.value,2)
            if game_area[marioY][i] == MarioExpert.icons.KOOPA.value: #KOOPATROOPA

                return (MarioExpert.actions.BUTTON_A.value)
            if game_area[marioY][i] == MarioExpert.icons.PIPE.value: #PIPE
                
                return (MarioExpert.actions.BUTTON_A.value,2)
            if game_area[marioY+1][i] == MarioExpert.icons.GROUND.value: #GROUND

                return (MarioExpert.actions.BUTTON_A.value,2)
            if game_area[marioY+1][i] == MarioExpert.icons.EMPTY.value: #EMPTY
                return (MarioExpert.actions.RIGHT_ARROW.value)
            else:
                return 2
        #Make one that checks under mario for air (jump to not fall off)
            
            #Maybe call actions sequence inside here? instead of returning? Therefore you can have combinations.
            



    def __init__(self, results_path: str, headless=False):
        
        self.results_path = results_path

        self.environment = MarioController(headless=headless)

        self.video = None
        
        self.stepCount = 0

        self.initialStep = 0

     
    def choose_action(self):
        state = self.environment.game_state()
        frame = self.environment.grab_frame()
        game_area = self.environment.game_area()
        print(game_area)
        # Implement your code here to choose the best action
        [action1,self.environment.overRideFlag] = self.entityRespondY(game_area)
        
        if self.stepCount - self.initialStep <= 10 or self.environment.overRideFlag is True:
            action = action1
        
        elif self.environment.overRideFlag is False:
            action = self.entityRespondX(game_area)
            
        if self.environment.prevActions == action:
            self.counter+=1
        
        elif self.environment.prevActions != action:
            self.counter = 0
            
        if self.counter == 5:
            self.counter = 0
            return 3
        
        return action
    

    def step(self):
        """
        Modify this function as required to implement the Mario Expert agent's logic.

        This is just a very basic example
        """
        self.stepCount+=1
        # Choose an action - button press or other...
        action = self.choose_action()
        self.environment.run_action(action)



    ## FROM HERE ONWARDS DONT
    def play(self):
        """
        Do NOT edit this method.
        """
        self.environment.reset()

        frame = self.environment.grab_frame()
        height, width, _ = frame.shape

        self.start_video(f"{self.results_path}/mario_expert.mp4", width, height)

        while not self.environment.get_game_over():
            frame = self.environment.grab_frame()
            self.video.write(frame)

            self.step()

        final_stats = self.environment.game_state()
        logging.info(f"Final Stats: {final_stats}")

        with open(f"{self.results_path}/results.json", "w", encoding="utf-8") as file:
            json.dump(final_stats, file)

        self.stop_video()

    def start_video(self, video_name, width, height, fps=30):
        """
        Do NOT edit this method.
        """
        self.video = cv2.VideoWriter(
            video_name, cv2.VideoWriter_fourcc(*"mp4v"), fps, (width, height)
        )

    def stop_video(self) -> None:
        """
        Do NOT edit this method.
        """
        self.video.release()
