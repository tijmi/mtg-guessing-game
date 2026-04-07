import pygame

class Game:
    def __init__(self, width, height):
        pygame.init()
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        self.fpsfont = pygame.font.SysFont("Segoe UI", 20) # reminder to try Lemon font later
        self.scorefont = pygame.font.SysFont("Segoe UI", 80)

        #reminder to self to implement:
        # display image, display time elapsed
    
    def new_round(self, card_img, card_name, difficulty):
        self.card_img = pygame.image.load(card_img) # pass a filepath to unprocessed image
        self.card_name = card_name
        self.diff = difficulty

    def load_card(self, card_img):
        pass
    
    def update(self):
        background = pygame.Surface((self.width, self.height))
        background.blit.card_img(background, (50, 100))
    
    def draw_time(self):
        text = self.fpsfont.render(str(self.time), True, pygame.Color("red"))
        self.screen.blit(text, (500, 500))


    


