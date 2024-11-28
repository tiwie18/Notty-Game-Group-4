import pygame
from pygame.locals import *
import random
from enum import Enum
import os
import scripts.math_util as math_util
from scripts.ui_base import *
from scripts.screen_base import *

# Create __init__.py in the scripts directory if it doesn't exist
scripts_dir = os.path.join(os.getcwd(), 'scripts')
init_file = os.path.join(scripts_dir, '__init__.py')

if not os.path.exists(init_file):
    with open(init_file, 'w') as f:
        pass  # Create an empty file

print(f"Created {init_file}")

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600

# Card spacing constants
CARD_WIDTH = 80
CARD_HEIGHT = 120
HORIZONTAL_SPACING = 30  # Space between cards horizontally
VERTICAL_SPACING = 20  # Space between cards vertically
STACK_OFFSET = 15  # Offset for stacked cards

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


class LoadScreenLabel(ClickableLabel):
    def __init__(self, image_path_1, image_path_2, pos, screen_class, scale_factor=0.2):
        super().__init__(image_path_1, image_path_2, pos, scale_factor)
        self.screen_class = screen_class

    def click(self):
        global current_screen
        current_screen = self.screen_class()


class DrawCardLabel(ClickableLabel):
    def __init__(self, game):
        self.game = game  # Reference to the PlayGame instance

    def display_action_options(self):
        choice = input("Choose action:\n1. Take a card from the opponent\n2. Draw cards from the deck\n")

        if choice == '1':
            self.game.take_card_from_opponent()
        elif choice == '2':
            self.game.draw_cards_from_deck()
        else:
            print("Invalid choice. Please choose again.")

    def reset_turn(self):
        self.game.reset_turn()


class DiscardLabel(ClickableLabel):
    def __init__(self, game):
        self.game = game

    def click(self):
        self.game.discard_card()


class PlayForMeLabel(ClickableLabel):
    def __init__(self, game):
        self.game = game

    def click(self):
        self.game.play_for_me()


class GamePassLabel(ClickableLabel):
    def __init__(self, image_path_1, image_path_2, pos, scale_factor=0.2):
        super().__init__(image_path_1, image_path_2, pos, scale_factor=scale_factor)

    def click(self):
        pass


class NewGameLabel(ClickableLabel):
    def click(self):
        global current_screen
        current_screen = HomeScreen()


class ExitGameLabel(ClickableLabel):
    def click(self):
        global game_over
        game_over = True


class DeckLabel(ClickableLabel):
    def click(self):
        global current_screen


class Card(RenderableImage):

    def __init__(self, color, number, position2d=(0, 0), scale2d=(0.2, 0.2), rotation2d=(1, 0)):
        self.image_path = f"resources/images/cards/{color}_{number}.png"
        self.image_path_back = f"resources/images/card/backside_card_new.png"
        super().__init__(self.image_path, position2d, scale2d, rotation2d)
        self.color = color
        self.number = number
        self.selected = False
        self.highlighted = False
        self.rect = pygame.Rect(position2d[0] - CARD_WIDTH / 2,
                                position2d[1] - CARD_HEIGHT / 2,
                                CARD_WIDTH, CARD_HEIGHT)

    def flip(self, to_back = True):
        """
        flip over the cards, true for back side false for
        """
        if to_back:
            self.image_src = self.image_path_back
        else:
            self.image_src = self.image_path

    def update_position(self, new_pos):
        """Update both the display position and collision rect"""
        self.position2d = new_pos
        self.rect.x = new_pos[0] - CARD_WIDTH / 2
        self.rect.y = new_pos[1] - CARD_HEIGHT / 2

    def draw(self, screen):
        if self.highlighted or self.selected:
            # Create highlight surface
            highlight = pygame.Surface((CARD_WIDTH + 8, CARD_HEIGHT + 8))
            highlight.set_alpha(150)  # Make it slightly transparent

            if self.highlighted:
                highlight.fill((147, 112, 219))  # Purple for opponent's card
            else:
                highlight.fill((255, 140, 0))  # Orange for selected card

            # Draw highlight behind card
            highlight_x = self.position2d[0] - (CARD_WIDTH + 8) / 2
            highlight_y = self.position2d[1] - (CARD_HEIGHT + 8) / 2
            screen.blit(highlight, (highlight_x, highlight_y))

        # Draw the card
        super().draw(screen)

    def contains_point(self, pos):
        return self.rect.collidepoint(pos)


class Player:
    def __init__(self, position, cards=None):
        self.position = position  # 'bottom', 'top', 'left', or 'right'
        self.cards = cards if cards else []
        self.selected_cards = []

    def add_card(self, card):
        self.cards.append(card)
        self.update_card_positions()

    def remove_card(self, card):
        if card in self.cards:
            self.cards.remove(card)
            if card in self.selected_cards:
                self.selected_cards.remove(card)
            self.update_card_positions()

    def update_card_positions(self):
        if not self.cards:
            return

        stacked = len(self.cards) > 5

        if self.position in ['bottom', 'top']:
            self._arrange_horizontal(stacked)
        else:
            self._arrange_vertical(stacked)

    def _arrange_horizontal(self, stacked):
        """Arrange cards horizontally (for bottom and top players)"""
        # Calculate total width based on number of visible cards
        total_width = CARD_WIDTH * (5 if stacked else len(self.cards))
        if not stacked:
            total_width += HORIZONTAL_SPACING * (len(self.cards) - 1)

        # Center the cards horizontally
        start_x = (WINDOW_WIDTH - total_width) / 2
        # Position cards at top or bottom
        y = WINDOW_HEIGHT - CARD_HEIGHT - 60 if self.position == 'bottom' else 60

        for i, card in enumerate(self.cards):
            if stacked:
                # Calculate horizontal stack offset
                x_offset = min(i, 4) * (total_width / 4)  # Position first 5 cards
                stack_x_offset = (i - 4) * HORIZONTAL_SPACING / 2 if i >= 5 else 0  # Offset additional cards
                x = start_x + x_offset + stack_x_offset
                card.update_position((x, y))
            else:
                # Simple horizontal layout
                x = start_x + i * (CARD_WIDTH + HORIZONTAL_SPACING)
                card.update_position((x, y))

            # Set card rotation based on position
            if self.position == 'top':
                card.rotation2d = math_util.euler_angle_to_rotation(180)  # Face down
            else:  # bottom
                card.rotation2d = math_util.euler_angle_to_rotation(0)  # Face up

    def _arrange_vertical(self, stacked):
        total_height = CARD_HEIGHT * (5 if stacked else len(self.cards))
        if not stacked:
            total_height += VERTICAL_SPACING * (len(self.cards) - 1)

        # Position cards at sides
        x = 100 if self.position == 'left' else WINDOW_WIDTH - 100
        start_y = (WINDOW_HEIGHT - total_height) / 2

        for i, card in enumerate(self.cards):
            # Calculate y position with stacking
            if stacked:
                y_offset = min(i, 4) * (CARD_HEIGHT + VERTICAL_SPACING)
                x_offset = (i - 4) * HORIZONTAL_SPACING / 2 if i >= 5 else 0
                final_x = x + (x_offset if self.position == 'left' else -x_offset)
                card.update_position((final_x, start_y + y_offset))
            else:
                card.update_position((x, start_y + i * (CARD_HEIGHT + VERTICAL_SPACING)))

            # Set orientation - cards should face inward
            angle = 90 if self.position == 'left' else -90
            card.rotation2d = math_util.euler_angle_to_rotation(angle)

    def handle_click(self, pos):
        for card in self.cards:
            if card.rect.collidepoint(pos):
                return card
        return None


class GameState:

    def __init__(self, num_players=2):
        self.players = []
        self.current_player = 0
        self.deck = self._create_deck()
        self._init_players(num_players)
        self.selected_opponent_card = None
        self.has_drawn_this_turn = False
        self.num_players = num_players

    def _create_deck(self):
        """Create and shuffle the initial deck"""
        colors = ['red', 'blue', 'green', 'yellow']
        numbers = range(1, 11)
        deck = []
        for _ in range(2):  # Two of each card
            for color in colors:
                for number in numbers:
                    deck.append(Card(color, number))
        random.shuffle(deck)
        return deck

    def _init_players(self, num_players):
        """Initialize players with their starting hands"""
        positions = ['bottom', 'top'] if num_players == 2 else ['bottom', 'left', 'right']
        for position in positions:
            initial_cards = [self.deck.pop() for _ in range(5)]
            self.players.append(Player(position, initial_cards))
            self.players[-1].update_card_positions()

    def clear_highlights(self):
        """Clear all highlights and selections"""
        if self.selected_opponent_card:
            self.selected_opponent_card.highlighted = False
            self.selected_opponent_card = None

        for player in self.players:
            for card in player.cards:
                card.highlighted = False

    def is_valid_sequence(self, cards):
        """Check if cards form a valid sequence (same color, consecutive numbers)"""
        if len(cards) < 3:
            return False

        color = cards[0].color
        if not all(card.color == color for card in cards):
            return False

        numbers = sorted(card.number for card in cards)
        return all(numbers[i] + 1 == numbers[i + 1] for i in range(len(numbers) - 1))

    def is_valid_set(self, cards):
        """Check if cards form a valid set (same number, different colors)"""
        if len(cards) < 3:
            return False

        number = cards[0].number
        if not all(card.number == number for card in cards):
            return False

        colors = [card.color for card in cards]
        return len(colors) == len(set(colors))  # All colors must be different

    def is_valid_group(self, cards):
        """Check if cards form either a valid sequence or set"""
        return self.is_valid_sequence(cards) or self.is_valid_set(cards)

    def handle_click(self, pos):
        """Handle clicking on a card"""
        # Check opponent's cards first
        for i, player in enumerate(self.players):
            if i != self.current_player:
                clicked_card = player.handle_click(pos)
                if clicked_card:
                    if self.selected_opponent_card:
                        self.selected_opponent_card.highlighted = False
                    self.selected_opponent_card = clicked_card
                    clicked_card.highlighted = True
                    return True

        # Then check current player's cards
        current_player = self.players[self.current_player]
        clicked_card = current_player.handle_click(pos)
        if clicked_card:
            clicked_card.selected = not clicked_card.selected
            if clicked_card.selected:
                current_player.selected_cards.append(clicked_card)
            else:
                if clicked_card in current_player.selected_cards:
                    current_player.selected_cards.remove(clicked_card)
            return True

        return False

    def take_opponent_card(self):
        """Take a highlighted card from an opponent"""
        if self.selected_opponent_card and not self.has_drawn_this_turn:
            for player in self.players:
                if self.selected_opponent_card in player.cards:
                    player.remove_card(self.selected_opponent_card)
                    self.players[self.current_player].add_card(self.selected_opponent_card)
                    self.selected_opponent_card.highlighted = False
                    self.selected_opponent_card = None
                    self.has_drawn_this_turn = True
                    return True
        return False

    def draw_cards(self, num_cards=1):
        """Draw cards from the deck"""
        if not self.has_drawn_this_turn:
            for _ in range(min(num_cards, 3)):  # Maximum 3 cards per turn
                if self.deck:
                    card = self.deck.pop()
                    self.players[self.current_player].add_card(card)
            self.has_drawn_this_turn = True
            current_player = self.players[self.current_player]
            current_player.update_card_positions()
            return True
        return False

    def discard_cards(self, cards):
        """Discard a valid group of cards"""
        if not self.is_valid_group(cards):
            return False

        current_player = self.players[self.current_player]
        for card in cards:
            current_player.remove_card(card)
            self.deck.append(card)

        random.shuffle(self.deck)
        current_player.update_card_positions()
        return True

    def end_turn(self):
        """End the current player's turn and move to the next player"""
        # Reset current player's state
        current_player = self.players[self.current_player]
        for card in current_player.selected_cards:
            card.selected = False
        current_player.selected_cards.clear()

        # Reset opponent card selection
        if self.selected_opponent_card:
            self.selected_opponent_card.highlighted = False
            self.selected_opponent_card = None

        # Reset turn flags and move to next player
        self.has_drawn_this_turn = False
        self.current_player = (self.current_player + 1) % len(self.players)

        # Update all players' card positions
        for player in self.players:
            player.update_card_positions()

    def draw(self, screen):
        """Draw all players' cards"""
        for player in self.players:
            for card in player.cards:
                card.draw(screen)

    def check_winner(self):
        """Check if there's a winner (player with no cards)"""
        for i, player in enumerate(self.players):
            if len(player.cards) == 0:
                return i
        return None


class StartScreen(ScreenBase):
    def __init__(self):
        super().__init__(background_filename="resources/images/ui/screens/StartScreen.png")
        self.start_time = pygame.time.get_ticks()
        self.transition_delay = 3000

    def update(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.start_time >= self.transition_delay:
            self.transition_to_home_screen()

    def transition_to_home_screen(self):
        global current_screen
        print("Transitioning to HomeScreen...")
        current_screen = HomeScreen()


class HomeScreen(ScreenBase):
    def __init__(self):
        super().__init__(background_filename="resources/images/ui/screens/HomeScreen.png")
        font = pygame.font.Font(None, 40)

        self.play_label = ClickableLabel("resources/images/ui/labels/play_game_label.png",
                                         "resources/images/ui/labels/clickable_play_game_label.png",
                                         (400, 200), 0.2)
        self.play_label.add_click_listener(lambda: change_screen(StartGameScreen()))
        self.rules_label = ClickableLabel("resources/images/ui/labels/rules_label.png",
                                          "resources/images/ui/labels/clickable_rules_label.png",
                                          (400, 275))
        self.rules_label.add_click_listener(lambda: change_screen(RuleScreen()))
        self.exit_label = ExitGameLabel("resources/images/ui/labels/exit_label.png",
                                        "resources/images/ui/labels/clickable_exit_label.png",
                                        (400, 350))

        self.objects.append(self.play_label)
        self.objects.append(self.rules_label)
        self.objects.append(self.exit_label)


class RuleScreen(ScreenBase):
    def __init__(self):
        super().__init__(background_filename="resources/images/ui/screens/rulescreen.png")


class StartGameScreen(ScreenBase):
    def __init__(self):
        super().__init__(background_filename="resources/images/ui/screens/StartGameScreen.png")

        self.two_player_label = LoadScreenLabel("resources/images/ui/labels/two_player.png",
                                               "resources/images/ui/labels/clickable_two_player.png",
                                               (200, 375), TwoPlayerScreen)
        self.three_player_label = LoadScreenLabel("resources/images/ui/labels/three_player.png",
                                                   "resources/images/ui/labels/clickable_three_player.png",
                                                   (590, 375), ThreePlayerScreen)

        self.objects.append(self.two_player_label)
        self.objects.append(self.three_player_label)


class TwoPlayerScreen(ScreenBase):
    def __init__(self):
        super().__init__(background_filename='resources/images/ui/screens/PlayScreen.png')
        self.game_state = GameState(num_players=2)

        # Initialize all buttons
        button_scale = 0.1
        button_y = WINDOW_HEIGHT - 30
        self.buttons = {
            'deck': ClickableLabel(
                "resources/images/ui/labels/deck_label.png",
                "resources/images/ui/labels/clickable_deck_label.png",
                (WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2),
                0.15
            ),
            'pass': ClickableLabel(
                "resources/images/ui/labels/game_pass_label.png",
                "resources/images/ui/labels/clickable_game_pass_label.png",
                (50, button_y),
                button_scale
            ),
            'draw': ClickableLabel(
                "resources/images/ui/labels/draw_card_label.png",
                "resources/images/ui/labels/clickable_draw_card_label.png",
                (175, button_y),
                button_scale
            ),
            'discard': ClickableLabel(
                "resources/images/ui/labels/discard_label.png",
                "resources/images/ui/labels/clickable_discard_label.png",
                (300, button_y),
                button_scale
            ),
            'auto': ClickableLabel(
                "resources/images/ui/labels/play_for_me_label.png",
                "resources/images/ui/labels/clickable_play_for_me_label.png",
                (425, button_y),
                button_scale
            )
        }

        # Set up button click handlers
        self.buttons['pass'].add_click_listener(self.handle_pass)
        self.buttons['draw'].add_click_listener(self.handle_draw)
        self.buttons['discard'].add_click_listener(self.handle_discard)
        self.buttons['auto'].add_click_listener(self.handle_play_for_me)
        self.buttons['deck'].add_click_listener(self.handle_deck_click)

        # Add buttons to objects list
        self.objects.extend(self.buttons.values())

    def handle_card_click(self, pos):
        """Handle clicking on cards"""
        for player in self.game_state.players:
            for card in player.cards:
                if card.rect.collidepoint(pos):
                    if player == self.game_state.players[self.game_state.current_player]:
                        # Toggle selection for current player's cards
                        card.selected = not card.selected
                        if card.selected:
                            player.selected_cards.append(card)
                        else:
                            if card in player.selected_cards:
                                player.selected_cards.remove(card)
                    else:
                        # Highlight opponent's card
                        self.game_state.clear_highlights()
                        card.highlighted = True
                        self.game_state.selected_opponent_card = card
                    return True
        return False

    def handle_pass(self):
        self.game_state.end_turn()

    def handle_draw(self):
        self.game_state.draw_cards(3)

    def handle_discard(self):
        current_player = self.game_state.players[self.game_state.current_player]
        if len(current_player.selected_cards) >= 3:
            if self.game_state.is_valid_group(current_player.selected_cards):
                self.game_state.discard_cards(current_player.selected_cards)

    def handle_play_for_me(self):
        pass

    def handle_deck_click(self):
        self.game_state.draw_cards(1)

    def mouseup(self, event):
        if event.button == 1:  # Left click
            if not self.handle_card_click(event.pos):
                # If no card was clicked, check buttons
                for button in self.buttons.values():
                    if button.is_inside(event.pos):
                        button.click()

            # Update card positions after any changes
            for player in self.game_state.players:
                player.update_card_positions()

    def keydown(self, event):
        if event.key == K_SPACE:
            self.game_state.take_opponent_card()
        elif event.key == K_RETURN:
            self.game_state.end_turn()
        elif event.key == K_ESCAPE:
            global current_screen
            current_screen = HomeScreen()

    def draw(self, screen):
        # Draw background
        super().draw(screen)

        # Draw game state
        self.game_state.draw(screen)

        # Draw UI elements
        for button in self.buttons.values():
            button.draw(screen)

        # Draw turn indicator
        font = pygame.font.Font(None, 36)
        text = font.render(f"Player {self.game_state.current_player + 1}'s Turn", True, (255, 255, 255))
        screen.blit(text, (10, 10))

    def update(self):
        for button in self.buttons.values():
            button.update()


class ThreePlayerScreen(ScreenBase):
    def __init__(self):
        super().__init__(background_filename='resources/images/ui/screens/PlayScreen.png')
        self.game_state = GameState(num_players=3)

        button_scale = 0.1
        button_y = WINDOW_HEIGHT - 30

        self.buttons = {
            'deck': ClickableLabel(
                "resources/images/ui/labels/deck_label.png",
                "resources/images/ui/labels/clickable_deck_label.png",
                (WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2),
                0.1
            ),
            'pass': ClickableLabel(
                "resources/images/ui/labels/game_pass_label.png",
                "resources/images/ui/labels/clickable_game_pass_label.png",
                (50, button_y),
                0.1
            ),
            'draw': ClickableLabel(
                "resources/images/ui/labels/draw_card_label.png",
                "resources/images/ui/labels/clickable_draw_card_label.png",
                (175, button_y),
                0.05
            ),
            'discard': ClickableLabel(
                "resources/images/ui/labels/discard_label.png",
                "resources/images/ui/labels/clickable_discard_label.png",
                (300, button_y),
                0.05
            ),
            'auto': ClickableLabel(
                "resources/images/ui/labels/play_for_me_label.png",
                "resources/images/ui/labels/clickable_play_for_me_label.png",
                (425, button_y),
                0.05
            )
        }

        # Set up button click handlers
        self.buttons['pass'].add_click_listener(self.handle_pass)
        self.buttons['draw'].add_click_listener(self.handle_draw)
        self.buttons['discard'].add_click_listener(self.handle_discard)
        self.buttons['auto'].add_click_listener(self.handle_play_for_me)
        self.buttons['deck'].add_click_listener(self.handle_deck_click)

        # Add buttons to objects list
        self.objects.extend(self.buttons.values())

    # All handlers and methods same as TwoPlayerScreen
    def handle_card_click(self, pos):
        """Handle clicking on cards"""
        for player in self.game_state.players:
            for card in player.cards:
                if card.rect.collidepoint(pos):
                    if player == self.game_state.players[self.game_state.current_player]:
                        # Toggle selection for current player's cards
                        card.selected = not card.selected
                        if card.selected:
                            player.selected_cards.append(card)
                        else:
                            if card in player.selected_cards:
                                player.selected_cards.remove(card)
                    else:
                        # Highlight opponent's card
                        self.game_state.clear_highlights()
                        card.highlighted = True
                        self.game_state.selected_opponent_card = card
                    return True
        return False

    def handle_pass(self):
        self.game_state.end_turn()

    def handle_draw(self):
        self.game_state.draw_cards(3)

    def handle_discard(self):
        current_player = self.game_state.players[self.game_state.current_player]
        if len(current_player.selected_cards) >= 3:
            if self.game_state.is_valid_group(current_player.selected_cards):
                self.game_state.discard_cards(current_player.selected_cards)

    def handle_play_for_me(self):
        pass

    def handle_deck_click(self):
        self.game_state.draw_cards(1)

    def mouseup(self, event):
        if event.button == 1:  # Left click
            if not self.handle_card_click(event.pos):
                # If no card was clicked, check buttons
                for button in self.buttons.values():
                    if button.is_inside(event.pos):
                        button.click()

            # Update card positions after any changes
            for player in self.game_state.players:
                player.update_card_positions()

    def keydown(self, event):
        if event.key == K_SPACE:
            self.game_state.take_opponent_card()
        elif event.key == K_RETURN:
            self.game_state.end_turn()
        elif event.key == K_ESCAPE:
            global current_screen
            current_screen = HomeScreen()

    def draw(self, screen):
        # Draw background
        super().draw(screen)

        # Draw game state
        self.game_state.draw(screen)

        # Draw UI elements
        for button in self.buttons.values():
            button.draw(screen)

        # Draw turn indicator
        font = pygame.font.Font(None, 36)
        text = font.render(f"Player {self.game_state.current_player + 1}'s Turn", True, (255, 255, 255))
        screen.blit(text, (10, 10))

        # Draw player labels for 3-player mode
        self.draw_player_labels(screen)

    def draw_player_labels(self, screen):
        """Draw labels to identify each player in three player layout"""
        font = pygame.font.Font(None, 24)

        # Bottom player (current player)
        bottom_text = font.render("Player 1", True, (255, 255, 255))
        screen.blit(bottom_text, (WINDOW_WIDTH / 2 - 30, WINDOW_HEIGHT - 20))

        # Left player
        left_text = font.render("Player 2", True, (255, 255, 255))
        screen.blit(left_text, (20, WINDOW_HEIGHT / 2))

        # Right player
        right_text = font.render("Player 3", True, (255, 255, 255))
        screen.blit(right_text, (WINDOW_WIDTH - 100, WINDOW_HEIGHT / 2))

    def update(self):
        for button in self.buttons.values():
            button.update()


class CongratsScreen(ScreenBase):
    def __init__(self):
        super().__init__(background_filename='resources/images/ui/screens/CongratsScreen.png')

        self.newgame_label = NewGameLabel("resources/images/ui/labels/new_game_label.png",
                                          "resources/images/ui/labels/clickable_new_game_label.png",
                                          (350, 250))
        self.exitgame_label = ExitGameLabel("resources/images/ui/labels/exit_label.png",
                                            "resources/images/ui/labels/clickable_exit_label.png",
                                            (350, 350))

        self.objects.append(self.newgame_label)
        self.objects.append(self.exitgame_label)

    def keydown(self, event):
        if event.key == K_ESCAPE:
            global game_over
            game_over = True


class LoseScreen(ScreenBase):
    def __init__(self):
        super().__init__(background_filename='resources/images/ui/screens/LoseScreen.png')

        self.newgame_label = NewGameLabel("resources/images/ui/labels/new_game_label.png",
                                          "resources/images/ui/labels/clickable_new_game_label.png",
                                          (350, 250))
        self.exitgame_label = ExitGameLabel("resources/images/ui/labels/exit_label.png",
                                            "resources/images/ui/labels/clickable_exit_label.png",
                                            (350, 350))

        self.objects.append(self.newgame_label)
        self.objects.append(self.exitgame_label)

    def keydown(self, event):
        if event.key == K_ESCAPE:
            global game_over
            game_over = True


from time import sleep

pygame.init()
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption('Card Game Funt4stic Te4m')
current_screen = StartScreen()


def main():
    global current_screen
    game_over = False

    while not game_over:
        for event in pygame.event.get():
            if event.type == QUIT:
                game_over = True
            if event.type == MOUSEBUTTONUP:
                current_screen.mouseup(event)
            if event.type == KEYDOWN:
                current_screen.keydown(event)

        current_screen.update()
        current_screen.draw(screen)
        pygame.display.flip()
        pygame.time.delay(30)

    pygame.quit()


if __name__ == "__main__":
    main()
