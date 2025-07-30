import pygame
import pygame_gui

from modules.essentials.dialog_box_tkinter import *
from modules.essentials.pygame_obj_generator import *

from modules.data_handlers.cleaner import *
from modules.data_handlers.handle_data import *
from modules.data_handlers.fetch_sprites import *



class Login:
    def __init__(
            self, 
            screen:pygame.Surface, 
            window_size: tuple[int, int], 
            window_title: str, 
            background_color: tuple[int, int, int], 
            fps: int
        ) -> None:

        #necessary window information
        self.window_size = window_size
        self.window_title = window_title
        self.background_color = background_color
        self.fps = fps
        self.clock = pygame.time.Clock()
        self.time_delta = self.clock.tick(self.fps)/1000.0 

        #setting up screen
        self.screen = screen
        pygame.display.set_caption(self.window_title)

        #setting up GUI manager, GUI generator and pygame object generator
        self.gui_manager = pygame_gui.UIManager(window_size, 'resources/themes/log_in_theme.json')
        self.gui_generator = GenerateUI(self.gui_manager)

        #initialize dialogbox
        self.dialogbox = DialogBox()

        #fetching sprites
        self.background_sprites = FetchSprites('resources/sprites/log-in').begin()
        self.labels_sprites = FetchSprites('resources/sprites/labels').begin()

        #creating pygame obj for each sprites
        self.background_obj = pygame.image.load(self.background_sprites[1])
        self.logo_obj = pygame.image.load(self.background_sprites[0])
        self.password_label_obj = pygame.image.load(self.labels_sprites[1])
        self.username_label_obj = pygame.image.load(self.labels_sprites[2])

        #inializing scaling and position of pygame objects
        self.background = GenerateRect(scale=(1055,598), position=(528, 299),pygame_object=self.background_obj)
        self.logo = GenerateRect(scale=(300,206), position=(528, 225),pygame_object=self.logo_obj)
        self.username_label = GenerateRect(scale=(129, 22), position=(285, 365),pygame_object=self.username_label_obj)
        self.password_label = GenerateRect(scale=(129, 22), position=(285, 415),pygame_object=self.password_label_obj)

        #generating GUI elements/objects
        self.username_field = self.gui_generator.searchbar(position=(355, 350), dimension=(350, 40), id='#username_field')
        self.password_field = self.gui_generator.searchbar(position=(355, 400), dimension=(350, 40), id='#password_field')
        self.password_field.set_text_hidden(True)
        self.log_in_button = self.gui_generator.button(position=(705, 400), dimension=(45, 45), id='#log_in_btn', text='', tool_tip='enter')
        

        self.running = True


    def run(self) -> None:
        while self.running:
            #render other pygame objects
            self.screen.blit(self.background.scaled(), self.background.rect())
            self.screen.blit(self.logo.scaled(), self.logo.rect())
            self.screen.blit(self.password_label.scaled(), self.password_label.rect())
            self.screen.blit(self.username_label.scaled(), self.username_label.rect())

            #render GUI elements
            self.gui_manager.update(self.time_delta)
            self.gui_manager.draw_ui(self.screen)

            # Update the display
            pygame.display.flip()

            self.clock.tick(self.fps)


            #event handler
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    ans = self.dialogbox.show_popup("yesno","Quit The program?")
                    if ans == True:
                        self.running = False
                        return None, ''
                        pygame.quit()
                    else:
                        pass

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        result, user_id = self.check_user()
                        if result:
                            return True, user_id
                        else:
                            pass

                if event.type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == self.log_in_button:
                        result, user_id = self.check_user()
                        if result:
                            return True, user_id
                        else:
                            pass
                
                self.gui_manager.process_events(event)
                        

    def check_user(self) -> tuple[bool, str]:
        user_name = self.username_field.get_text()
        password = self.password_field.get_text()

        if user_name == '' or password == '':
            self.dialogbox.show_popup("error","Insufficient data, please enter password and username!")
            return False
        else:
            result, user_id = FetchData().check_user(user_name, password)
            if result:
                return True, user_id
                
            else:
                self.dialogbox.show_popup("error", f'No user with user_id of {user_name} and given password exists in database!')
                return False, user_id
