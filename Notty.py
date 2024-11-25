from pickle import GLOBAL

import pygame
from pygame.locals import *
import random
from enum import Enum
import os
import scripts.math_util as math_util

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600

game_over = False
current_screen = None

PATH_CARDS = r"resources/images/cards/"
PATH_LABELS = r"resources/images/ui/labels/"
PATH_UI = r"resources/images/ui/"
PATH_SCREEN = r"resources/images/ui/screen/"
PATH_START_SCREEN = r"resources/images/StartScreenObject"

def change_screen(screen_instance):
    global current_screen
    current_screen = screen_instance


def load_and_scale_image(image_path, scale_factor=0.2):
    """Memuat gambar dan mengubah ukurannya berdasarkan scale_factor."""
    img = pygame.image.load(image_path)
    new_width = int(img.get_width() * scale_factor)
    new_height = int(img.get_height() * scale_factor)
    return pygame.transform.scale(img, (new_width, new_height))


class VisualObject:
    def __init__(self, position2d=(0, 0), scale2d=(1, 1), rotation2d=(1, 0), alpha = 255):
        self.position2d = position2d
        self.scale2d = scale2d
        self.rotation2d = rotation2d
        self.alpha = alpha
        pass

    @property
    def euler_angle(self):
        return math_util.rotation_to_euler_angle(self.rotation2d)

    @euler_angle.setter
    def euler_angle(self, value):
        value = math_util.euler_angle_to_rotation(value)
        self.rotation2d = value

    def draw(self, screen):
        pass

    def update(self):
        pass

    def mouseup(self, event):
        pass


class RenderableImage(VisualObject):
    '''
    A class that provide basic rendering functionality for images along with transformation (position, scale, rotation)
    '''
    def __init__(self, image_src, position2d=(0, 0), scale2d=(1, 1), rotation2d=(1, 0), alpha = 255):
        super().__init__(position2d=position2d, scale2d=scale2d, rotation2d=rotation2d, alpha=alpha)
        if not os.path.exists(image_src):
            raise FileNotFoundError(image_src)
        self.image_src = image_src
        # self.image = pygame.image.load(image_src).convert_alpha()
        self._cached_src_image_dict = {}
        self._store_cache()

    @property
    def image(self):
        if self.image_src not in self._cached_src_image_dict.keys():
            self._update_cache_if_dirty()
        return self._cached_src_image_dict[self.image_src]

    def _transform_image(self):
        # basically follows the order of SQT scale->rotation->translation
        size2d = self._size2d()
        scale2d = self.scale2d
        original_size2d = self.image.get_size()
        # this is a simple super sampler anti-aliasing
        # rotation will severely corrupt the original image sample result, so do the pre scale before it is rotated
        preprocess_size2d = original_size2d
        if scale2d[0] > scale2d[1]:  # the original picture is not that long
            target_length = original_size2d[0] * scale2d[0] / scale2d[1]
            preprocess_size2d = (target_length, original_size2d[1])
        elif scale2d[0] < scale2d[1]:  # the original picture is not that high
            target_height = original_size2d[1] * scale2d[1] / scale2d[0]
            preprocess_size2d = (original_size2d[0], target_height)
        # point scale, also known as 1d scale
        scale_ratio = size2d[1] / preprocess_size2d[1]
        # in the following step we get the super sampled picture
        transformed_image = pygame.transform.scale(self.image, preprocess_size2d)
        angle = math_util.rotation_to_euler_angle(self.rotation2d)
        transformed_image = pygame.transform.rotate(transformed_image, angle)
        rect = transformed_image.get_rect()
        # finally scale the image to given size
        transformed_image = pygame.transform.smoothscale(transformed_image,
                                                   (rect.width * scale_ratio, rect.height * scale_ratio))
        # t (not needed to be processed here)
        transformed_image.set_alpha(self.alpha)
        return transformed_image

    # calculate the size using given scale. e.g. the original image is 100*100, scale (2,2) will make the size 200*200
    # scale is always (1,1) when using the original size
    def _size2d(self):
        x = self.image.get_size()[0] * self.scale2d[0]
        y = self.image.get_size()[1] * self.scale2d[1]
        return x, y

    # cache the transformed image so that it won't be resampled every frame
    def _store_cache(self):
        self._cached_image_src = self.image_src
        if self.image_src not in self._cached_src_image_dict.keys():
            self._cached_src_image_dict[self.image_src] = pygame.image.load(self.image_src).convert_alpha()
        self._cached_transformed_image = self._transform_image()
        self._cached_size2d = self._size2d()
        self._cached_rotation2d = self.rotation2d
        self._cached_alpha = self.alpha


    # when properties changed e.g. scale or the whole image src, it requires a resample, which means update the cache
    def _update_cache_if_dirty(self):
        if self.image_src != self._cached_image_src:
            # self.image = pygame.image.load(self.image_src)
            self._store_cache()
        elif self._cached_size2d != self._size2d() or self.rotation2d != self._cached_rotation2d or self.alpha != self._cached_alpha:
            self._store_cache()

    def draw(self, screen):
        self._update_cache_if_dirty()
        rect = self._cached_transformed_image.get_rect(center=self.position2d)
        screen.blit(self._cached_transformed_image, rect.topleft)

    def update(self):
        pass


class Label(RenderableImage):
    # if it's image instead of text:
    def __init__(self, image_path, pos, scale_factor=0.2):
        super().__init__(image_path, pos, (scale_factor, scale_factor),(1, 0), 255)

    @property
    def image_path(self):
        return self.image_src

    @image_path.setter
    def image_path(self, value):
        self.image_src = value

    @property
    def pos(self):
        return self.position2d

    @pos.setter
    def pos(self, pos):
        self.position2d = pos

    @property
    def img(self):
        return self._cached_transformed_image

    @property
    def width(self):
        return self._size2d()[0]

    @width.setter
    def width(self, width):
        scale_x = self.image.get_width() / width
        scale_y = self.scale2d[1]
        self.scale2d = (scale_x, scale_y)

    @property
    def height(self):
        return self._size2d()[1]

    @height.setter
    def height(self, height):
        scale_y = self.image.get_height() / height
        scale_x = self.scale2d[0]
        self.scale2d = (scale_x, scale_y)


class ClickableLabel(Label):
    def __init__(self, image_path1, image_path2, pos, scale_factor=0.2):
        super().__init__(image_path1, pos, scale_factor=scale_factor)
        self.image_path1 = image_path1  # pict for normal(without click)
        self.image_path2 = image_path2  # pict for hover
        # self.img_normal = load_and_scale_image(self.image_path1, scale_factor)
        # self.img_hover = load_and_scale_image(self.image_path2, scale_factor)
        self.img_src_normal = self.image_path1
        self.img_src_hover = self.image_path2
        # self.img = self.img_normal
        # self.width = self.img.get_width()
        # self.height = self.img.get_height()
        self.click_listener_list = []

    def is_inside(self, pos):
        return self.pos[0] <= pos[0] <= self.pos[0] + self.width and \
            self.pos[1] <= pos[1] <= self.pos[1] + self.height

    def update(self):
        if self.is_inside(pygame.mouse.get_pos()):
            self.image_src = self.img_src_hover
        else:
            self.image_src = self.img_src_normal

    def mouseup(self, event):
        if event.button == 1 and self.is_inside(event.pos):
            self.click()

    def click(self):
        for listener in self.click_listener_list:
            listener()

    def add_click_listener(self, function):
        self.click_listener_list.append(function)


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
        global PATH_CARDS
        filename = f"{color}_{number}.png"
        filepath = os.path.join(PATH_CARDS, filename)
        if os.path.exists(filepath):
            return filepath
        return os.path.join(PATH_CARDS, "default.png")

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


class ScreenBase:
    def __init__(self, background_filename=None):
        """Initialize the screen with an optional background image."""
        self.objects = []

        # Set background to a solid color if no image is provided
        if background_filename is not None:
            if os.path.exists(background_filename):
                self.background_image = pygame.image.load(background_filename)
                self.background_image = pygame.transform.scale(self.background_image,
                                                               (800, 600))  # Scale to screen size
            else:
                raise FileNotFoundError(f"Warning: Background image {background_filename} not found.")
                print(f"Warning: Background image {background_filename} not found.")
                self.background_image = None
        else:
            self.background_image = None

    def draw(self, screen):
        """Draw the background image or solid color, and all objects."""
        if self.background_image is not None:
            screen.blit(self.background_image, (0, 0))
        else:
            screen.fill((0, 0, 0))  # Default to black if no background image is set

        # Draw all objects in the objects list
        for o in self.objects:
            o.draw(screen)

    def update(self):
        """Update all objects on the screen."""
        for o in self.objects:
            o.update()

    def keydown(self, event):
        """Handle keydown events."""
        pass

    def mouseup(self, event):
        """Handle mouseup events."""
        for o in self.objects:
            o.mouseup(event)


class StartScreen(ScreenBase):
    def __init__(self):
        """Initialize the StartScreen with the background image and some objects."""
        global PATH_SCREEN
        super().__init__(background_filename = os.path.join(PATH_SCREEN, "StartScreen.png"))  # Set the background to 'startscreen.png'

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
        global PATH_SCREEN
        super().__init__(background_filename= os.path.join(PATH_SCREEN, "HomeScreen.png"))  # Set background for the home screen

        # Define the font for labels
        font = pygame.font.Font(None, 40)
        global PATH_LABELS
        # Create the clickable labels with positions (already defined classes)
        # self.play_label = PlayGameLabel("labels/play_game_label.png", "labels/clickable_play_game_label.png",(400, 200))
        self.play_label = ClickableLabel(os.path.join(PATH_LABELS, "play_game_label.png"), os.path.join(PATH_LABELS, "clickable_play_game_label.png"),
                                        (400, 200), 0.2)
        self.play_label.add_click_listener(lambda : change_screen(StartGameScreen()))
        # self.rules_label = RulesLabel("labels/rules_label.png", "labels/clickable_rules_label.png", (400, 275))
        self.rules_label = ClickableLabel(os.path.join(PATH_LABELS, "rules_label.png"), os.path.join(PATH_LABELS,"clickable_rules_label.png"), (400, 275))
        self.rules_label.add_click_listener(lambda : change_screen(RuleScreen()))
        self.exit_label = ExitGameLabel(os.path.join(PATH_LABELS, "exit_label.png"), os.path.join(PATH_LABELS, "clickable_exit_label.png"), (400, 350))

        # Add labels to the screen objects list
        self.objects.append(self.play_label)
        self.objects.append(self.rules_label)
        self.objects.append(self.exit_label)


class RuleScreen(ScreenBase):
    def __init__(self):
        """Initialize the RuleScreen with the background image rulescreen.png."""
        global PATH_SCREEN
        super().__init__(background_filename= os.path.join(PATH_SCREEN, "rulescreen.png", ))


class StartGameScreen(ScreenBase):
    def __init__(self):
        """Initialize the StartGameScreen with the background image startgamescreen.png."""
        global PATH_SCREEN
        super().__init__(background_filename= os.path.join(PATH_SCREEN, "StartGameScreen.png"))  # Set background for the start game screen

        global PATH_LABELS
        # Add clickable labels for the player selection
        self.two_player_label = TwoPlayerLabel(os.path.join(PATH_LABELS, "two_player.png"), os.path.join(PATH_LABELS, "clickable_two_player.png"), (200, 375))
        self.three_player_label = ThreePlayerLabel(os.path.join(PATH_LABELS, "three_player.png"), os.path.join(PATH_LABELS, "clickable_three_player.png"),
                                                   (590, 375))

        # Add the labels to the screen objects
        self.objects.append(self.two_player_label)
        self.objects.append(self.three_player_label)


class PlayScreen(ScreenBase):
    def __init__(self, num_players):
        # Initialize the PlayScreen with a specific background
        global PATH_SCREEN
        super().__init__(background_filename= os.path.join(PATH_SCREEN, 'PlayScreen.png'))

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

        global PATH_LABELS

        self.deck_label = ClickableLabel( os.path.join(PATH_LABELS, "deck_label.png"), os.path.join(PATH_LABELS,"clickable_deck_label.png"), (WINDOW_WIDTH/2,WINDOW_HEIGHT/2), 0.1)
        self.game_pass_label = ClickableLabel(os.path.join(PATH_LABELS, "game_pass_label.png"), os.path.join(PATH_LABELS,"clickable_game_pass_label.png"),
                                             (50, 550),2)  # Position the label horizontally at the bottom
        self.draw_card_label = ClickableLabel(os.path.join(PATH_LABELS,"draw_card_label.png"), os.path.join(PATH_LABELS,"clickable_draw_card_label.png"),
                                             (200, 550),2)
        self.discard_label = ClickableLabel(os.path.join(PATH_LABELS,"discard_label.png"), os.path.join(PATH_LABELS,"clickable_discard_label.png"), (350, 550),2)
        self.play_for_me_label = ClickableLabel(os.path.join(PATH_LABELS,"play_for_me_label.png"),
                                                os.path.join(PATH_LABELS,"clickable_play_for_me_label.png"), (650, 550),2)

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
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
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
