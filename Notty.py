from pickle import GLOBAL

import pygame
from pygame.locals import *
import random
from enum import Enum
import os
import scripts.configs as configs
from scripts.ui_base import *
from scripts.screen_base import *
import scripts.math_util as math_util

game_over = False
current_screen = None

def change_screen(screen_instance):
    global current_screen
    current_screen = screen_instance

def load_and_scale_image(image_path, scale_factor=0.2):
    """Memuat gambar dan mengubah ukurannya berdasarkan scale_factor."""
    img = pygame.image.load(image_path)
    new_width = int(img.get_width() * scale_factor)
    new_height = int(img.get_height() * scale_factor)
    return pygame.transform.scale(img, (new_width, new_height))

class PlayGameLabel(ClickableLabel):
    def click(self):
        global current_screen
        current_screen = StartGameScreen()


class RulesLabel(ClickableLabel):
    def click(self):
        global current_screen
        current_screen = RuleScreen()


class SettingLabel(ClickableLabel):
    def click(self):
        global current_screen
        current_screen = SettingScreen()


class QuitGameLabel(ClickableLabel):
    def click(self):
        global current_screen
        current_screen = HomeScreen()


class TwoPlayerLabel(ClickableLabel):
    def click(self):
        global current_screen
        current_screen = PlayScreen(2)


class ThreePlayerLabel(ClickableLabel):
    def click(self):
        global current_screen
        current_screen = PlayScreen(3)


class DrawCardLabel(ClickableLabel):
    def __init__(self, game):
        self.game = game  # Reference to the PlayGame instance

    def display_action_options(self):
        # Display action options for the player
        choice = input("Choose action:\n1. Take a card from the opponent\n2. Draw cards from the deck\n")

        if choice == '1':
            self.game.take_card_from_opponent()  # Execute the action from PlayGame(we need to make new def in PlayGame Class)
        elif choice == '2':
            self.game.draw_cards_from_deck()  # Execute the action from PlayGame(we need to make new def in PlayGame Class)
        else:
            print("Invalid choice. Please choose again.")

    def reset_turn(self):
        # to make sure that this choice only once per turn
        self.game.reset_turn()


class DiscardLabel(ClickableLabel):
    def __init__(self, game):
        self.game = game

    def click(self):
        self.game.discard_card()  # Execute the action from PlayGame(we need to make new def in PlayGame Class)


class PlayForMeLabel(ClickableLabel):
    def __init__(self, game):
        self.game = game

    def click(self):
        self.game.play_for_me()  # Execute the action from PlayGame(we need to make new def in PlayGame Class)


class GamePassLabel(ClickableLabel):
    def __init__(self, image_path_1, image_path_2, pos, scale_factor=0.2):
        super().__init__(image_path_1, image_path_2, pos, scale_factor=scale_factor)

    def click(self):
        pass


class DeckLabel(ClickableLabel):
    def click(self):
        global current_screen


class NewGameLabel(ClickableLabel):
    def click(self):
        global current_screen
        current_screen = HomeScreen()


class ExitGameLabel(ClickableLabel):
    def click(self):
        global game_over
        game_over = True


class Card(RenderableImage):
    def __init__(self, x, y, color, number, orientation='normal', scale_factor=0.2):
        super().__init__(Card.calc_image_src(color,number), (x,y), (scale_factor, scale_factor),Card.calc_orientation_rotation(orientation), 255)
        self.x = x
        self.y = y
        self.color = color
        self.number = number
        self.orientation = orientation  # 'normal', 'left', 'right', 'top'

    @staticmethod
    def calc_image_src(color, number):
        filename = f"{color}_{number}.png"
        filepath = os.path.join(configs.PATH_CARDS, filename)
        if os.path.exists(filepath):
            return filepath
        return os.path.join(configs.PATH_CARDS, "default.png")

    @staticmethod
    def calc_orientation_rotation(orientation):
        if orientation == 'left':
            return math_util.euler_angle_to_rotation(90)
        elif orientation == 'right':
            return math_util.euler_angle_to_rotation(-90)
        elif orientation == 'top':
            return math_util.euler_angle_to_rotation(180)
        else:
            return math_util.euler_angle_to_rotation(0)

    def load_image(self, color, number):
        """Load the appropriate image based on the card's color and number."""
        image_filename = Card.calc_image_src(color, number)
        self.image_src = image_filename

    def update(self):
        """Update the card's position or other properties if needed."""
        pass

    def draw(self, screen):
        """Draw the card image on the screen."""
        screen.blit(self.image, (self.x, self.y))


class Player(VisualObject):
    def __init__(self, position, cards):
        self.position = position  # Position: 'top', 'left', 'bottom', 'right'
        self.cards = cards  # List of cards

    def display_cards(self, screen, card_spacing=-25):  # Negative spacing for overlap
        """Display the player's cards with the correct orientation, based on the player count."""
        card_width = self.cards[0].image.get_width()  # Width of a single card
        card_height = self.cards[0].image.get_height()  # Height of a single card

        if self.position == 'bottom':
            # Player at the bottom: cards are displayed horizontally with overlap
            start_x = 50
            start_y = 450
            for i, card in enumerate(self.cards):
                card.x = start_x + i * (card_spacing + card_width)  # Adjust x for horizontal overlap
                card.y = start_y  # Keep y constant for all cards
                card.orientation = 'normal'  # No rotation needed for the bottom player
                card.draw(screen)

        elif self.position == 'left':
            # Player at the left: cards are stacked vertically with overlap
            start_x = 50
            start_y = 100
            for i, card in enumerate(self.cards):
                card.x = start_x  # x is fixed for left position
                card.y = start_y + i * (card_spacing + card_height)  # Adjust y for vertical overlap
                card.orientation = 'left'  # Rotate cards for the left player
                card.draw(screen)

        elif self.position == 'right':
            # Player at the right: cards are stacked vertically with overlap
            start_x = 550
            start_y = 100
            for i, card in enumerate(self.cards):
                card.x = start_x  # x is fixed for right position
                card.y = start_y + i * (card_spacing + card_height)  # Adjust y for vertical overlap
                card.orientation = 'right'  # Rotate cards for the right player
                card.draw(screen)

        elif self.position == 'top':
            # Player at the top: cards are displayed horizontally with overlap
            start_x = 50
            start_y = 50
            for i, card in enumerate(self.cards):
                card.x = start_x + i * (card_spacing + card_width)  # Adjust x for horizontal overlap
                card.y = start_y  # Keep y constant for all cards
                card.orientation = 'top'  # Rotate cards for the top player
                card.draw(screen)


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
        global current_screen  # Update global current_screen to HomeScreen
        print("Transitioning to HomeScreen...")
        current_screen = HomeScreen()  # Switch the screen to HomeScreen


class HomeScreen(ScreenBase):
    def __init__(self):
        """Initialize the HomeScreen with the background and clickable labels."""
        super().__init__(background_filename= os.path.join(configs.PATH_SCREEN, "HomeScreen.png"))  # Set background for the home screen

        # Define the font for labels
        font = pygame.font.Font(None, 40)
        # Create the clickable labels with positions (already defined classes)
        # self.play_label = PlayGameLabel("labels/play_game_label.png", "labels/clickable_play_game_label.png",(400, 200))
        self.play_label = ClickableLabel(os.path.join(configs.PATH_LABELS, "play_game_label.png"), os.path.join(configs.PATH_LABELS, "clickable_play_game_label.png"),
                                        (400, 200), 0.2)
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
            global game_over
            game_over = True


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
            global game_over
            game_over = True


from time import sleep

# Initialize pygame
pygame.init()

# Set the window dimensions
screen = pygame.display.set_mode((configs.WINDOW_WIDTH, configs.WINDOW_HEIGHT))
pygame.display.set_caption('Card Game Funt4stic Te4m')

# Start with the home screen
current_screen = StartScreen()


# Main game loop
def main():
    global current_screen
    game_over = False

    while not game_over:
        # Event handling
        for event in pygame.event.get():
            if event.type == QUIT:
                game_over = True
            if event.type == MOUSEBUTTONUP:
                current_screen.mouseup(event)
            if event.type == KEYDOWN:
                current_screen.keydown(event)

        # Update game state
        current_screen.update()

        # Draw everything
        current_screen.draw(screen)

        # Update the screen
        pygame.display.flip()

        # Delay to limit frame rate
        pygame.time.delay(30)

    pygame.quit()


if __name__ == "__main__":
    main()
