from modules.windows.start_up_window import Startup
from modules.windows.log_in_window import Login
from modules.windows.amadeus_window import Amadeus
import asyncio
import pygame

pygame.init()

background_color = (0, 0, 0)
window_size = (1055,598)
screen = pygame.display.set_mode(window_size)
fps = 60

#log in function
def login(
    screen:pygame.Surface, 
    window_size:tuple[int, int], 
    background_color:tuple[int, int, int], 
    fps:int
)-> None:

    window_title = 'Log in'
    log_in, user_id = Login(screen, window_size, window_title, background_color, fps).run()
    if log_in:
        startup(screen,window_size, background_color, fps, user_id)

#start up sequence from log in to amadeus
def startup(
    screen:pygame.Surface,
    window_size:tuple[int, int], 
    background_color:tuple[int, int, int], 
    fps:int, 
    user_id:str
)-> None:
    
    window_title = 'Start up'
    start_up = Startup(screen, window_size, window_title, background_color, fps).run()
    if start_up:
        amadeus(screen, window_size, user_id)

#amadeus function
def amadeus(
    screen:pygame.Surface, 
    window_size:tuple[int, int], 
    user_id:str
)-> None:

    window_title = 'Amadeus'
    amadeus = Amadeus(screen, window_size, window_title, user_id)
    asyncio.run(amadeus.run())


try:
    login(screen, window_size, background_color, fps)
except Exception as e:
    print(e)