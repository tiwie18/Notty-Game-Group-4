from scripts.screen_base import *
import scripts.configs as configs
from scripts.ui_base import *
from scripts.labels import *
from scripts.player import Player
from scripts.card import Card
import pygame
from pygame.locals import *

class StartScreen(ScreenBase):
    def __init__(self):
        """Initialize the StartScreen with the background image and some objects."""
        super().__init__(background_filename = os.path.join(configs.PATH_SCREEN, "StartScreen.png"))  # Set the background to 'startscreen.png'

        # Track the time when the StartScreen was shown
        self.start_time = pygame.time.get_ticks()  # Get the current time in milliseconds
        self.transition_delay = 3000  # Delay of 3 seconds (3000 milliseconds)

    def update(self):
        """Check the time and transition after the delay."""
        current_time = pygame.time.get_ticks()

        # If 3 seconds have passed, transition to the home screen
        if current_time - self.start_time >= self.transition_delay:
            self.transition_to_home_screen()

    def transition_to_home_screen(self):
         # Update global current_screen to HomeScreen
        print("Transitioning to HomeScreen...")
        global_variables.current_screen = HomeScreen()  # Switch the screen to HomeScreen


class HomeScreen(ScreenBase):
    def __init__(self):
        """Initialize the HomeScreen with the background and clickable labels."""
        super().__init__(background_filename= os.path.join(configs.PATH_SCREEN, "HomeScreen.png"))  # Set background for the home screen

        # Define the font for labels
        font = pygame.font.Font(None, 40)
        # Create the clickable labels with positions (already defined classes)
        # self.play_label = PlayGameLabel("labels/play_game_label.png", "labels/clickable_play_game_label.png",(400, 200))
        self.play_label = ClickableLabel(os.path.join(configs.PATH_LABELS, "play_game_label.png"), os.path.join(configs.PATH_LABELS, "clickable_play_game_label.png"),
                                        (0, 200), 0.2)
        self.play_label.add_click_listener(lambda : change_screen(StartGameScreen()))
        # self.rules_label = RulesLabel("labels/rules_label.png", "labels/clickable_rules_label.png", (400, 275))
        self.rules_label = ClickableLabel(os.path.join(configs.PATH_LABELS, "rules_label.png"), os.path.join(configs.PATH_LABELS,"clickable_rules_label.png"), (400, 275))
        self.rules_label.add_click_listener(lambda : change_screen(RuleScreen()))
        self.exit_label = ExitGameLabel(os.path.join(configs.PATH_LABELS, "exit_label.png"), os.path.join(configs.PATH_LABELS, "clickable_exit_label.png"), (400, 350))

        # Add labels to the screen objects list
        self.objects.append(self.play_label)
        self.objects.append(self.rules_label)
        self.objects.append(self.exit_label)


class RuleScreen(ScreenBase):
    def __init__(self):
        """Initialize the RuleScreen with the background image rulescreen.png."""
        super().__init__(background_filename= os.path.join(configs.PATH_SCREEN, "rulescreen.png", ))


class StartGameScreen(ScreenBase):
    def __init__(self):
        """Initialize the StartGameScreen with the background image startgamescreen.png."""
        super().__init__(background_filename= os.path.join(configs.PATH_SCREEN, "StartGameScreen.png"))  # Set background for the start game screen

        # Add clickable labels for the player selection
        self.two_player_label = TwoPlayerLabel(os.path.join(configs.PATH_LABELS, "two_player.png"), os.path.join(configs.PATH_LABELS, "clickable_two_player.png"), (200, 375))
        self.three_player_label = ThreePlayerLabel(os.path.join(configs.PATH_LABELS, "three_player.png"), os.path.join(configs.PATH_LABELS, "clickable_three_player.png"),
                                                   (590, 375))

        # Add the labels to the screen objects
        self.objects.append(self.two_player_label)
        self.objects.append(self.three_player_label)


class PlayScreen(ScreenBase):
    def __init__(self, num_players):
        # Initialize the PlayScreen with a specific background
        super().__init__(background_filename= os.path.join(configs.PATH_SCREEN, 'PlayScreen.png'))

        # Create player objects and add them to the screen
        self.num_players = num_players
        self.players = []

        # Create players based on the number of players selected (2 or 3)
        if self.num_players == 2:
            # Player 1 (Top)
            player1 = Player('top',
                             [Card(x=100, y=150, color='red', number=5), Card(x=150, y=150, color='blue', number=8)])
            # Player 2 (Bottom)
            player2 = Player('bottom', [Card(x=100, y=450, color='green', number=3),
                                        Card(x=150, y=450, color='yellow', number=9)])

            self.players.append(player1)
            self.players.append(player2)

        elif self.num_players == 3:
            # Player 1 (Left)
            player1 = Player('left',
                             [Card(x=100, y=150, color='red', number=5), Card(x=100, y=200, color='blue', number=8)])
            # Player 2 (Bottom)
            player2 = Player('bottom', [Card(x=100, y=450, color='green', number=3),
                                        Card(x=150, y=450, color='yellow', number=9)])
            # Player 3 (Right)
            player3 = Player('right', [Card(x=600, y=150, color='green', number=7),
                                       Card(x=600, y=200, color='yellow', number=2)])

            self.players.append(player1)
            self.players.append(player2)
            self.players.append(player3)

        # Add players to the screen
        for player in self.players:
            self.objects.append(player)

        # Create the clickable labels for game actions

        self.deck_label = ClickableLabel( os.path.join(configs.PATH_LABELS, "deck_label.png"), os.path.join(configs.PATH_LABELS,"clickable_deck_label.png"), (configs.WINDOW_WIDTH/2,configs.WINDOW_HEIGHT/2), 0.1)
        self.game_pass_label = ClickableLabel(os.path.join(configs.PATH_LABELS, "game_pass_label.png"), os.path.join(configs.PATH_LABELS,"clickable_game_pass_label.png"),
                                             (50, 550),2)  # Position the label horizontally at the bottom
        self.draw_card_label = ClickableLabel(os.path.join(configs.PATH_LABELS,"draw_card_label.png"), os.path.join(configs.PATH_LABELS,"clickable_draw_card_label.png"),
                                             (200, 550),2)
        self.discard_label = ClickableLabel(os.path.join(configs.PATH_LABELS,"discard_label.png"), os.path.join(configs.PATH_LABELS,"clickable_discard_label.png"), (350, 550),2)
        self.play_for_me_label = ClickableLabel(os.path.join(configs.PATH_LABELS,"play_for_me_label.png"),
                                                os.path.join(configs.PATH_LABELS,"clickable_play_for_me_label.png"), (650, 550),2)

        # Add the clickable labels to the objects list
        self.objects.append(self.deck_label)
        self.objects.append(self.game_pass_label)
        self.objects.append(self.draw_card_label)
        self.objects.append(self.discard_label)
        self.objects.append(self.play_for_me_label)


class CongratsScreen(ScreenBase):
    def __init__(self):
        super().__init__(background_filename='screens/CongratsScreen.png')  # Use congratsscreen.png as background

        self.newgame_label = NewGameLabel("labels/new_game_label.png", "labels/clickable_new_game_label.png",
                                          (350, 250))
        self.exitgame_label = ExitGameLabel("labels/exit_label.png", "labels/clickable_exit_label.png", (350, 350))

        # Create the clickable labels with their image files and positions
        self.objects.append(self.newgame_label)
        self.objects.append(self.exitgame_label)

    def keydown(self, event):
        """Handle keydown events, such as ESC for quitting the game."""
        if event.key == K_ESCAPE:
            global_variables.game_over = True


class LoseScreen(ScreenBase):
    def __init__(self):
        super().__init__(background_filename='screens/LoseScreen.png')  # Use congratsscreen.png as background

        self.newgame_label = NewGameLabel("labels/new_game_label.png", "labels/clickable_new_game_label.png",
                                          (350, 250))
        self.exitgame_label = ExitGameLabel("labels/exit_label.png", "labels/clickable_exit_label.png", (350, 350))

        # Create the clickable labels with their image files and positions
        self.objects.append(self.newgame_label)
        self.objects.append(self.exitgame_label)

    def keydown(self, event):
        """Handle keydown events, such as ESC for quitting the game."""
        if event.key == K_ESCAPE:
            global_variables.game_over = True