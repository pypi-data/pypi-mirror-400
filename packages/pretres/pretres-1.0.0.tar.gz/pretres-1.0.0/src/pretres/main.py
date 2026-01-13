import random
import sys

import pygame
import time
from dataclasses import dataclass
from importlib import resources
from enum import Enum

class UiModes(Enum):
    TEXT = 0,
    GUI = 1

ui_mode = UiModes.GUI
try:
    import tkinter as tk
except:
    ui_mode = UiModes.TEXT


# source: https://sl.wikipedia.org/wiki/Boggle
DICES = [
    ['A','D','J','O','P','T'],
    ['A','C','I','R','U','Z'],
    ['E','F','N','O','V','Ž'],
    ['B','E','O','R','S','Ž'],
    ['A','E','L','M','S','Š'],
    ['A','E','K','L','O','V'],
    ['A','B','E','K','R','V'],
    ['A','B','H','J','N','U'],
    ['C','E','G','I','M','T'],
    ['Č','D','I','M','O','Z'],
    ['A','D','F','L','O','S'],
    ['A','C','E','N','P','U'],
    ['Č','E','I','N','P','T'],
    ['C','E','H','I','M','U'],
    ['A','B','E','G','L','S'],
    ['A','I','K','R','Š','V']]

# source: physical game
#.GECTIM .NEPITČ .EPACNU .EGLBAS
#.RCZIAU .EVBKAR .ČDMZOI .EBSOŽR
#.JUBNAH .EUMCIH .DJPAOT .ŽVENFO
#.AKRIŠV .EOLKAV .LAODSF .AŠELSM

PLAY_TIME_S = 90  # time players have to find as many words as they can.


@dataclass
class LetterInfo:
    letter: str
    rotation: int # 0, 1, 2, 3 corresponding to 0, 90, 180, 270 degrees


def generate_grid() -> list[list[LetterInfo]]:
    dice_locations = random.sample(range(16), 16)
    new_grid: list[list[LetterInfo]] = [[LetterInfo(letter='?', rotation=0) for _ in range(4)] for _ in range(4)]

    for i, dice_idx in enumerate(dice_locations):
        dice_letters = DICES[dice_idx]
        selected_letter = random.choice(dice_letters)
        rotation = random.randint(0, 3)
        row = i // 4
        col = i % 4
        new_grid[row][col] = LetterInfo(selected_letter, rotation)

    return new_grid


class PretresView(tk.Tk):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.title("Pretres")
        self.geometry("400x550")
        
        # Main container
        self.main_frame = tk.Frame(self, padx=20, pady=20)
        self.main_frame.pack(expand=True, fill=tk.BOTH)
        
        # Canvas for the grid
        self.canvas = tk.Canvas(self.main_frame, width=320, height=320, bg='white')
        self.canvas.pack(pady=10)
        
        # Timer label
        self.timer_label = tk.Label(self.main_frame, text="90", font=("Helvetica", 24))
        self.timer_label.pack(pady=20)
        
        # Action button
        self.action_button = tk.Button(self.main_frame, text="Pretresi", command=self.controller.start_new_game, font=("Helvetica", 16))
        self.action_button.pack(pady=10)

    def draw_grid(self, grid: list[list[LetterInfo]]):
        self.canvas.delete("all")
        cell_size = 80
        for r in range(4):
            for c in range(4):
                x = c * cell_size + cell_size / 2
                y = r * cell_size + cell_size / 2
                item = grid[r][c]
                angle = item.rotation * 90
                
                # Draw text with rotation
                # Note: valid angles for tk.Canvas.create_text are usually 0. To rotate text we needs to specific angle attribute if supported or rotate the canvas logic.
                # Standard Tkinter Canvas text doesn't support 'angle' until Tk 8.6.
                self.canvas.create_text(x, y, text=item.letter, font=("Helvetica", 32, "bold"), angle=angle)
                
                # Draw cell borders (optional)
                self.canvas.create_rectangle(c * cell_size, r * cell_size, (c+1) * cell_size, (r+1) * cell_size)

    def update_timer(self, seconds: int):
        self.timer_label.config(text=str(seconds))

class PretresController:
    def __init__(self):
        self.view = PretresView(self)
        self.timer_job: str | None = None
        self.time_left = 90
        
        self.start_new_game()

    def start_new_game(self):
        # Reset timer
        if self.timer_job:
            self.view.after_cancel(self.timer_job)
        self.time_left = PLAY_TIME_S
        self.view.update_timer(self.time_left)
        
        # Generate and show grid
        grid = generate_grid()
        self.view.draw_grid(grid)
        
        # Start countdown
        self.countdown()

    def countdown(self):
        if self.time_left > 0:
            self.time_left -= 1
            self.view.update_timer(self.time_left)
            self.timer_job = self.view.after(1000, self.countdown)
        else:
            self.timer_job = None
            self.play_sound()

    def play_sound(self):
        pygame.mixer.init()
        sound_file = resources.files("pretres.data").joinpath("drum.wav")
        pygame.mixer.music.load(sound_file)
        pygame.mixer.music.play()
        time.sleep(1)
        pygame.mixer.music.play()
        time.sleep(1)
        pygame.mixer.music.play()

        while pygame.mixer.music.get_busy():
            pass


    def run(self):
        self.view.mainloop()

def text_display(grid: list[list[LetterInfo]]):
    print()
    for line in grid:
        print('          ', end='')
        for letter in line:
            print(f' {letter.letter}', end='')  # there is no text rotation in terminal
        print()
    print()


def text_timer(timeout_s: int):
    for i in range(timeout_s):
        print(f'\r{timeout_s - i}', end='')
        time.sleep(1)

    print('\n\n========== K O N E C ===========\n\n\n')


def gui_main():
    app = PretresController()
    app.run()

def text_main():
    grid = generate_grid()
    text_display(grid)
    text_timer(PLAY_TIME_S)


def main():
    if len(sys.argv) == 2:
        if sys.argv[1] == '-t':
            text_main()
        else:
            print(f"Unknown parameter {sys.argv[1]}, use '-t- to start the game in text mode.")
            gui_main()
    elif ui_mode == UiModes.TEXT:
        text_main()
    else:
        gui_main()


if __name__ == '__main__':
    main()
