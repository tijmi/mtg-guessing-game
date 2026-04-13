from game import Game
import pygame
import importdata
import trainai


class game:
    def __init__(self):
        print("Hello, World!")
        self.game = Game(1920, 1080)
    
    def start_round(self):
        self.game.new_round(r"C:\Users\cagla\Downloads\mtg-guessing-game\6ed-260-uktabi-orangutan.jpg", "so2", "easy")

    def run(self):
        running = True
        while running:
            if self.game.state == 2:
                for event in pygame.event.get():
                    if event.type == pygame.KEYUP and event.key == pygame.K_ESCAPE:
                        running = False
                        pygame.display.quit()
                    if event.type == pygame.MOUSEBUTTONUP:
                        self.game.button_checker()
                #self.game.time = pygame.time.get_ticks()/1000
                self.game.update_menu()
                #self.game.draw_time()
                pygame.display.flip()
            elif self.game.state == 1:
                for event in pygame.event.get():
                    if event.type == pygame.KEYUP and event.key == pygame.K_ESCAPE:
                        running = False
                        pygame.display.quit()
                    if event.type == pygame.KEYUP and event.key == pygame.K_m and (not self.game.text_input.active):
                        self.game.state = 2
                    self.game.text_input.handle_event(event)
                self.game.time = pygame.time.get_ticks()/1000 - self.game.start_time
                self.game.update()
                self.game.draw_time()
                pygame.display.flip()



        

if __name__ == "__main__":
    while True:
        try:
            print("1:play game\n2:train ai \n3:import new data \n4:stop program \n")
            mode = int(input("enter choice: ").strip() or "1")
        except ValueError:
            print("Invalid input. Please enter a number.")
            continue
        if mode == 1:
            game_instance = game()
            game_instance.start_round()
            game_instance.run()
        elif mode == 2:
            trainer_instance = trainai.trainer()
            trainer_instance.preparedata()
            trainer_instance.trainmodel()
        elif mode == 3:
            data_importer = importdata.dataimport()
            data_importer.newdata()
        elif mode == 4:
            print("Stopping program.")
            break
        else:
            print("Invalid mode. Please enter a number between 1 and 4.")