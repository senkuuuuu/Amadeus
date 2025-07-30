import pygame
import asyncio
import pygame_gui

from modules.functionality.record_audio import *
from modules.functionality.voice_to_text import *
from modules.functionality.text_to_voice import *
from modules.functionality.start_speaking import *

from modules.essentials.renderer import *
from modules.essentials.dialog_box_tkinter import *
from modules.essentials.character_ai_async import *
from modules.essentials.pygame_obj_generator import *
from modules.essentials.emotion_analysis_hugging_face import *

from modules.data_handlers.cleaner import *
from modules.data_handlers.handle_data import *



class Amadeus:
    def __init__(
            self, 
            screen:pygame.Surface,
            window_size:tuple[int, int], 
            window_title:str, 
            user_id:str
        ) -> None:

        #intial inputs
        self.ai_response = '...'
        self.user_input = '...'

        self.user_id = user_id
        self.chat_id = FetchData().check_chatroom(user_id=self.user_id)

        #creating task list
        self.tasks = []
        self.cleaner = clean()
        self.running = True    

        #basic pygame data
        self.screen = screen
        self.window_size = window_size
        self.window_title = window_title

        #background animation metadata
        self.background_y_init_pos = 0
        self.background_animation_speed = 10
        self.background_fps = 0.0001
        
        #setting up GUI manager
        self.gui_manager = pygame_gui.UIManager(window_size, 'resources/themes/amadeus_theme.json')
        self.gui_generator = GenerateUI(self.gui_manager)

        #generating gui elements
        #for recording 
        self.is_recording = False
        self.start_recording_button = self.gui_generator.button(position=(995, 10), dimension=(50, 50), id='#start_recording_button', text='', tool_tip='start recording')
        self.stop_recording_button = self.gui_generator.button(position=(995, 10), dimension=(50, 50), id='#stop_recording_button', text='', tool_tip='stop recording')
        self.stop_recording_button.hide()
        self.stop_recording_button.disable()

        #for amadeus terminal
        self.terminal_log = [] 
        self.starting_text = "<font color='#FFCD00' size=3.5><b>Amadeus/log></b></font> sucessfully loaded data<br>"
        self.terminal = self.gui_generator.text_box(position=(10,388), dimension=(1035, 200), id="#terminal", html_text=self.starting_text)
        self.hide_terminal = self.gui_generator.button(position=(10, 310), dimension=(290, 35), id='#hide_terminal_button', text='amadeus terminal _ ', tool_tip='hide the amadeus terminal')
        self.show_terminal = self.gui_generator.button(position=(10, 510), dimension=(290, 35), id='#show_terminal_button', text='amadeus terminal ^ ', tool_tip='show the amadeus terminal')
        self.show_terminal.hide()
        self.show_terminal.disable()

        #for reset conversation
        self.reset_button = self.gui_generator.button(position=(10, 10), dimension=(50, 50), id='#reset_conversation_button', text='', tool_tip='restarts conversation')

        self.user_text_input = self.gui_generator.searchbar(
            position=(10, 350),  # Adjust position as needed
            dimension=(900, 35), # Adjust dimension as needed
            id='#user_text_input',
        )
        self.send_text_button = self.gui_generator.button(
            position=(935, 350), # Position next to the text input
            dimension=(100, 35),
            id='#send_text_button',
            text='Send'
        )
        #initializing dialogbox
        self.dialog_box = DialogBox()
        self.emotion = "neutral"
        self.ai_response = '...'
        self.user_input = '...'
        self.text_input_received = False # New flag for text input
        self.audio_input_received = False
        #for text input

        


    ''' Event handlers '''
    async def pygame_event_loop(self, event_queue:asyncio.Queue) -> None:
        while self.running:
            await asyncio.sleep(0.01)  
            event = pygame.event.poll()
            if event.type != pygame.NOEVENT:
                await event_queue.put(event)
    
    async def handle_events(self, event_queue:asyncio.Queue) -> None:

        while self.running:
            if not event_queue.empty():
                event = await event_queue.get()
                
                # Handle text input events first
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        # Handle enter key press
                        if self.user_text_input.is_focused:
                            self._process_text_input()
                            continue
                    
                    # Let pygame_gui handle other key events
                    self.gui_manager.process_events(event)
                    continue
                    
                if event.type == pygame_gui.UI_TEXT_ENTRY_FINISHED:
                    if event.ui_element == self.user_text_input:
                        self._process_text_input()
                        continue

                # Existing event handling code...
                if event.type == pygame.QUIT:
                    result = self.dialog_box.show_popup('yesno', 'Do you wish to exit the program?')
                    if result:
                        self.running = False
                        self.cleaner.terminate_tasks(self.tasks)
                        self.cleaner.terminate_temp()
                        self.cleaner.terminate_lingering_obj(self.__class__)
                elif event.type == pygame_gui.UI_BUTTON_PRESSED:
                    '''control recording functionality'''
                    if event.ui_element == self.start_recording_button:
                        self.is_recording = True
                        # No direct event.set() here; `run` will observe self.is_recording

                        #hide and disable start recording button
                        self.start_recording_button.hide()
                        self.start_recording_button.disable()

                        #show and enable sopt recording button
                        self.stop_recording_button.show()
                        self.stop_recording_button.enable()

                    if event.ui_element == self.stop_recording_button:
                        self.is_recording = False
                        # No direct event.clear() here; `run` will observe self.is_recording

                        #hide and disable sopt recording button
                        self.stop_recording_button.hide()
                        self.stop_recording_button.disable()

                    if event.ui_element == self.send_text_button:
                        self.user_input = self.user_text_input.get_text()
                        if self.user_input:
                            terminal_user_log = f"<font color='#00B3FF' size=3.5><b>Users/salieri></b></font> {self.user_input}<br>"
                            self.terminal_log.append(terminal_user_log)
                            self.user_text_input.set_text('') # Clear the input box
                            self.is_recording = False # Ensure recording is off if text input is used
                            self.text_input_received = True # New flag for text input

                            #hide and disable recording buttons
                            self.start_recording_button.hide()
                            self.start_recording_button.disable()
                            self.stop_recording_button.hide()
                            self.stop_recording_button.disable()
                        else:
                            self.dialog_box.show_popup("info", "Please type something before sending.")

                    '''control terminal visibility'''
                    if event.ui_element == self.hide_terminal:
                        self.show_terminal.show()
                        self.show_terminal.enable()
                        self.hide_terminal.hide()
                        self.hide_terminal.disable()
                        self.terminal.hide()

                        # Move text input and send button lower (e.g. y = window_height - 45)
                        self.user_text_input.set_relative_position((10, self.window_size[1] - 45))
                        self.send_text_button.set_relative_position((935, self.window_size[1] - 45))
                        

                    if event.ui_element == self.show_terminal:
                        self.hide_terminal.show()
                        self.hide_terminal.enable()
                        self.show_terminal.hide()
                        self.show_terminal.disable()
                        self.terminal.show()

                        # Reset position back to above the terminal (original y = 350)
                        self.user_text_input.set_relative_position((10, 350))
                        self.send_text_button.set_relative_position((935, 350))


                    '''control reset conversation'''
                    if event.ui_element == self.reset_button:
                        print(self.chat_id)
                        if self.chat_id:
                            result = self.dialog_box.show_popup('yesno', 'do you want to reset conversation?')
                            if result:
                                EditData().delete_chatroom(self.user_id)
                                self.chat_id = None
                                self.terminal.clear()
                                self.terminal.append_html_text("<font color='#FFCD00' size=3.5><b>Amadeus/log></b></font> conversation restarted<br>")
                            else:
                                pass
                        else:
                            self.dialog_box.show_popup("error", f'user {self.user_id} has no existing conversation in the database!')

                elif event.type == pygame_gui.UI_TEXT_ENTRY_FINISHED:
                    if event.ui_element == self.user_text_input:
                        self.user_input = self.user_text_input.get_text()
                        if self.user_input:
                            terminal_user_log = f"<font color='#00B3FF' size=3.5><b>Users/salieri></b></font> {self.user_input}<br>"
                            self.terminal_log.append(terminal_user_log)
                            self.user_text_input.set_text('') # Clear the input box
                            self.is_recording = False # Ensure recording is off if text input is used
                            self.text_input_received = True # New flag for text input

                            #hide and disable recording buttons
                            self.start_recording_button.hide()
                            self.start_recording_button.disable()
                            self.stop_recording_button.hide()
                            self.stop_recording_button.disable()
                        else:
                            self.dialog_box.show_popup("info", "Please type something before sending.")

                self.gui_manager.process_events(event)
            await asyncio.sleep(0.01)

    ''' Animation handlers '''
    async def idle_animation(
        self, 
        screen:pygame.Surface, 
        character:AmadeusWindowRenderer, 
        idle_fps:int, 
        start_idle:asyncio.Event
    ) -> None:
        
        character_state = 0
        self.last_character_update = 0
        self.last_background_update = 0
        last_frame_time = pygame.time.get_ticks() / 1000
    
        while self.running:
            await start_idle.wait()
            
            # Get current time in seconds
            current_time = pygame.time.get_ticks() / 1000
            time_delta = current_time - last_frame_time
            if time_delta > 0.05:  # Cap update rate
                time_delta = 0.05

            last_frame_time = current_time

            if current_time - self.last_background_update >= self.background_fps:
                self.background_y_init_pos += self.background_animation_speed
                if self.background_y_init_pos >= 1183:
                    self.background_y_init_pos = 0

                self.last_background_update = current_time
            
            if current_time - self.last_character_update >= idle_fps:
                character_state += 1
                self.last_character_update = current_time

            if not self.user_text_input.is_focused:
                while self.terminal_log:
                    msg = self.terminal_log.pop(0)
                    self.terminal.append_html_text(msg)

            character.background_animation(screen, self.background_y_init_pos-1183, True)
            character.background_animation(screen, self.background_y_init_pos, False)
            character.idle(screen, character_state)
            
            self.gui_manager.update(time_delta)
            self.gui_manager.draw_ui(screen)
            pygame.display.flip()
            await asyncio.sleep(0.01)
            
    async def thinking_animation(
        self, 
        screen:pygame.Surface, 
        character:AmadeusWindowRenderer, 
        start_thinking:asyncio.Event, 
        fps:int
    ) -> None:
        
        last_frame_time = pygame.time.get_ticks() / 1000
        while self.running:
            await start_thinking.wait()

            # Get current time in seconds
            current_time = pygame.time.get_ticks() / 1000
            time_delta = min(0.016, max(0.0001, current_time - last_frame_time)) 
            last_frame_time = current_time

            if current_time - self.last_background_update >= self.background_fps:
                self.background_y_init_pos += self.background_animation_speed
                if self.background_y_init_pos >= 1183:
                    self.background_y_init_pos = 0
                self.last_background_update = current_time

            if not self.user_text_input.is_focused:
                while self.terminal_log:
                    msg = self.terminal_log.pop(0)
                    self.terminal.append_html_text(msg)

            character.background_animation(screen, self.background_y_init_pos-1183, True)
            character.background_animation(screen, self.background_y_init_pos, False)
            character.thinking(screen)
            
            self.gui_manager.update(time_delta)
            self.gui_manager.draw_ui(screen)
            pygame.display.flip()
            await asyncio.sleep(0.01)

    async def talking_animation(
        self, 
        screen:pygame.Surface, 
        character:AmadeusWindowRenderer, 
        talking_fps: int, 
        start_talking:asyncio.Event
    ) -> None:
        
        character_state = 0
        last_frame_time = pygame.time.get_ticks() / 1000
    
        while self.running:
            await start_talking.wait()
            
            # Get current time in seconds
            current_time = pygame.time.get_ticks() / 1000
            time_delta = min(0.016, max(0.0001, current_time - last_frame_time)) 
            last_frame_time = current_time
            
            if current_time - self.last_background_update >= self.background_fps:
                self.background_y_init_pos += self.background_animation_speed
                if self.background_y_init_pos >= 1183:
                    self.background_y_init_pos = 0
                self.last_background_update = current_time
            
            if current_time - self.last_character_update >= 1/talking_fps:
                character_state += 1
                self.last_character_update = current_time
            
            if not self.user_text_input.is_focused:
                while self.terminal_log:
                    msg = self.terminal_log.pop(0)
                    self.terminal.append_html_text(msg)

            character.background_animation(screen, self.background_y_init_pos-1183, True)
            character.background_animation(screen, self.background_y_init_pos, False)
            character.talking(screen, character_state)

            self.gui_manager.update(time_delta)
            self.gui_manager.draw_ui(screen)
            pygame.display.flip()
            await asyncio.sleep(0.01)


    ''' functionality handlers '''
    async def record_voice(
        self, 
        start_recording:asyncio.Event, 
        start_voice_to_text:asyncio.Event, 
        start_idle:asyncio.Event, 
        start_thinking:asyncio.Event
    ) -> None:
        
        while self.running:
            await start_recording.wait()

            #stop flag
            stop_event = asyncio.Event()
            
            try:
                # recording in a thread
                record_task = asyncio.create_task(
                    asyncio.to_thread(StartRecording(self.is_recording, stop_event).begin)
                )
                
                while self.is_recording:
                    await asyncio.sleep(0.1)
                
                stop_event.set()
                await record_task
               
                #handle functionality flags
                start_recording.clear()
                start_voice_to_text.set()

                #handle animation flags
                start_idle.clear()
                start_thinking.set()
                
            except Exception as e:
                #display debig
                print(f'[ERROR] {e}')
                #stop recording
                start_recording.clear()

                #show and enable start recording button
                self.start_recording_button.show()
                self.start_recording_button.enable()
                self.dialog_box.show_popup(type="error", error_message="something went wrong with recording\n- check you microphone")
          
    async def voice_to_text(
        self, 
        start_voice_to_text:asyncio.Event, 
        start_generating_ai_response:asyncio.Event
    ) -> None:

        while self.running:
            await start_voice_to_text.wait()
            self.user_input = await asyncio.to_thread(VoiceToText().begin)

            terminal_user_log = f"<font color='#00B3FF' size=3.5><b>Users/salieri></b></font> {self.user_input}<br>"
            self.terminal_log.append(terminal_user_log)
            
            #handle functionality flags
            start_voice_to_text.clear()
            start_generating_ai_response.set()

    async def run_character_ai(
        self, 
        character: AmadeusWindowRenderer, 
        start_generating_ai_response: asyncio.Event, 
        start_ai_speaking: asyncio.Event, 
        start_idle: asyncio.Event, 
        start_thinking: asyncio.Event
    ) -> None:
        while self.running:
            await start_generating_ai_response.wait()
            start_generating_ai_response.clear()
            
            try:
                # Initialize text-to-voice handler
                ttv = None
                
                if self.chat_id is None:
                    # Create new chatroom and get greeting
                    result = await AI().create_chatroom(self.user_id)
                    if result:
                        self.chat_id, greeting_data = result
                        ttv = TextToVoice(greeting_data)
                        self.ai_response = ttv.get_text()
                        
                        # Save greeting audio if available
                        if not ttv.save_audio():
                            print("Warning: No greeting audio available")
                else:
                    # Get normal response
                    response = await AI().generate_response(self.user_input, self.chat_id)
                    ttv = TextToVoice(response)
                    self.ai_response = ttv.get_text()
                    
                    # Save response audio if available
                    if not ttv.save_audio():
                        print("Warning: No response audio available")

                # Process emotion and update terminal
                self.emotion = await asyncio.to_thread(
                    lambda: EmotionAnalysis().analyze_emotion(self.ai_response)
                )
                character.character_talking_sprites = FetchSprites(
                    f'resources/sprites/talking_all/talking_{self.emotion}'
                ).begin()
                character.character_idle_sprites = FetchSprites(
                    f'resources/sprites/idle_all/idle_{self.emotion}'
                ).begin()

                terminal_Ai_log = (
                    f"<font color='#FFCD00' size=3.5><b>Amadeus/log></b></font> "
                    f"{self.ai_response}<br>"
                )
                self.terminal_log.append(terminal_Ai_log)
                
                # Only proceed to speaking if we have audio
                if ttv and ttv.get_audio_path():
                    start_ai_speaking.set()
                else:
                    # No audio available, return to idle
                    start_thinking.clear()
                    start_idle.set()
                    self.start_recording_button.show()
                    self.start_recording_button.enable()

            except Exception as e:
                print(f"Error in AI interaction: {e}")
                self.dialog_box.show_popup(
                    'error', 
                    'Had an error communicating with Makise Kurisu, try the following\n'
                    '- Check your internet connection\n'
                    '  click restart conversation\n'
                    'El Psy Congroo...'
                )
                start_thinking.clear()
                start_idle.set()
                self.start_recording_button.show()
                self.start_recording_button.enable()
        
    
    async def start_ai_speak(
        self, 
        character: AmadeusWindowRenderer,
        start_ai_speaking: asyncio.Event, 
        start_idle: asyncio.Event, 
        start_talking: asyncio.Event, 
        start_thinking: asyncio.Event
    ) -> None:
        while self.running:
            try:
                await start_ai_speaking.wait()
                
                # Get the audio file path
                audio_path = Path('temp') / 'output.mp3'
                
                if audio_path.exists():
                    try:
                        await asyncio.to_thread(
                            StartSpeaking(
                                start_talking, 
                                start_idle, 
                                start_thinking, 
                                asyncio.get_event_loop()
                            ).begin
                        )
                    except Exception as e:
                        print(f"Error playing audio: {e}")
                else:
                    print("No audio file found to play")
                
                # Reset character to neutral
                character.character_talking_sprites = FetchSprites(
                    'resources/sprites/talking_all/talking_neutral'
                ).begin()
                character.character_idle_sprites = FetchSprites(
                    'resources/sprites/idle_all/idle_neutral'
                ).begin()
                
                # Clean up
                start_ai_speaking.clear()
                self.start_recording_button.show()
                self.start_recording_button.enable()

            except Exception as e:
                print(f"Error in AI speech playback: {e}")
                start_ai_speaking.clear()
                start_idle.set()
                self.start_recording_button.show()
                self.start_recording_button.enable()
    async def run(self) -> None:
        #setting up pygame window
        screen = self.screen
        pygame.display.set_caption(self.window_title)

        #initializing essentials
        character = AmadeusWindowRenderer()
        idle_fps = 30
        talking_fps = 5

        #event queue for pygame events
        event_queue = asyncio.Queue()

        #event flags for animation (still useful for controlling animation loops)
        start_idle = asyncio.Event()
        start_idle.set() # Start in idle animation
        start_thinking = asyncio.Event()
        start_talking = asyncio.Event()

        # Main loop tasks that run continuously
        self.tasks = [
            # Event handler
            asyncio.create_task(self.pygame_event_loop(event_queue)),
            asyncio.create_task(self.handle_events(event_queue)), # No flags passed here

            # Animation handlers
            asyncio.create_task(self.idle_animation(screen, character, idle_fps, start_idle)),
            asyncio.create_task(self.thinking_animation(screen, character, start_thinking, idle_fps)),
            asyncio.create_task(self.talking_animation(screen, character, talking_fps, start_talking)),
        ]

        # Add the main game loop control within run()
        while self.running:
            # Check for audio input
            if self.is_recording:
                # Stop idle animation, start thinking (as recording might involve processing)
                start_idle.clear()
                start_thinking.set()
                try:
                    # Recording logic
                    await self._record_voice_flow() # Call a helper method for the voice flow
                    self.audio_input_received = True
                    self.is_recording = False # Reset recording flag after completion
                except Exception as e:
                    print(f'[ERROR] Recording failed: {e}')
                    self.dialog_box.show_popup(type="error", error_message="Something went wrong with recording\n- check your microphone")
                    self.start_recording_button.show()
                    self.start_recording_button.enable()
                    start_thinking.clear()
                    start_idle.set() # Back to idle on error

            # Check if either text input or audio input is ready for AI processing
            if self.text_input_received or self.audio_input_received:
                # Ensure correct animation state
                start_idle.clear()
                start_thinking.set()

                # Process user input
                if self.audio_input_received:
                    # Convert voice to text
                    self.user_input = await asyncio.to_thread(VoiceToText().begin)
                    terminal_user_log = f"<font color='#00B3FF' size=3.5><b>Users/salieri></b></font> {self.user_input}<br>"
                    self.terminal_log.append(terminal_user_log)
                    self.audio_input_received = False # Reset flag

                # Now, self.user_input is set (either from audio or text)
                if self.user_input: # Proceed only if there's actual input
                    try:
                        # Generate AI response (both text and audio)
                        if self.chat_id is None:
                            self.chat_id = await AI().create_chatroom(self.user_id)
                        
                        # Get both text and audio response
                        response = await AI().generate_response(self.user_input, self.chat_id)
                        self.ai_response = response['text']

                        # Save audio if available
                        if response['audio']:
                            text_to_voice = TextToVoice(response)
                            text_to_voice.save_audio()

                        # Identify emotion and set appropriate sprites
                        self.emotion = await asyncio.to_thread(lambda: EmotionAnalysis().analyze_emotion(self.ai_response))
                        character.character_talking_sprites = FetchSprites(f'resources/sprites/talking_all/talking_{self.emotion}').begin()
                        character.character_idle_sprites = FetchSprites(f'resources/sprites/idle_all/idle_{self.emotion}').begin()

                        # Append AI response to terminal
                        terminal_Ai_log = f"<font color='#FFCD00' size=3.5><b>Amadeus/log></b></font> {self.ai_response}<br>"
                        self.terminal_log.append(terminal_Ai_log)

                        # AI speaks
                        start_thinking.clear() # Stop thinking animation
                        start_talking.set() # Start talking animation
                        # StartSpeaking assumes it will clear start_talking and set start_idle internally
                        await asyncio.to_thread(StartSpeaking(start_talking, start_idle, start_thinking, asyncio.get_event_loop()).begin)

                        # Reset emotion to neutral after speaking
                        character.character_talking_sprites = FetchSprites(f'resources/sprites/talking_all/talking_neutral').begin()
                        character.character_idle_sprites = FetchSprites(f'resources/sprites/idle_all/idle_neutral').begin()

                    except Exception as e:
                        print(f"Error during AI interaction: {e}")
                        self.dialog_box.show_popup('error', 'Had an error communicating with Makise Kurisu, try the following\n-check your internet connection\n-click restart conversation\nEl Psy Congroo...')
                    finally:
                        # Always return to idle and enable input after processing
                        start_thinking.clear()
                        start_idle.set()
                        self.start_recording_button.show()
                        self.start_recording_button.enable()
                        self.text_input_received = False # Reset text input flag
                else:
                    # If user input was empty after processing (e.g., voice-to-text failed)
                    start_thinking.clear()
                    start_idle.set()
                    self.start_recording_button.show()
                    self.start_recording_button.enable()
                    self.text_input_received = False # Reset text input flag

            # Allow other tasks to run
            await asyncio.sleep(0.01) # Small sleep to yield control

        try:
            # We still await the continuous background tasks here
            await asyncio.gather(*self.tasks)
        except asyncio.CancelledError:
            pass
        finally:
            pygame.quit()
    # Helper method for the recording flow
    async def _record_voice_flow(self):
        stop_event = asyncio.Event()
        record_task = asyncio.create_task(
            asyncio.to_thread(StartRecording(self.is_recording, stop_event).begin)
        )
        while self.is_recording: # This will be set to False by stop_recording_button
            await asyncio.sleep(0.1)
        stop_event.set()
        await record_task
        # At this point, recording is done, and audio_input_received will be set by run()
    
    ''' clean up '''
    def __del__(self):
        print(f"Destroyed instance: {self.__class__}")

    def _process_text_input(self):
        """Helper method to process text input efficiently"""
        self.user_input = self.user_text_input.get_text()
        if self.user_input:
            terminal_user_log = f"<font color='#00B3FF' size=3.5><b>Users/salieri></b></font> {self.user_input}<br>"
            self.terminal_log.append(terminal_user_log)
            self.user_text_input.set_text('')
            self.is_recording = False
            self.text_input_received = True
            
            # Hide and disable recording buttons
            self.start_recording_button.hide()
            self.start_recording_button.disable()
            self.stop_recording_button.hide()
            self.stop_recording_button.disable()
        else:
            self.dialog_box.show_popup("info", "Please type something before sending.")