from PIL import Image, ImageFilter

import pygame
import math
import json
import random
import string
import numpy as np
from keras.models import load_model
import cv2



class Game:
    def __init__(self, width, height):
        self.COLOR_INACTIVE = pygame.Color('lightskyblue3')
        self.COLOR_ACTIVE = pygame.Color('dodgerblue2')
        with open("data_labels.json", 'r') as f:
            self.data_labels = json.load(f)
        self.translator = str.maketrans('', '', string.punctuation)

        pygame.init()
        self.width = width
        self.height = height
        window = (width, height)
        self.screen = pygame.display.set_mode(window)
        self.screen = pygame.display.set_mode((width, height))
        self.FONT = pygame.font.SysFont("Segoe UI", 20)
        self.fpsfont = pygame.font.SysFont("Arial", 20) # reminder to try Lemon font later
        self.scorefont = pygame.font.SysFont("Arial", 80)
        
        # Load the AI model
        self.model = load_model("mtgmodel.keras")
        self.last_prediction_time = 0
        self.prediction_interval = 1.0  # Predict every 1 second
        self.ai_prediction = None
        self.ai_confidence = 0
        
        self.easy_button = self.Button(400, 720, 250, 100, "Easy", self.FONT)
        self.medium_button = self.Button(800, 720, 250, 100, "Medium", self.FONT)
        self.hard_button = self.Button(1200, 720, 250, 100, "Hard", self.FONT)
        self.text_input = self.InputBox(700, 890, 140, 32, color_inactive=self.COLOR_INACTIVE, color_active=self.COLOR_ACTIVE, font=self.FONT)
        self.state = 2
        self.round_final_time = "0"

        #reminder to self to implement:
        # display image, display time elapsed
    
    def new_round(self, difficulty):
        self.card = random.choice(list(self.data_labels.keys()))
        self.card = self.data_labels[self.card]
        self.start_time = pygame.time.get_ticks()/1000
        self.card_img = pygame.image.load(self.card["scryfall_image"][0]) # pass a filepath to unprocessed image
        self.last_prediction_time = 0
        self.ai_prediction = None
        self.card_img_temp = pygame.transform.scale_by(self.card_img, (self.height/(self.card_img.get_height()*2)))
        self.card_name = self.card["cardname"].lower() # pass the card name as a string
        self.card_name = self.card_name.translate(self.translator)
        self.text_input.card_name = self.card_name
        self.text_input.active = True
        self.text_input.typed = False
        self.text_input.round_over = False
        self.text_input.flash_color_goal = pygame.Color('dodgerblue2')
        self.text_input.color_active = pygame.Color('dodgerblue2')
        self.text_input.text = ""
        self.diff = difficulty

    def load_card(self, card_img):
        pass
    
    def predict_card(self):
        """Predict the card from the blurred image currently on screen"""
        if self.card_img is None:
            return
        
        try:
            # Convert the blurred pygame surface (already on screen) to numpy array
            frame = pygame.image.tostring(self.card_img, "RGBA")
            frame = np.frombuffer(frame, dtype=np.uint8).reshape(
                self.card_img.get_height(),
                self.card_img.get_width(),
                4
            )
            
            # Convert RGBA to RGB for the model (model was trained on RGB)
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_RGBA2RGB)
            
            # Resize to 96x96 for the model (matching training preprocessing)
            frame_resized = cv2.resize(frame_rgb, (96, 96))
            # Keep as [0, 255] - preprocess_input layer will handle normalization
            frame_batch = np.expand_dims(frame_resized.astype(np.float32), axis=0)
            
            # Get prediction
            predictions = self.model.predict(frame_batch, verbose=0)
            predicted_idx = np.argmax(predictions[0])
            confidence = float(predictions[0][predicted_idx])
            
            # Get the card names in the SAME order as training (not sorted!)
            card_names = list(self.data_labels.keys())
            if predicted_idx < len(card_names):
                predicted_name = self.data_labels[card_names[predicted_idx]]["cardname"].lower()
                predicted_name = predicted_name.translate(self.translator)
                self.ai_prediction = predicted_name
                print(f"Prediction: {predicted_name} (confidence: {confidence:.4f}), Index: {predicted_idx}/{len(card_names)}")
                self.ai_confidence = confidence
        except Exception as e:
            print(f"Prediction error: {e}")
    
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
        
        # Update AI predictions every X seconds
        current_time = pygame.time.get_ticks() / 1000 - self.start_time
        if current_time - self.last_prediction_time > self.prediction_interval:
            self.predict_card()
            self.last_prediction_time = current_time
        
        # Draw AI prediction in top-left corner
        if self.ai_prediction:
            pred_text = f"AI: {self.ai_prediction} ({self.ai_confidence:.2f})"
            pred_surface = self.fpsfont.render(pred_text, True, pygame.Color("yellow"))
            background.blit(pred_surface, (200, 70))
        
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
            self.new_round("easy")
            self.state = 1

        elif self.medium_button.rect_position.collidepoint(mouse_pos):
            self.new_round("medium")  
            self.state = 1
        elif self.hard_button.rect_position.collidepoint(mouse_pos):
            self.new_round("hard")
            self.state = 1
        

    
    def draw_time(self):
        if not self.text_input.round_over:
            text = self.fpsfont.render(str(round(self.time, 2)), True, pygame.Color("red"))
            self.round_final_time = str(round(self.time, 2))
        else:
            text = self.fpsfont.render(self.round_final_time, True, pygame.Color("green"))
        self.screen.blit(text, (self.width/2 - 15, 150))

    class Button:
        def __init__(self, x, y, width, height, text, font=None):
            self.x = x
            self.y = y
            self.width = width
            self.height = height
            self.text = text
            self.font = font or pygame.font.SysFont("Segoe UI", 20) 
            self.translator = str.maketrans('', '', string.punctuation)
        
        def draw(self, screen):
            self.rect_position = pygame.draw.rect(screen, (255, 0, 0), (self.x, self.y, self.width, self.height))
            text_surface = self.font.render(self.text, True, (255, 255, 255))
            text_rect = text_surface.get_rect(center=(self.x + self.width/2, self.y + self.height/2))
            screen.blit(text_surface, text_rect)
        
    # !!!!! The following code is a modified version of the stack overflow answer found here: https://stackoverflow.com/questions/46390231/how-to-create-an-input-box-in-pygame/46390328#46390328  !!!!!
    class InputBox:
        def __init__(self, x, y, w, h, text='', color_inactive=None, color_active=None, font=None):
            self.COLOR_INACTIVE = color_inactive or pygame.Color('lightskyblue3')
            self.COLOR_ACTIVE = color_active or pygame.Color('dodgerblue2')
            self.FONT = font or pygame.font.SysFont("Segoe UI", 20)
            self.typed = False
            self.default_x = x
            self.rect = pygame.Rect(x, y, w, h)
            self.color = self.COLOR_INACTIVE
            self.text = text
            self.txt_surface = self.FONT.render(text, True, self.color)
            self.translator = str.maketrans('', '', string.punctuation)
            self.active = False
            self.flash_color = (255, 0, 0)
            self.flash_color_goal = self.COLOR_ACTIVE
            self.wrong_guess = 0
            self.truth_nuke = 0
            self.round_over = False

        def handle_event(self, event):
            if event.type == pygame.MOUSEBUTTONDOWN:
                # If the user clicked on the input_box rect.
                if self.rect.collidepoint(event.pos):
                    # Toggle the active variable.
                    self.active = not self.active
                else:
                    self.active = False
                # Change the current color of the input box.
                self.color = self.COLOR_ACTIVE if self.active else self.COLOR_INACTIVE
            if event.type == pygame.KEYDOWN:
                if self.active:
                    if event.key == pygame.K_RETURN:

                        if self.text.lower().translate(self.translator) == self.card_name:
                            print("yuno ball")
                            self.truth_nuke = 100
                            self.round_over = True
                            self.active = False
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
                    self.txt_surface = self.FONT.render(self.text, True, self.color)

        def update(self):
            # Resize the box if the text is too long.
            width = max(200, self.txt_surface.get_width()+10)
            self.rect.x = min(self.default_x, self.default_x - width/2)
            self.rect.w = width
            if not self.active and not self.round_over:
                self.txt_surface = self.FONT.render("Click back to guess", True, pygame.Color('gray'))

        def lerp_color(self, color1, color2, t):
            return tuple(
            int(c1 + (c2 - c1) * t)
            for c1, c2 in zip(color1, color2))
        
        def draw(self, screen):
            if not self.typed and self.active:
                self.txt_surface = self.FONT.render("Type your guess now", True, self.COLOR_ACTIVE if self.active else self.COLOR_INACTIVE)

            if self.truth_nuke > 0:
                t = self.truth_nuke / 100.0
                self.flash_color_goal = (0,255,80)
                self.color_active = (0,255,80)
                self.flash_color = self.lerp_color(self.flash_color_goal ,(0,255,155), t)
                self.truth_nuke -= 1
                current_time = pygame.time.get_ticks()
                #shake_x = self.get_shake_offset(self.truth_nuke, 100, current_time)
            elif self.wrong_guess > 0:
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
            pygame.draw.rect(screen, self.flash_color if self.wrong_guess > 0 or self.truth_nuke > 0 else (self.COLOR_ACTIVE if self.active else self.COLOR_INACTIVE), rect, 2)

        def get_shake_offset(self, wrong_value, max_wrong, time_ms, amplitude=20, frequency=40):
            # Intensity increases as wrong_value decreases toward 0
            intensity = (wrong_value**1.5 / max_wrong**1.5) if max_wrong > 0 else 0
            # Sinusoidal shake: left/right oscillation
            offset_x = amplitude * intensity * math.sin(time_ms * frequency * 0.001)
            return int(offset_x)

            
        



        


