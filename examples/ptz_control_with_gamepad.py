# -*- coding: utf-8 -*-
# 
# Control the VISCA PTZ camera using a standard (non-XBox) gamepad
# By Samarthya Lykamanuella (groaking)
# Licensed under GPL-3.0
# ---
# Gamepad event listener using Python
# -> SOURCE: https://github.com/zeth/inputs/blob/master/examples/gamepad_example.py
# Multithreading tips for gamepads
# -> SOURCE: https://gist.github.com/effedebe/6cae2a5849923fb373ab749594b9ed50

from inputs import get_gamepad
from pyvisca import visca
from threading import Thread
import numpy
import time

class GPad(Thread):
    ''' This class listens to the gamepad event without blocking the main code (using multithreading). '''
    
    def __init__(self):
        Thread.__init__(self)
        self.BTN_BASE5 = 0
        self.BTN_BASE6 = 0
        self.SQUARE = 0
        self.TRIANGLE = 0
        self.CIRCLE = 0
        self.CROSS = 0
        self.ABS_X = 128
        self.ABS_Y = 128
        self.ABS_Z = 128
        self.ABS_RZ = 128
    
    def run(self):
        while True:
            for event in get_gamepad():
                # Category of binary respond values
                if event.ev_type == "Key":
                    if event.code == "BTN_TOP":
                        self.SQUARE = event.state
                    elif event.code == "BTN_TRIGGER":
                        self.TRIANGLE = event.state
                    elif event.code == "BTN_THUMB":
                        self.CIRCLE = event.state
                    elif event.code == "BTN_THUMB2":
                        self.CROSS = event.state
                    elif event.code == "BTN_BASE5":
                        self.BTN_BASE5 = event.state
                    elif event.code == "BTN_BASE6":
                        self.BTN_BASE6 = event.state
                
                # Category of analog values
                elif event.ev_type == "Absolute":
                    if event.code == "ABS_X":
                        self.ABS_X = event.state
                    elif event.code == "ABS_Y":
                        self.ABS_Y = event.state
                    elif event.code == "ABS_Z":
                        self.ABS_Z = event.state
                    elif event.code == "ABS_RZ":
                        self.ABS_RZ = event.state

def get_speed(val, max_speed):
    '''
    Calculate the absolute speed according to the analog joystick's input voltage.
    If val == 128, then the joystick is at rest.
    The range of value (val) is within 0 and 255.
    The maximum speed (max_speed) determines
    '''
    i = numpy.abs( (val+1) - 128)
    return float( max_speed * float( i / 128 ) )

def main():
    ''' Actually controls the VISCA PTZ camera using joystick/gamepad. '''
    
    # Establish and initialize the VISCA object
    # (Change the port value according to your system's availability.)
    cam = visca.PTZ('/dev/ttyUSB0')
    
    # Set the max speed (pixel per 100 ms) of the X-Y joystick movement
    MAX_MOVEMENT_SPEED = 7
    
    # Set the delay time for movement speed
    MOVEMENT_REDUNDANT_DELAY = 0.01
    
    # Set the delay time after each movement, before stopping any continuous command
    MOVEMENT_STOP_DELAY = 0.05
    
    # Establish the non-blocking multithreading for analog input
    game_pad = GPad()
    game_pad.start()
    
    # Fail-safe error catching with infinite loop
    while True:
        
        # Recalling presets
        if game_pad.CROSS == 1:
            cam.preset_recall(0)
            game_pad.CROSS = 0  # --- blocking
        if game_pad.CIRCLE == 1:
            cam.preset_recall(1)
            game_pad.CIRCLE = 0  # --- blocking
        if game_pad.TRIANGLE == 1:
            cam.preset_recall(2)
            game_pad.TRIANGLE = 0  # --- blocking
        if game_pad.SQUARE == 1:
            cam.preset_recall(3)
            game_pad.SQUARE = 0  # --- blocking
        
        # Movement actions (left-right panning)
        if game_pad.ABS_X != 128:
            val = game_pad.ABS_X
            i = get_speed(val, MAX_MOVEMENT_SPEED)
            # Do the movement
            if val < 128:
                cam.left(round(i))
                time.sleep(MOVEMENT_STOP_DELAY)
                cam.stop()
            elif val > 128 and val <= 255:
                cam.right(round(i))
                time.sleep(MOVEMENT_STOP_DELAY)
                cam.stop()
        
        # Movement actions (up-down tilting)
        if game_pad.ABS_Y != 128:
            val = game_pad.ABS_Y
            i = get_speed(val, MAX_MOVEMENT_SPEED)
            # Do the movement
            if val < 128:
                cam.up(round(i))
                time.sleep(MOVEMENT_STOP_DELAY)
                cam.stop()
            elif val > 128 and val <= 255:
                cam.down(round(i))
                time.sleep(MOVEMENT_STOP_DELAY)
                cam.stop()
        
        # Movement actions (zoom)
        if game_pad.ABS_RZ != 128:
            val = game_pad.ABS_RZ
            i = get_speed(val, MAX_MOVEMENT_SPEED)
            # Do the movement
            if val < 128:
                cam.zoom_in(round(i))
                time.sleep(MOVEMENT_STOP_DELAY)
                cam.zoom_stop()
            elif val > 128 and val <= 255:
                cam.zoom_out(round(i))
                time.sleep(MOVEMENT_STOP_DELAY)
                cam.zoom_stop()
        
        # Movement actions (focus)
        if game_pad.ABS_Z != 128:
            val = game_pad.ABS_Z
            i = get_speed(val, MAX_MOVEMENT_SPEED)
            # Do the movement
            if val < 128:
                cam.focus_near(round(i))
                time.sleep(MOVEMENT_STOP_DELAY)
                cam.focus_stop()
            elif val > 128 and val <= 255:
                cam.focus_far(round(i))
                time.sleep(MOVEMENT_STOP_DELAY)
                cam.focus_stop()
        
        # Analog center button press actions
        # ---
        # Move camera to home/default position
        if game_pad.BTN_BASE5 == 1:
            cam.home()
            game_pad.BTN_BASE5 = 0  # --- blocking
        # Perform autofocus
        if game_pad.BTN_BASE6 == 1:
            cam.autofocus_sens_low()
            game_pad.BTN_BASE6 = 0  # --- blocking
        
        # Prevent too fast a movement
        time.sleep(MOVEMENT_REDUNDANT_DELAY)
    
    # Wait until the end of the game_pad thread
    game_pad.joint()
    
if __name__ == "__main__":
    main()
