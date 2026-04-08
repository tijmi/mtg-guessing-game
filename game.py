from PIL import Image, ImageFilter

import pygame

COLOR_INACTIVE = pygame.Color('lightskyblue3')
COLOR_ACTIVE = pygame.Color('dodgerblue2')
FONT = pygame.font.SysFont("Segoe UI", 20)

class Game:
    def __init__(self, width, height):
        pygame.init()
        self.width = width
        self.height = height
        window = (width, height)
        self.screen = pygame.display.set_mode(window)
        self.screen = pygame.display.set_mode((width, height))
        self.fpsfont = pygame.font.SysFont("Segoe UI", 20) # reminder to try Lemon font later
        self.scorefont = pygame.font.SysFont("Segoe UI", 80)
        self.easy_button = self.Button(400, 720, 250, 100, "Easy")
        self.medium_button = self.Button(800, 720, 250, 100, "Medium")
        self.hard_button = self.Button(1200, 720, 250, 100, "Hard")
        self.text_input = self.InputBox(700, 790, 140, 32)
        self.state = 2

        #reminder to self to implement:
        # display image, display time elapsed
    
    def new_round(self, card_img, card_name, difficulty):
        self.start_time = pygame.time.get_ticks()/1000
        self.card_img = pygame.image.load(card_img) # pass a filepath to unprocessed image
        self.card_img_temp = pygame.transform.scale_by(self.card_img, (self.height/(self.card_img.get_height()*2)))
        self.card_name = card_name
        self.diff = difficulty

    def load_card(self, card_img):
        pass
    
    def update(self):
        self.screen.fill((0, 0, 0))
        data = pygame.image.tostring(self.card_img_temp, "RGBA")
        pil_image = Image.frombytes("RGBA", self.card_img_temp.get_size(), data)
        pil_image = pil_image.filter(ImageFilter.GaussianBlur(radius=max(20 - self.time, 0)))
        self.card_img = pygame.image.fromstring(pil_image.tobytes(), pil_image.size, pil_image.mode)
        self.text_input.update()
        self.text_input.draw(self.screen)
        background = pygame.Surface((self.width, self.height))
        background.blit(self.card_img, (self.width/2 - self.card_img.get_width()/2, self.height/2 - self.card_img.get_height()/2))
        self.screen.blit(background,(0,0))

    def update_menu(self):
        self.screen.fill((0, 0, 0))
        background = pygame.Surface((self.width, self.height))
        #background.blit(self.card_img, (50, 100))
        self.screen.blit(background,(0,0))
        self.easy_button.draw(self.screen)
        self.medium_button.draw(self.screen)
        self.hard_button.draw(self.screen)


    def button_checker(self):
        print("Checking buttons...")
        mouse_pos = pygame.mouse.get_pos()
        if self.easy_button.rect_position.collidepoint(mouse_pos):
            self.new_round(r"C:\Users\cagla\Downloads\mtg-guessing-game\6ed-260-uktabi-orangutan.jpg", "so2", "easy")
            self.state = 1

        elif self.medium_button.rect_position.collidepoint(mouse_pos):
            self.new_round(r"C:\Users\cagla\Downloads\mtg-guessing-game\6ed-260-uktabi-orangutan.jpg", "so2", "medium")  
            self.state = 1
        elif self.hard_button.rect_position.collidepoint(mouse_pos):
            self.new_round(r"C:\Users\cagla\Downloads\mtg-guessing-game\6ed-260-uktabi-orangutan.jpg", "so2", "hard")
            self.state = 1
        

    
    def draw_time(self):
        text = self.fpsfont.render(str(round(self.time, 2)), True, pygame.Color("red"))
        self.screen.blit(text, (self.width/2 - 15, 200))

    class Button:
        def __init__(self, x, y, width, height, text):
            self.x = x
            self.y = y
            self.width = width
            self.height = height
            self.text = text
        
        def draw(self, screen):
            self.rect_position = pygame.draw.rect(screen, (255, 0, 0), (self.x, self.y, self.width, self.height))
            font = pygame.font.SysFont("Segoe UI", 20)
            text_surface = font.render(self.text, True, (255, 255, 255))
            text_rect = text_surface.get_rect(center=(self.x + self.width/2, self.y + self.height/2))
            screen.blit(text_surface, text_rect)
        
    # !!!!! The following code is a modified version of the stack overflow answer found here: https://stackoverflow.com/questions/46390231/how-to-create-an-input-box-in-pygame/46390328#46390328  !!!!!
    class InputBox:
        COLOR_INACTIVE = pygame.Color('lightskyblue3')
        COLOR_ACTIVE = pygame.Color('dodgerblue2')
        FONT = pygame.font.Font(None, 32)
        def __init__(self, x, y, w, h, text=''):
            self.rect = pygame.Rect(x, y, w, h)
            self.color = COLOR_INACTIVE
            self.text = text
            self.txt_surface = FONT.render(text, True, self.color)
            self.active = False

        def handle_event(self, event):
            if event.type == pygame.MOUSEBUTTONDOWN:
                # If the user clicked on the input_box rect.
                if self.rect.collidepoint(event.pos):
                    # Toggle the active variable.
                    self.active = not self.active
                else:
                    self.active = False
                # Change the current color of the input box.
                self.color = COLOR_ACTIVE if self.active else COLOR_INACTIVE
            if event.type == pygame.KEYDOWN:
                if self.active:
                    if event.key == pygame.K_RETURN:
                        print(self.text)
                        self.text = ''
                    elif event.key == pygame.K_BACKSPACE:
                        self.text = self.text[:-1]
                    else:
                        self.text += event.unicode
                    # Re-render the text.
                    self.txt_surface = FONT.render(self.text, True, self.color)

        def update(self):
            # Resize the box if the text is too long.
            width = max(200, self.txt_surface.get_width()+10)
            self.rect.w = width

        def draw(self, screen):
            # Blit the text.
            screen.blit(self.txt_surface, (self.rect.x+5, self.rect.y+5))
            # Blit the rect.
            pygame.draw.rect(screen, self.color, self.rect, 2)


            
        



        


