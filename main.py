from game import Game
import pygame

class game:
    def __init__(self):
        print("Hello, World!")
        self.game = Game(1920, 1080)
    
    def start_round(self):
        game.new_round("some_filepath.jpg")

    def run(self):
        running = True
        while running:
            self.game.clear()
            self.game.time = pygame.time.get_ticks()/1000
            self.game.update()
            self.game.draw_time()



        

if __name__ == "__main__":
    while True:
        try:
            mode = int(input("1: play game\n 2:train ai \n 3:import new data \n").strip() or "1")
        except ValueError:
            print("Invalid input. Please enter a number.")
            continue
        if mode == 1:
            game_instance = game()
            game_instance.run()