from PIL import Image, ImageFilter

import pygame
import math



class Game:
    def __init__(self, width, height):
        pygame.init()
        self.width = width
        self.height = height
        window = (width, height)
        self.screen = pygame.display.set_mode(window)
        self.screen = pygame.display.set_mode((width, height))
        self.fpsfont = pygame.font.SysFont("Arial", 20) # reminder to try Lemon font later
        self.scorefont = pygame.font.SysFont("Arial", 80)
        self.easy_button = self.Button(400, 720, 250, 100, "Easy")
        self.medium_button = self.Button(800, 720, 250, 100, "Medium")
        self.hard_button = self.Button(1200, 720, 250, 100, "Hard")
        self.text_input = self.InputBox(960, 200, 320, 44)
        self.state = 2

        #reminder to self to implement:
        # display image, display time elapsed
    
    def new_round(self, card_img, card_name, difficulty):
        self.start_time = pygame.time.get_ticks()/1000
        self.card_img = pygame.image.load(card_img) # pass a filepath to unprocessed image
        self.card_img_temp = pygame.transform.scale_by(self.card_img, (self.height/(self.card_img.get_height()*2)))
        self.card_name = card_name
        self.text_input.card_name = card_name
        self.text_input.active = True
        self.text_input.typed = False
        self.text_input.text = ""
        self.diff = difficulty

    def load_card(self, card_img):
        pass
    
    def update(self):
        self.screen.fill((0, 0, 0))
        data = pygame.image.tostring(self.card_img_temp, "RGBA")
        pil_image = Image.frombytes("RGBA", self.card_img_temp.get_size(), data)
        pil_image = pil_image.filter(ImageFilter.GaussianBlur(radius=max(20 - self.time, 0)))
        self.card_img = pygame.image.fromstring(pil_image.tobytes(), pil_image.size, pil_image.mode)
        background = pygame.Surface((self.width, self.height))
        self.text_input.update()
        self.text_input.draw(background)
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
        self.screen.blit(text, (self.width/2 - 15, 150))

    class Button:
        def __init__(self, x, y, width, height, text):
            self.x = x
            self.y = y
            self.width = width
            self.height = height
            self.text = text
        
        def draw(self, screen):
            self.rect_position = pygame.draw.rect(screen, (255, 0, 0), (self.x, self.y, self.width, self.height))
            font = pygame.font.SysFont("Arial", 20)
            text_surface = font.render(self.text, True, (255, 255, 255))
            text_rect = text_surface.get_rect(center=(self.x + self.width/2, self.y + self.height/2))
            screen.blit(text_surface, text_rect)
        
    # !!!!! The following code is a modified version of the stack overflow answer found here: https://stackoverflow.com/questions/46390231/how-to-create-an-input-box-in-pygame/46390328#46390328  !!!!!
    class InputBox:
        def __init__(self, x, y, w, h, text=''):
            self.typed = False
            self.default_x = x
            self.rect = pygame.Rect(x, y, w, h)
            self.color_inactive = pygame.Color('white')
            self.color_active = pygame.Color('dodgerblue2')
            self.font = pygame.font.SysFont("Arial", 28)
            self.text = text
            self.txt_surface = self.font.render(text, True, self.color_inactive)
            self.active = False
            self.flash_color = (255, 0, 0)
            self.flash_color_goal = self.color_active
            self.wrong_guess = 0

        def handle_event(self, event):
            if event.type == pygame.MOUSEBUTTONDOWN:
                # If the user clicked on the input_box rect.
                if self.rect.collidepoint(event.pos):
                    # Toggle the active variable.
                    self.active = not self.active
                else:
                    self.active = False
                # Change the current color of the input box.
            if event.type == pygame.KEYDOWN:
                if self.active:
                    if event.key == pygame.K_RETURN:
                        if self.text == self.card_name:
                            print("yuno ball")
                        else:
                            print("Hell na")
                            self.wrong_guess = 100
                        self.text = ''
                    elif event.key == pygame.K_BACKSPACE:
                        self.text = self.text[:-1]
                    else:
                        self.typed = True
                        self.text += event.unicode
                    # Re-render the text.
                    self.txt_surface = self.font.render(self.text, True, self.color_active if self.active else self.color_inactive)

        def update(self):
            # Resize the box if the text is too long.
            width = max(200, self.txt_surface.get_width()+10)
            self.rect.x = min(self.default_x, self.default_x - width/2)
            self.rect.w = width
            if not self.active:
                self.txt_surface = self.font.render("Click back to guess", True, pygame.Color('gray'))

        def lerp_color(self, color1, color2, t):
            return tuple(
            int(c1 + (c2 - c1) * t)
            for c1, c2 in zip(color1, color2))
        
        def draw(self, screen):
            if not self.typed and self.active:
                self.txt_surface = self.font.render("Type your guess now", True, self.color_active if self.active else self.color_inactive)

            if self.wrong_guess > 0:
                t = self.wrong_guess / 100.0
                self.flash_color = self.lerp_color((255,0,0), self.flash_color_goal, t)
                self.wrong_guess -= 2
                current_time = pygame.time.get_ticks()
                shake_x = self.get_shake_offset(self.wrong_guess, 100, current_time)

            # Blit the text.
            #screen.blit(self.txt_surface, (self.rect.x+self.rect.w/2, self.rect.y+5))
            rect = self.rect
            rect.x += shake_x if self.wrong_guess > 0 else 0
            screen.blit(self.txt_surface, (rect.x+5, rect.y+4))
            # Blit the rect.
            pygame.draw.rect(screen, self.flash_color if self.wrong_guess > 0 else (self.color_active if self.active else self.color_inactive), rect, 2)

        def get_shake_offset(self, wrong_value, max_wrong, time_ms, amplitude=20, frequency=20):
            # Intensity increases as wrong_value decreases toward 0
            intensity = (wrong_value**1.5 / max_wrong**1.5) if max_wrong > 0 else 0
            # Sinusoidal shake: left/right oscillation
            offset_x = amplitude * intensity * math.sin(time_ms * frequency * 0.001)
            return int(offset_x)

            
        



        


