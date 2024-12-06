import pygame
from pygame.locals import *
import random
from enum import Enum
import os
import scripts.math_util as math_util
import scripts.main as core
from scripts.animation import *

# Create __init__.py in the scripts directory if it doesn't exist
scripts_dir = os.path.join(os.getcwd(), 'scripts')
init_file = os.path.join(scripts_dir, '__init__.py')

if not os.path.exists(init_file):
    with open(init_file, 'w') as f:
        pass  # Create an empty file

print(f"Created {init_file}")

WINDOW_WIDTH = 900
WINDOW_HEIGHT = 675
UNI_SCALE = WINDOW_HEIGHT / 3546

# Card spacing constants
CARD_WIDTH = 80
CARD_HEIGHT = 120
HORIZONTAL_SPACING = 5  # Space between cards horizontally
VERTICAL_SPACING = -40  # Space between cards vertically
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


def pop_up_buttons(button_list, pretime=0, posttime=1):
    for button in button_list:
        original_scale2d = button.scale2d
        button.scale2d = (0, 0)
        scale_animation_sequence = AnimationSequenceTask(loop=False)

        animation_task_1 = constant_2d("scale2d", (0, 0), pretime + 1)
        animation_task_2 = overshoot_2d("scale2d", (0, 0), original_scale2d, 0.5, overshoot=0.6)
        animation_task_3 = constant_2d("scale2d", original_scale2d, posttime)

        scale_animation_sequence.add_sub_task(animation_task_1)
        scale_animation_sequence.add_sub_task(animation_task_2)
        scale_animation_sequence.add_sub_task(animation_task_3)

        animation.play_animation(button, scale_animation_sequence, layer=1)
        pretime += 0.1
        posttime -= 0.1


class VisualObject:
    def __init__(self, position2d=(0, 0), scale2d=(1, 1), rotation2d=(1, 0), alpha=255):
        self.position2d = position2d
        self.scale2d = scale2d
        self.rotation2d = rotation2d
        self.alpha = alpha
        self.visible = True
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

    def __init__(self, image_src, position2d=(0, 0), scale2d=(1, 1), rotation2d=(1, 0), alpha=255):
        super().__init__(position2d=position2d, scale2d=scale2d, rotation2d=rotation2d, alpha=alpha)
        self.image_src = image_src
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
            self._store_cache()
        elif self._cached_size2d != self._size2d() or self.rotation2d != self._cached_rotation2d or self.alpha != self._cached_alpha:
            self._store_cache()

    def draw(self, screen):
        if not self.visible:
            return
        self._update_cache_if_dirty()
        rect = self._cached_transformed_image.get_rect(center=self.position2d)
        screen.blit(self._cached_transformed_image, rect.topleft)

    def update(self):
        pass


class Label(RenderableImage):
    # if it's image instead of text:
    def __init__(self, image_path, pos, scale_factor=0.2):
        super().__init__(image_path, pos, (scale_factor, scale_factor), (1, 0), 255)

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
        super().__init__(image_path1, pos, scale_factor)  # Pass scale_factor to parent
        self.image_path1 = image_path1  # pict for normal(without click)
        self.image_path2 = image_path2  # pict for hover
        self.img_src_normal = self.image_path1
        self.img_src_hover = self.image_path2
        self.click_listener_list = []
        self._cursor_inside = False
        self.cursor_enter_listener_list = []
        self.cursor_exit_listener_list = []
        self._enabled = True
        self.on_enabled_listener_list = []
        self.on_disabled_listener_list = []

    @property
    def enabled(self):
        return self._enabled

    @enabled.setter
    def enabled(self, enabled):
        if self._enabled != enabled:
            self._enabled = enabled
            if enabled:
                for listener in self.on_enabled_listener_list:
                    listener()
            else:
                for listener in self.on_disabled_listener_list:
                    listener()

    def is_inside(self, pos):
        return self.pos[0] - self.width * 0.5 <= pos[0] <= self.pos[0] + self.width * 0.5 and \
            self.pos[1] - self.height * 0.5 <= pos[1] <= self.pos[1] + self.height * 0.5

    def update(self):
        if not self._enabled:
            return
        if self.is_inside(pygame.mouse.get_pos()):
            if not self._cursor_inside:
                self._cursor_inside = True
                for listener in self.cursor_enter_listener_list:
                    listener()
            self.image_src = self.img_src_hover
        else:
            if self._cursor_inside:
                self._cursor_inside = False
                for listener in self.cursor_exit_listener_list:
                    listener()
            self.image_src = self.img_src_normal

    def mouseup(self, event):
        if event.button == 1 and self.is_inside(event.pos):
            self.click()

    def click(self):
        if not self._enabled:
            return
        for listener in self.click_listener_list:
            listener()

    def add_click_listener(self, function):
        self.click_listener_list.append(function)

    def add_on_cursor_enter_listener(self, function):
        self.cursor_enter_listener_list.append(function)

    def add_on_cursor_exit_listener(self, function):
        self.cursor_exit_listener_list.append(function)

    def add_on_enabled_listener(self, function):
        self.on_enabled_listener_list.append(function)

    def add_on_disabled_listener(self, function):
        self.on_disabled_listener_list.append(function)


def set_label_cursor_anim_effect(label: ClickableLabel):
    start_angle = label.euler_angle
    start_scale2d = label.scale2d
    end_scale2d = math_util.vec_2d_mul(start_scale2d, 1.2)
    amplitude = 5
    label.add_on_cursor_enter_listener(
        lambda: animation.play_animation(label, vibrate_once_1d("euler_angle", start_angle, amplitude, 0.2)))
    label.add_on_cursor_enter_listener(
        lambda: animation.play_animation(label, overshoot_2d("scale2d", start_scale2d, end_scale2d, 0.2), layer=1))
    label.add_on_cursor_exit_listener(
        lambda: animation.play_animation(label, overshoot_2d("scale2d", end_scale2d, start_scale2d, 0.2), layer=1))


def set_label_enable_anim_effect(label: ClickableLabel):
    start_scale2d = label.scale2d
    end_scale2d = (0, 0)
    label.add_on_enabled_listener(
        lambda: animation.play_animation(label, overshoot_2d("scale2d", end_scale2d, start_scale2d, 0.2), layer=1))
    label.add_on_disabled_listener(
        lambda: animation.play_animation(label, move_to("scale2d", start_scale2d, end_scale2d, 0.2), layer=1))


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


class BackLabel(ClickableLabel):
    def __init__(self, image_path1, image_path2, pos, scale_factor=0.1):
        super().__init__(image_path1, image_path2, pos, scale_factor)
        self.click_listener_list = []

    def click(self):
        global current_screen
        current_screen = HomeScreen()


class TwoPlayerLabel(ClickableLabel):
    def __init__(self, image_path1, image_path2, pos, scale_factor=0.2):
        super().__init__(image_path1, image_path2, pos, scale_factor)
        self.click_listener_list = []  # Initialize click listener list

    def click(self):
        """Handle click on two player button"""
        global current_screen
        print("Creating TwoPlayerScreen...")  # Debug print
        current_screen = TwoPlayerScreen()


class ThreePlayerLabel(ClickableLabel):
    def __init__(self, image_path1, image_path2, pos, scale_factor=0.2):
        super().__init__(image_path1, image_path2, pos, scale_factor)
        self.click_listener_list = []  # Initialize click listener list

    def click(self):
        """Handle click on three player button"""
        global current_screen
        print("Creating ThreePlayerScreen...")  # Debug print
        current_screen = ThreePlayerScreen()


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
        pygame.quit()


class DeckLabel(ClickableLabel):
    def click(self):
        global current_screen


class Card(RenderableImage):
    def __init__(self, color, number, position2d=(0, 0), scale2d=(0.15, 0.15), rotation2d=(1, 0)):
        # For face-up cards
        self.face_up_image = f"resources/images/cards/{color}_{number}.png"
        # For face-down cards
        self.face_down_image = "resources/images/cards/backside_card.png"
        # Start with face-down image
        image_path = self.face_down_image
        self.logic_card = None

        super().__init__(image_path, position2d, scale2d, rotation2d)
        self.color = color
        self.number = number
        self.selected = False  # For selection state
        self.highlighted = False  # For opponent's cards
        self.is_face_up = False
        self.is_raised = False  # New property for raised state
        self.hover_offset = 0
        self.HOVER_DISTANCE = -20  # Distance to raise card
        self.RAISED_HORIZONTAL_OFFSET = 20  # Additional horizontal spacing for raised cards

        self.rect = pygame.Rect(position2d[0] - CARD_WIDTH / 2,
                                position2d[1] - CARD_HEIGHT / 2,
                                CARD_WIDTH, CARD_HEIGHT)

    def flip(self):
        """Flip the card face up/down"""
        self.is_face_up = not self.is_face_up
        self.image_src = self.face_up_image if self.is_face_up else self.face_down_image
        self._store_cache()

    def set_face_up(self):
        """Set the card to face up"""
        if not self.is_face_up:
            self.is_face_up = True
            self.image_src = self.face_up_image
            self._store_cache()

    def set_face_down(self):
        """Set the card to face down"""
        if self.is_face_up:
            self.is_face_up = False
            self.image_src = self.face_down_image
            self._store_cache()

    def update(self):
        """Update card state"""
        # Only update hover offset based on raised state
        if self.is_raised:
            self.hover_offset = self.HOVER_DISTANCE
        else:
            self.hover_offset = 0
            # Update rect position
        if self.position2d:
            offset2d = math_util.rotate_vec2d(self.rotation2d, (0, self.hover_offset))
            base_pos = math_util.vec_2d_plus(self.position2d, offset2d)
            self.rect.x = base_pos[0] - CARD_WIDTH / 2
            self.rect.y = base_pos[1] - CARD_HEIGHT / 2

    def toggle_raised(self):
        """Toggle the raised state of the card"""
        self.is_raised = not self.is_raised
        self.update()

    def update_position(self, new_pos, animation_layer=0):
        """Update both the display position and collision rect"""
        old_pos = self.position2d
        # self.position2d = new_pos
        hover_adjusted_pos = (new_pos[0], new_pos[1] + self.hover_offset)
        self.rect.x = hover_adjusted_pos[0] - CARD_WIDTH / 3
        self.rect.y = hover_adjusted_pos[1] - CARD_HEIGHT / 2.8
        # Animation Magic Touch Here
        if animation_layer in (0, 1, 2):
            animation.play_animation(self, move_to("position2d", old_pos, new_pos, 0.2), animation_layer)

    def update_rotation(self, new_rot, animation_layer=1):
        old_rot = self.rotation2d
        # self.rotation2d = new_rot
        if animation_layer in [0, 1, 2]:
            if abs(math_util.vec_2d_dot(math_util.vec_2d_plus(old_rot, new_rot), (1, 1))) > 0.001:
                animation.play_animation(self, ease_in_out_2d("rotation2d", old_rot, new_rot, 0.2),
                                         layer=animation_layer)
            else:
                middle_rot = (old_rot[1], -old_rot[0])

                scale_animation_sequence = AnimationSequenceTask(loop=False)

                animation_task_1 = move_to("rotation2d", old_rot, middle_rot, 0.1)
                animation_task_2 = move_to("rotation2d", middle_rot, new_rot, 0.1)

                scale_animation_sequence.add_sub_task(animation_task_1)
                scale_animation_sequence.add_sub_task(animation_task_2)

                animation.play_animation(self, scale_animation_sequence, layer=1)

    def contains_point(self, pos):
        """Check if a point is within the card's clickable area"""
        # Using expanded hitbox for better detection, especially for stacked cards
        # Comment: I deeply doubt about that...
        # expanded_rect = self.rect.inflate(-10, -10)  # Increased from 10,10 to 20,20
        x = self.image.get_size()[0] * self.scale2d[0]
        y = self.image.get_size()[1] * self.scale2d[1]
        card_pos = self.position2d
        return card_pos[0] - x * 0.5 < pos[0] < card_pos[0] + x * 0.5 and card_pos[1] - y * 0.5 < pos[1] < card_pos[
            1] + y * 0.5
        # return expanded_rect.collidepoint(pos)

    def draw(self, screen):
        """Draw the card with highlighting if selected"""
        offset2d = math_util.rotate_vec2d(self.rotation2d, (0, self.hover_offset))
        hover_adjusted_pos = math_util.vec_2d_plus(self.position2d, offset2d)

        if self.highlighted or self.selected:
            angle = math_util.rotation_to_euler_angle(self.rotation2d)

            if abs(angle) == 90:  # For left/right players
                # Smaller highlight for side players
                highlight = pygame.Surface((CARD_WIDTH + 2, CARD_HEIGHT + 2))
                highlight.set_alpha(150)

                if self.highlighted:
                    highlight.fill((147, 112, 219))
                else:
                    highlight.fill((255, 140, 0))

                # Rotate highlight to match card orientation
                highlight = pygame.transform.rotate(highlight, angle)
                highlight_rect = highlight.get_rect(center=hover_adjusted_pos)
                screen.blit(highlight, highlight_rect.topleft)
            else:  # For bottom player and 2-player game
                # Original highlight size
                highlight = pygame.Surface((CARD_WIDTH + 2, CARD_HEIGHT + 2))
                highlight.set_alpha(150)

                if self.highlighted:
                    highlight.fill((147, 112, 219))
                else:
                    highlight.fill((255, 140, 0))

                highlight_x = hover_adjusted_pos[0] - (CARD_WIDTH + 4) / 2
                highlight_y = hover_adjusted_pos[1] - (CARD_HEIGHT + 4) / 2
                screen.blit(highlight, (highlight_x, highlight_y))

        original_pos = self.position2d
        self.position2d = hover_adjusted_pos
        super().draw(screen)
        self.position2d = original_pos


class Player(core.IPlayerAgentListener):
    def __init__(self, position, cards=None):
        self.position = position  # 'bottom', 'top', 'left', or 'right'
        self.cards = cards if cards else []
        self.selected_cards = []
        self.stacked_cards = []  # Track which cards are in the stack
        self._logic_player = None
        self.game_state = None
        self.hovered_card = None

    @property
    def logic_player(self):
        return self._logic_player

    @logic_player.setter
    def logic_player(self, logic_player: core.PlayerAgent):
        # automatically make player a listener
        logic_player.add_action_listener(self)
        self._logic_player = logic_player

    def add_card(self, card):
        """Add a card to player's hand"""
        self.cards.append(card)
        if not card.is_face_up:
            card.is_face_up = True
            card.flip()
        # self.update_card_positions()

    def remove_card(self, card):
        """Remove a card from player's hand"""
        if card in self.cards:
            self.cards.remove(card)
            if card in self.selected_cards:
                self.selected_cards.remove(card)
            if card in self.stacked_cards:
                self.stacked_cards.remove(card)
            if self.hovered_card == card:
                self.hovered_card = None
            # self.update_card_positions()

    def update_card_positions(self):
        """Update positions of all cards in hand"""
        if not self.cards:
            return

        stacked = len(self.cards) > 5

        # Clear stacked cards at the start of update
        self.stacked_cards.clear()

        # Update all cards
        for card in self.cards:
            card.update()

        if self.position in ['bottom', 'top']:
            self._arrange_horizontal(stacked)
        else:
            self._arrange_vertical(stacked)

    def _arrange_horizontal(self, stacked):
        """Arrange cards horizontally (for bottom and top players)"""
        left_padding = 150
        right_padding = 150
        available_width = WINDOW_WIDTH - left_padding - right_padding

        # Calculate spacing
        spacing = available_width / (len(self.cards) - 1) if len(self.cards) > 1 else 0

        # Determine starting x position and base y position
        if (self.position == 'bottom' or self.position == 'top') and len(self.cards) < 5:
            spacing = 1.4 * CARD_WIDTH
            total_width = (len(self.cards) - 1) * CARD_WIDTH
            start_x = (WINDOW_WIDTH - total_width) / 2
        else:
            start_x = left_padding

        base_y = WINDOW_HEIGHT - (CARD_HEIGHT * 1.05) if self.position == 'bottom' else CARD_HEIGHT / 1.35

        # Position cards
        for i, card in enumerate(self.cards):
            x = start_x + i * spacing
            # If the card is selected, raise it by 1/3 of its height

            if self.position == 'bottom':
                y = base_y - (CARD_HEIGHT / 3) if card.selected else base_y
            else:
                y = base_y + (CARD_HEIGHT / 3) if card.selected else base_y

            card.update_position((x, y))
            if self.position == 'top':
                card.update_rotation(math_util.euler_angle_to_rotation(180))
            else:
                card.update_rotation(math_util.euler_angle_to_rotation(0))

    def _arrange_vertical(self, stacked):
        top_padding = 100
        bottom_padding = 220
        available_width = WINDOW_HEIGHT - top_padding - bottom_padding

        if len(self.cards) < 5:
            spacing = CARD_HEIGHT * 0.8
            total_height = (len(self.cards) - 1) * spacing + CARD_HEIGHT  # Total height including all cards
            base_y = (WINDOW_HEIGHT - total_height) / 2

        else:
            spacing = available_width / (len(self.cards) - 1) if len(self.cards) > 1 else 0
            base_y = top_padding

        if self.position == 'left':
            start_x = CARD_WIDTH / 1.05
        else:
            start_x = WINDOW_WIDTH - (CARD_WIDTH * 0.95)

        # Position cards
        for i, card in enumerate(self.cards):
            if self.position == 'left':
                x = start_x + (CARD_HEIGHT / 3) if card.selected else start_x
            else:
                x = start_x - (CARD_HEIGHT / 3) if card.selected else start_x
            y = base_y + i * spacing

            # Update pos
            card.update_position((x, y))

            # card rotation
            if self.position == 'left':
                card.update_rotation(math_util.euler_angle_to_rotation(-90))
            else:
                card.update_rotation(math_util.euler_angle_to_rotation(90))

    def flip_all_cards(self, face_up: bool = False):
        if not face_up:
            for card in self.cards:
                card.set_face_down()
        else:
            for card in self.cards:
                card.set_face_up()

    def handle_click(self, pos):
        """Handle clicking on a card in player's hand"""
        # Reverse the cards list to check from front to back
        for card in reversed(self.cards):
            if card.contains_point(pos):
                return card
        return None

    # IPlayerAgentListener implementation methods
    def draw_start_cards(self, job):
        pass

    def start_turn(self, job):
        job.add_start_evoke_listener(self.game_state.start_turn)

    def start_draw_from_deck(self, job):
        def toggle_draw_mode():
            if not self.game_state.draw_mode_active:
                self.game_state.toggle_draw_mode()
                print(f"player {self} draw from deck")

        job.add_start_evoke_listener(toggle_draw_mode)

    def draw_card_from_deck(self, job):
        job.add_start_evoke_listener(self.game_state.draw_single_card)

    def end_draw_card_from_deck(self, job):
        job.add_start_evoke_listener(self.game_state.confirm_drawn_cards_start)
        job.add_end_evoke_listener(self.game_state.confirm_drawn_cards_end)

    def select_card(self, card, job):
        def select_collection_card():
            visual_card = self.game_state.logic_card_to_visual_card(card)
            self.game_state.select_card(visual_card)

        def on_card_selected():
            visual_card = self.game_state.logic_card_to_visual_card(card)
            if self.game_state.draw_mode_active:
                # In draw mode, force cards to stay down and just handle selection
                visual_card.is_raised = False
                visual_card.hover_offset = 0
                self.update_card_positions()
            else:
                # For normal mode, check if card is in stack
                if visual_card in self.stacked_cards:
                    if visual_card.selected:
                        visual_card.is_raised = True
                        visual_card.hover_offset = visual_card.HOVER_DISTANCE
                    else:
                        visual_card.is_raised = False
                        visual_card.hover_offset = 0
                else:
                    # For non-stacked cards, just toggle selection
                    visual_card.is_raised = False
                    visual_card.hover_offset = 0
                self.update_card_positions()

        job.add_start_evoke_listener(select_collection_card)
        job.add_start_evoke_listener(on_card_selected)

    def deselect_card(self, card, job):
        def deselect_collection_card():
            visual_card = self.game_state.logic_card_to_visual_card(card)
            self.game_state.deselect_card(visual_card)

        def on_card_deselected():
            visual_card = self.game_state.logic_card_to_visual_card(card)
            if self.game_state.draw_mode_active:
                # In draw mode, force cards to stay down and just handle selection
                visual_card.is_raised = False
                visual_card.hover_offset = 0
                self.update_card_positions()
            else:
                # For normal mode, check if card is in stack
                if visual_card in self.stacked_cards:
                    if visual_card.selected:
                        visual_card.is_raised = True
                        visual_card.hover_offset = visual_card.HOVER_DISTANCE
                    else:
                        visual_card.is_raised = False
                        visual_card.hover_offset = 0
                else:
                    # For non-stacked cards, just toggle selection
                    visual_card.is_raised = False
                    visual_card.hover_offset = 0
                self.update_card_positions()

        job.add_start_evoke_listener(deselect_collection_card)
        job.add_start_evoke_listener(on_card_deselected)

    def dispose_selected(self, job):
        job.add_start_evoke_listener(self.game_state.discard_selected_cards)

    def pass_turn(self, job):
        job.add_start_evoke_listener(self.game_state.end_turn)
        job.add_start_evoke_listener(self.game_state.flip_up_all_card)

    def start_draw_from_other_player(self, other_player, job):
        job.add_start_evoke_listener(self.game_state.toggle_take_opponent_mode)

        def flip_down_all_card():
            visual_other_player = self.game_state.logic_player_to_visual_player(other_player)
            for card in visual_other_player.cards:
                card.is_raised = False
                card.hover_offset = 0
                card.selected = False
                card.set_face_down()
            random.shuffle(visual_other_player.cards)
            visual_other_player.update_card_positions()

        job.add_start_evoke_listener(flip_down_all_card)

    def select_from_other_player(self, other_player, card, job):

        def select_other_player_card():
            visual_card = self.game_state.logic_card_to_visual_card(card)
            self.game_state.select_other_player_card(visual_card)

        job.add_start_evoke_listener(select_other_player_card)

    def draw_from_other_player(self, other_player, card, job):
        def flip_up_card():
            visual_other_player = self.game_state.logic_player_to_visual_player(other_player)
            visual_card = self.game_state.logic_card_to_visual_card(card)
            visual_card.set_face_up()
            visual_other_player.update_card_positions()

        job.add_start_evoke_listener(flip_up_card)

    def end_draw_from_other_player(self, job):
        def flip_up_all_card():
            for player in self.game_state.players:
                for card in player.cards:
                    card.is_raised = False
                    card.hover_offset = 0
                    card.selected = False
                    card.set_face_up()

        job.add_start_evoke_listener(self.game_state.take_opponent_card)
        job.add_start_evoke_listener(flip_up_all_card)


class HumanPlayerInput(core.PlayerInput):
    def __init__(self):
        super().__init__()
        self.valid_group_memory = None
        self.other_player_memory = None

    def activate(self):
        super().activate()
        print("HumanPlayerInput Activated")

    def deactivate(self):
        super().deactivate()
        print("HumanPlayerInput Deactivated")

    def pass_turn(self):
        if not self.active:
            return
        self.player.pass_turn()

    def start_draw_from_other_player(self, other_player):
        if not self.active:
            return
        if self.player.card_count() < 20:
            self.player.start_draw_from_other_player(other_player)
            self.other_player_memory = other_player

    def select_from_other_player(self, card):
        if not self.active:
            return
        self.player.select_from_other_player(self.other_player_memory, card)

    def draw_from_other_player(self):
        if not self.active:
            return
        job = self.player.draw_from_other_player(self.other_player_memory)
        job.add_end_evoke_listener(self.player.end_draw_from_other_player)  # draw, and immediately end

    def start_draw_from_deck(self):
        if not self.active:
            return
        self.player.start_draw_from_deck()

    def draw_card_from_deck(self):
        if not self.active:
            return
        player_status = self.player.game_manager.get_player_status(self.player)
        if player_status.num_card_drawn_from_deck < 3 and self.player.card_count() < 20:
            self.player.draw_card_from_deck()

    def end_draw_card_from_deck(self):
        if not self.active:
            return
        self.player.end_draw_card_from_deck()

    def select_card(self, card):
        if not self.active:
            return
        self.player.select_card(card)

    def deselect_card(self, card):
        if not self.active:
            return
        self.player.deselect_card(card)

    def dispose_selected(self):
        if not self.active:
            return
        if self.player.selected_valid_group():
            self.player.dispose_selected()
        else:
            debug_string = ""
            for card in self.player.selected_as_list():
                debug_string += str(card) + " "
            print(f"{debug_string} is not a valid group")


def list_diff(old_list, new_list):
    diff_in = [card for card in new_list if not card in old_list]
    diff_out = [card for card in old_list if not card in new_list]
    return diff_in, diff_out


class GameState:
    def __init__(self, num_players=2):
        self.game_logic_server = None
        self.game_manager = None
        self.human_input = None
        self._init_game_manager(num_players)

        self.logic_card_to_card_mapping = {}
        self.logic_player_to_player_mapping = {}

        self.players = []
        self.current_player = -1
        self.deck = self._create_deck()
        self._init_players(num_players)
        self.start_draw_initial_card()

        self.selected_opponent_card = None
        self.has_drawn_this_turn = False
        self.has_taken_player_card_this_turn = False
        self.num_players = num_players
        self.draw_mode_active = False
        self.cards_drawn_this_turn = 0
        self.deck_highlighted = False
        self.animation_in_progress = False
        self.drawn_cards = []  # Store temporarily drawn cards
        self.drawn_card_positions = []  # Store positions for drawn cards

    def logic_card_to_visual_card(self, logic_card):
        return self.logic_card_to_card_mapping[logic_card]

    def logic_player_to_visual_player(self, logic_player):
        return self.logic_player_to_player_mapping[logic_player]

    def _init_game_manager(self, num_players):
        self.game_logic_server = core.Game()
        self.game_manager = self.game_logic_server.game_manager
        for i in range(num_players):
            if i == 0:
                human_player_input = HumanPlayerInput()
                self.human_input = human_player_input
                last_player = core.PlayerAgent(self.game_manager, human_player_input)
            else:
                last_player = core.PlayerAgent(self.game_manager, core.AIPlayerInput())
            self.game_manager.add_player(last_player)
        self.game_manager.add_game_result_listener(self.check_winner)

    def start_draw_initial_card(self):
        job = None
        for player in self.players:
            logic_player = player.logic_player
            job = logic_player.draw_start_cards()
            job.add_start_evoke_listener(self.on_draw_initial_5_card_to_player_wrapper(player))
            print(f"logic_player:{logic_player}")
        job.add_end_evoke_listener(self.game_manager.start_next_player_turn)

    def on_draw_initial_5_card_to_player_wrapper(self, player):
        def on_draw_initial_5_card_to_player():
            self._sync_player_card(player)
            self._sync_deck_card()
            player.update_card_positions()

        return on_draw_initial_5_card_to_player

    def _create_deck(self):
        deck = []
        logic_cards = self.game_manager.deck.card_as_list()
        for logic_card in logic_cards:
            visual_card = Card(logic_card.color, logic_card.number)
            visual_card.set_face_down()
            visual_card.logic_card = logic_card
            visual_card.position2d = (WINDOW_WIDTH * 0.5, WINDOW_HEIGHT * 0.5)
            self.logic_card_to_card_mapping[logic_card] = visual_card
            deck.append(visual_card)
        print(f"Deck Created {len(deck)} cards")
        return deck

    def _sync_deck_card(self):
        logic_deck_cards = self.game_manager.deck.card_as_list()
        self.deck = [self.logic_card_to_card_mapping[logic_card] for logic_card in logic_deck_cards]

    def _sync_player_card(self, player):
        logic_player = player.logic_player
        logic_hand_cards = logic_player.card_as_list()
        new_cards = [self.logic_card_to_card_mapping[logic_card] for logic_card in logic_hand_cards]
        diff_in = [card for card in new_cards if not card in player.cards]
        diff_out = [card for card in player.cards if not card in new_cards]
        for card in diff_out:
            player.remove_card(card)
        for card in diff_in:
            player.add_card(card)
            card.set_face_up()
        return diff_in, diff_out

    def _sync_player_selected_card(self, player):
        logic_player = player.logic_player
        logic_selected_cards = logic_player.selected_as_list()
        new_cards = [self.logic_card_to_card_mapping[logic_card] for logic_card in logic_selected_cards]
        old_cards = player.selected_cards
        diff_in, diff_out = list_diff(old_cards, new_cards)
        for card in diff_out:
            player.selected_cards.remove(card)
            card.selected = False
        for card in diff_in:
            player.add_card(card)
            card.selected = True

    def _sync_player_turn(self):
        self.current_player = self.game_manager.player_turn

    def _init_players(self, num_players):
        positions = ['bottom', 'top'] if num_players == 2 else ['bottom', 'left', 'right']
        logic_players = self.game_manager.players
        for i in range(num_players):
            position = positions[i]
            logic_player = logic_players[i]
            player = Player(position, [])
            self.players.append(player)
            player.update_card_positions()
            player.logic_player = logic_player
            player.game_state = self
            self.logic_player_to_player_mapping[logic_player] = player

    def toggle_draw_mode(self):
        """Toggle draw mode on/off"""
        if not self.has_taken_player_card_this_turn and not self.has_drawn_this_turn and self.cards_drawn_this_turn < 3:
            self.draw_mode_active = not self.draw_mode_active
            if self.draw_mode_active and isinstance(current_screen, TwoPlayerScreen) or isinstance(current_screen,
                                                                                                   ThreePlayerScreen):
                current_screen.buttons['drawfromdeck'].enabled = not self.draw_mode_active
            self.deck_highlighted = self.draw_mode_active

            # Clear drawn cards when exiting draw mode
            if not self.draw_mode_active:
                self.drawn_cards = []
                self.drawn_card_positions = []
        else:
            self.draw_mode_active = False
            self.deck_highlighted = False

        # Ensure cards are properly positioned after mode change
        for player in self.players:
            player.update_card_positions()

    def toggle_take_opponent_mode(self):
        pass

    def draw_single_card(self):
        if (self.draw_mode_active and
                len(self.drawn_cards) < 3 and
                self.deck and
                not self.animation_in_progress):
            old_logic_cards = [card.logic_card for card in self.drawn_cards]
            new_logic_cards = self.game_manager.draw_card_buffer.card_as_list()
            diff_in, diff_out = list_diff(old_logic_cards, new_logic_cards)
            assert len(diff_in) == 1
            card = self.logic_card_to_card_mapping[diff_in[0]]
            print(f'{card.logic_card} draw from the deck to buffer')
            card.set_face_down()

            deck_x = WINDOW_WIDTH / 1.85
            deck_y = WINDOW_HEIGHT / 1.85
            offset_x = CARD_WIDTH + 15

            card_x = (WINDOW_WIDTH / 1.5) - offset_x - (len(self.drawn_cards) * (CARD_WIDTH + 20))
            card_y = WINDOW_HEIGHT / 3.4

            card.update_position((card_x, card_y))
            self.drawn_cards.append(card)
            self.drawn_card_positions.append((card_x, card_y))

            return True
        return False

    def confirm_drawn_cards_start(self):
        if self.drawn_cards:
            for card in self.drawn_cards:
                card.set_face_up()

    def confirm_drawn_cards_end(self):
        if self.drawn_cards:
            current_player = self.players[self.current_player]
            for card in self.drawn_cards:
                current_player.add_card(card)

            self._sync_deck_card()
            diff_in, diff_out = self._sync_player_card(current_player)
            assert len(diff_in) == 0 and len(diff_out) == 0

            self.cards_drawn_this_turn = len(self.drawn_cards)
            self.drawn_cards = []
            self.drawn_card_positions = []

            if self.cards_drawn_this_turn > 0:
                self.has_drawn_this_turn = True
                self.draw_mode_active = False
                self.deck_highlighted = False

            current_player.update_card_positions()

    def clear_highlights(self):
        if self.selected_opponent_card:
            self.selected_opponent_card.highlighted = False
            self.selected_opponent_card = None

        for player in self.players:
            for card in player.cards:
                card.highlighted = False

    def flip_down_all_card(self, player):
        visual_other_player = player
        for card in visual_other_player.cards:
            card.is_raised = False
            card.hover_offset = 0
            card.selected = False
            card.set_face_down()
        random.shuffle(visual_other_player.cards)
        visual_other_player.update_card_positions()

    def flip_up_all_card(self):
        for player in self.players:
            for card in player.cards:
                card.is_raised = False
                card.hover_offset = 0
                card.selected = False
                card.set_face_up()

    def is_valid_sequence(self, cards):
        if len(cards) < 3:
            return False

        color = cards[0].color
        if not all(card.color == color for card in cards):
            return False

        numbers = sorted(card.number for card in cards)
        return all(numbers[i] + 1 == numbers[i + 1] for i in range(len(numbers) - 1))

    def is_valid_set(self, cards):
        if len(cards) < 3:
            return False

        number = cards[0].number
        if not all(card.number == number for card in cards):
            return False

        colors = [card.color for card in cards]
        return len(colors) == len(set(colors))

    def is_valid_group(self, cards):
        return self.is_valid_sequence(cards) or self.is_valid_set(cards)

    def select_other_player_card(self, card: Card):
        if isinstance(card, core.Card):
            card = self.logic_card_to_card_mapping[card]
        if self.selected_opponent_card:
            self.selected_opponent_card.highlighted = False
        self.selected_opponent_card = card
        card.highlighted = True
        print(f"select_other_player_card(self, {card})")

    def handle_click(self, pos):
        for i, player in enumerate(self.players):
            if i != self.current_player:
                clicked_card = player.handle_click(pos)
                if clicked_card:
                    if self.selected_opponent_card:
                        self.selected_opponent_card.highlighted = False
                    self.selected_opponent_card = clicked_card
                    clicked_card.highlighted = True
                    return True

        current_player = self.players[self.current_player]
        clicked_card = current_player.handle_click(pos)
        if clicked_card:
            if clicked_card.selected:
                print(f"card clicked: {clicked_card}")
            else:
                print(f"card clicked: {clicked_card}")
            return True
        return False

    def select_card(self, card):
        current_player = self.players[self.current_player]
        if card not in current_player.cards:
            raise ValueError(f"{card} does not exist in current player")
        card.selected = True
        current_player.selected_cards.append(card)
        print(f"Card {card} selected")

    def deselect_card(self, card):
        current_player = self.players[self.current_player]
        if card not in current_player.cards:
            raise ValueError(f"{card} does not exist in current player")
        card.selected = False
        if card in current_player.selected_cards:
            current_player.selected_cards.remove(card)
        else:
            print("This branch should not be executed")
        print(f"Card {card} deselected")

    def take_opponent_card(self):
        if self.selected_opponent_card:
            for player in self.players:
                if self.selected_opponent_card in player.cards:
                    print("TAKE OPPONENT CARD")
                    diff_in, diff_out = self._sync_player_card(player)
                    print(f"diff in:{len(diff_in)}, diff out:{len(diff_out)}")
                    print(f'len old:{len(player.cards)}, len new:{player.logic_player.card_count()}')
                    assert len(diff_out) == 1
                    self.selected_opponent_card.is_face_up = True
                    current_player = self.players[self.current_player]
                    diff_in, diff_out = self._sync_player_card(current_player)
                    assert len(diff_in) == 1
                    self.selected_opponent_card.highlighted = False
                    self.selected_opponent_card = None
                    player.update_card_positions()
                    current_player.update_card_positions()
                    return True
        return False

    def discard_cards(self, cards):
        current_player = self.players[self.current_player]
        self._sync_player_card(current_player)
        for card in cards:
            current_player.remove_card(card)
            card.set_face_down()
        self._sync_deck_card()
        random.shuffle(self.deck)
        current_player.update_card_positions()
        return True

    def discard_selected_cards(self):
        current_player = self.players[self.current_player]
        diff_in, diff_out = self._sync_player_card(current_player)
        assert len(diff_in) == 0
        cards = diff_out
        for card in cards:
            card.set_face_down()
            card.selected = False
            card.hover_offset = 0
            card.is_raised = False
            card.highlighted = False
            card.update_position((WINDOW_WIDTH * 0.5, WINDOW_HEIGHT * 0.5))
            card.update_rotation((1, 0))
        self._sync_deck_card()
        random.shuffle(self.deck)
        current_player.update_card_positions()
        print(f"{cards} discarded")
        return True

    def start_turn(self):
        self._sync_player_turn()
        print(f"Started {self.current_player}'s turn")
        if isinstance(current_screen, ThreePlayerScreen) or isinstance(current_screen, TwoPlayerScreen):
            if self.current_player == 0:
                current_screen.resume_buttons()

    def end_turn(self):
        self.draw_mode_active = False
        self.deck_highlighted = False
        self.cards_drawn_this_turn = 0
        self.has_drawn_this_turn = False

        self.drawn_cards = []
        self.drawn_card_positions = []

        for player in self.players:
            self._sync_player_card(player)
            self._sync_player_selected_card(player)
            # for card in player.selected_cards:
            #     card.selected = False
            # player.selected_cards.clear()
        self._sync_deck_card()

        # current_player = self.players[self.current_player]
        # for card in current_player.selected_cards:
        #     card.selected = False
        # current_player.selected_cards.clear()

        if self.selected_opponent_card:
            self.selected_opponent_card.highlighted = False
            self.selected_opponent_card = None

        for player in self.players:
            player.update_card_positions()

        if isinstance(current_screen, ThreePlayerScreen):
            current_screen.active_opponent = None
            print("Reset Active opponent")
        if isinstance(current_screen, TwoPlayerScreen) or isinstance(current_screen, ThreePlayerScreen):
            current_screen.hide_buttons()

    def draw(self, screen):
        for player in self.players:
            for card in player.cards:
                card.draw(screen)

        for card in self.drawn_cards:
            card.draw(screen)

    def check_winner(self, player):
        """Check if there's a winner (player with no cards)"""
        visual_player = self.logic_player_to_visual_player(player)
        human_player = self.players[0]
        global current_screen
        if visual_player == human_player:
            current_screen = CongratsScreen()
        else:
            current_screen = LoseScreen()
        return None


class ScreenBase:
    def __init__(self, background_filename=None):
        self.objects = []

        if background_filename is not None:
            if os.path.exists(background_filename):
                self.background_image = pygame.image.load(background_filename)
                # self.background_image = pygame.transform.smoothscale(self.background_image, (800, 600))
                self.background_image = pygame.transform.smoothscale(self.background_image, (900, 675))
            else:
                print(f"Warning: Background image {background_filename} not found.")
                self.background_image = None
        else:
            self.background_image = None

    def draw(self, screen):
        if self.background_image is not None:
            screen.blit(self.background_image, (0, 0))
        else:
            screen.fill((0, 0, 0))

        for o in self.objects:
            o.draw(screen)

    def update(self):
        for o in self.objects:
            o.update()

    def keydown(self, event):
        pass

    def mouseup(self, event):
        for o in self.objects:
            o.mouseup(event)


class StartScreen(ScreenBase):

    def __init__(self):
        super().__init__(background_filename="resources/images/ui/screens/StartScreenObject/Rectangle.png")
        self.start_time = pygame.time.get_ticks()
        self.transition_delay = 6000

        # Animation Time!
        rotation_identity = math_util.euler_angle_to_rotation(0)
        bg_ratio = bg_ratio = WINDOW_HEIGHT / 3546
        pos_1 = (499 * bg_ratio, 1049 * bg_ratio)  # card red 9
        pos_2 = (668 * bg_ratio, 777 * bg_ratio)  # card red 10
        pos_3 = (971 * bg_ratio, 849 * bg_ratio)  # card red 8
        pos_4 = (1156 * bg_ratio, 545 * bg_ratio)  # card red 7
        pos_5 = (1560 * bg_ratio, 593 * bg_ratio)  # card red 6
        pos_6 = (3096 * bg_ratio, 625 * bg_ratio)
        pos_7 = (3462 * bg_ratio, 689 * bg_ratio)
        pos_8 = (3825 * bg_ratio, 810 * bg_ratio)  # card yellow 4
        pos_9 = (4137 * bg_ratio, 945 * bg_ratio)
        pos_10 = (1972 * bg_ratio, 2729 * bg_ratio)
        pos_11 = (2356 * bg_ratio, 2641 * bg_ratio)
        pos_12 = (2705 * bg_ratio, 2740 * bg_ratio)

        card_red_1 = RenderableImage("resources/images/ui/screens/StartScreenObject/Object 1 (4).png", position2d=pos_1,
                                     scale2d=(bg_ratio, bg_ratio),
                                     rotation2d=rotation_identity)
        card_red_2 = RenderableImage("resources/images/ui/screens/StartScreenObject/Object 1 (3).png", position2d=pos_2,
                                     scale2d=(bg_ratio, bg_ratio),
                                     rotation2d=rotation_identity)
        card_red_3 = RenderableImage("resources/images/ui/screens/StartScreenObject/Object 1 (2).png", position2d=pos_3,
                                     scale2d=(bg_ratio, bg_ratio),
                                     rotation2d=rotation_identity)
        card_red_4 = RenderableImage("resources/images/ui/screens/StartScreenObject/Object 1.png", position2d=pos_4,
                                     scale2d=(bg_ratio, bg_ratio),
                                     rotation2d=rotation_identity)
        card_red_5 = RenderableImage("resources/images/ui/screens/StartScreenObject/Object 1 (1).png", position2d=pos_5,
                                     scale2d=(bg_ratio, bg_ratio),
                                     rotation2d=rotation_identity)
        card_red_6 = RenderableImage("resources/images/ui/screens/StartScreenObject/Object 1 (8).png", position2d=pos_6,
                                     scale2d=(bg_ratio, bg_ratio),
                                     rotation2d=rotation_identity)
        card_red_7 = RenderableImage("resources/images/ui/screens/StartScreenObject/Object 1 (7).png", position2d=pos_7,
                                     scale2d=(bg_ratio, bg_ratio),
                                     rotation2d=rotation_identity)
        card_red_8 = RenderableImage("resources/images/ui/screens/StartScreenObject/Object 1 (6).png", position2d=pos_8,
                                     scale2d=(bg_ratio, bg_ratio),
                                     rotation2d=rotation_identity)
        card_red_9 = RenderableImage("resources/images/ui/screens/StartScreenObject/Object 1 (5).png", position2d=pos_9,
                                     scale2d=(bg_ratio, bg_ratio),
                                     rotation2d=rotation_identity)

        title_image = RenderableImage("resources/images/ui/screens/StartScreenObject/NottyGame.png",
                                      position2d=(WINDOW_WIDTH * 0.5, WINDOW_HEIGHT * 0.5),
                                      scale2d=(bg_ratio, bg_ratio),
                                      rotation2d=rotation_identity)

        card_yellow_1 = RenderableImage("resources/images/ui/screens/StartScreenObject/Object 1 (10).png",
                                        position2d=pos_10, scale2d=(bg_ratio, bg_ratio),
                                        rotation2d=rotation_identity)
        card_yellow_2 = RenderableImage("resources/images/ui/screens/StartScreenObject/Object 1 (11).png",
                                        position2d=pos_11, scale2d=(bg_ratio, bg_ratio),
                                        rotation2d=rotation_identity)
        card_yellow_3 = RenderableImage("resources/images/ui/screens/StartScreenObject/Object 1 (12).png",
                                        position2d=pos_12, scale2d=(bg_ratio, bg_ratio),
                                        rotation2d=rotation_identity)

        self.objects.append(card_red_1)
        self.objects.append(card_red_2)
        self.objects.append(card_red_3)
        self.objects.append(card_red_4)
        self.objects.append(card_red_5)
        self.objects.append(card_red_6)
        self.objects.append(card_red_7)
        self.objects.append(card_red_8)
        self.objects.append(card_red_9)
        self.objects.append(title_image)
        self.objects.append(card_yellow_1)
        self.objects.append(card_yellow_2)
        self.objects.append(card_yellow_3)

        start_screen_upper_group = [card_red_1, card_red_2, card_red_3, card_red_4, card_red_5, card_red_6, card_red_7,
                                    card_red_8, card_red_9]
        start_screen_lower_group = [card_yellow_1, card_yellow_2, card_yellow_3]
        start_screen_group = [card_red_1, card_red_2, card_red_3, card_red_4, card_red_5, card_red_6, card_red_7,
                              card_red_8, card_red_9, title_image, card_yellow_1, card_yellow_2, card_yellow_3]

        central_point = (WINDOW_HEIGHT * 0.5, WINDOW_HEIGHT)
        pretime = 0
        posttime = 2
        for card in start_screen_upper_group:
            # calc the motion offset for each card
            offset = math_util.vec_2d_mul(
                math_util.normalize_vec2d(math_util.vec_2d_minus(card.position2d, central_point)), 10)
            end_pos = math_util.vec_2d_plus(card.position2d, offset)
            pretime += 0.1
            posttime -= 0.1
            animation.play_animation(card,
                                     hop_with_overshoot_sequence("position2d", card.position2d, offset, pretime,
                                                                 posttime))

            card.scale2d = (0, 0)
            scale_animation_sequence = AnimationSequenceTask(loop=False)

            animation_task_1 = constant_2d("scale2d", (0, 0), pretime + 1)
            animation_task_2 = overshoot_2d("scale2d", (0, 0), (bg_ratio, bg_ratio), 0.5, overshoot=0.6)
            animation_task_3 = constant_2d("scale2d", (bg_ratio, bg_ratio), posttime)

            scale_animation_sequence.add_sub_task(animation_task_1)
            scale_animation_sequence.add_sub_task(animation_task_2)
            scale_animation_sequence.add_sub_task(animation_task_3)

            animation.play_animation(card, scale_animation_sequence, layer=1)

        animation.play_animation(title_image, ping_pong("scale2d", (0.17, 0.17), (bg_ratio, bg_ratio), 2))
        title_image.alpha = 0

        alpha_animation_sequence = AnimationSequenceTask(loop=False)
        alpha_animation_sequence.add_sub_task(constant_1d("alpha", 0, 2))
        alpha_animation_sequence.add_sub_task(ease_in_out_1d("alpha", 0, 255, 2))
        alpha_animation_sequence.add_sub_task(constant_1d("alpha", 255, 3))

        animation.play_animation(title_image, alpha_animation_sequence, layer=1)
        animation.play_animation(card_yellow_1, hop_with_overshoot_sequence("rotation2d", card_yellow_1.rotation2d,
                                                                            math_util.euler_angle_to_rotation(5), 0, 4,
                                                                            hop_time=0.7))
        animation.play_animation(card_yellow_2, hop_with_overshoot_sequence("rotation2d", card_yellow_2.rotation2d,
                                                                            math_util.euler_angle_to_rotation(-10), 0,
                                                                            4, hop_time=0.7))
        animation.play_animation(card_yellow_3, hop_with_overshoot_sequence("rotation2d", card_yellow_3.rotation2d,
                                                                            math_util.euler_angle_to_rotation(-15), 0,
                                                                            4, hop_time=0.7))
        # animation.play_animation(card_yellow_2, vibrate_once_2d("rotation2d", card_yellow_2.rotation2d, (0.1, 0.1), 0.5))

        for card in start_screen_lower_group:
            pretime += 0.1
            posttime -= 0.1
            card.scale2d = (0, 0)
            scale_animation_sequence = AnimationSequenceTask(loop=False)

            animation_task_1 = constant_2d("scale2d", (0, 0), pretime + 1)
            animation_task_2 = overshoot_2d("scale2d", (0, 0), (0.15, 0.15), 0.5, overshoot=0.6)
            animation_task_3 = constant_2d("scale2d", (0.15, 0.15), posttime)

            scale_animation_sequence.add_sub_task(animation_task_1)
            scale_animation_sequence.add_sub_task(animation_task_2)
            scale_animation_sequence.add_sub_task(animation_task_3)

            animation.play_animation(card, scale_animation_sequence, layer=1)

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
                                         (WINDOW_WIDTH / 2, WINDOW_HEIGHT / 3), 0.15)
        self.play_label.add_click_listener(lambda: change_screen(StartGameScreen()))
        self.rules_label = ClickableLabel("resources/images/ui/labels/rules_label.png",
                                          "resources/images/ui/labels/clickable_rules_label.png",
                                          (WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2.25), 0.15)
        self.rules_label.add_click_listener(lambda: change_screen(RuleScreen()))
        self.exit_label = ExitGameLabel("resources/images/ui/labels/exit_label.png",
                                        "resources/images/ui/labels/clickable_exit_label.png",
                                        (WINDOW_WIDTH / 2, WINDOW_HEIGHT / 1.8), 0.15)

        self.objects.append(self.play_label)
        self.objects.append(self.rules_label)
        self.objects.append(self.exit_label)

        # Animation Time!
        set_label_cursor_anim_effect(self.play_label)
        set_label_cursor_anim_effect(self.rules_label)
        set_label_cursor_anim_effect(self.exit_label)
        pop_up_buttons([self.play_label, self.rules_label, self.exit_label])


class RuleScreen(ScreenBase):
    def __init__(self):
        super().__init__(background_filename="resources/images/ui/screens/rulescreen.png")
        self.back_label = BackLabel("resources/images/ui/labels/back_label.png",
                                    "resources/images/ui/labels/clickable_back_label.png",
                                    (WINDOW_WIDTH / 1.2, WINDOW_HEIGHT / 1.1))
        self.objects.append(self.back_label)


class StartGameScreen(ScreenBase):
    def __init__(self):
        super().__init__(background_filename="resources/images/ui/screens/StartGameScreen.png")
        print("Initializing StartGameScreen")  # Debug print

        # Initialize two player button
        self.two_player_label = TwoPlayerLabel(
            "resources/images/ui/labels/two_player.png",
            "resources/images/ui/labels/clickable_two_player.png",
            (WINDOW_WIDTH / 4, WINDOW_HEIGHT / 1.65), 0.15)

        print("Created TwoPlayerLabel")  # Debug print

        # Initialize three player button
        self.three_player_label = ThreePlayerLabel(
            "resources/images/ui/labels/three_player.png",
            "resources/images/ui/labels/clickable_three_player.png",
            (WINDOW_WIDTH / 1.35, WINDOW_HEIGHT / 1.65), 0.15)

        print("Created ThreePlayerLabel")  # Debug print
        # Initialize back label
        self.back_label = BackLabel(
            "resources/images/ui/labels/back_label.png",
            "resources/images/ui/labels/clickable_back_label.png",
            (WINDOW_WIDTH / 1.15, WINDOW_HEIGHT / 1.1), 0.1)
        print("Created BackLabel")  # Debug print

        # Add labels to objects list
        self.objects = []
        self.objects.append(self.two_player_label)
        self.objects.append(self.three_player_label)
        self.objects.append(self.back_label)
        print("Added labels to objects list")  # Debug print

        set_label_cursor_anim_effect(self.two_player_label)
        set_label_cursor_anim_effect(self.three_player_label)
        pop_up_buttons([self.two_player_label, self.three_player_label])

    def update(self):
        """Update all objects in the screen"""
        for obj in self.objects:
            obj.update()

    def mouseup(self, event):
        """Handle mouse button release"""
        if event.button == 1:  # Left click
            mouse_pos = event.pos
            print(f"Mouse click at position: {mouse_pos}")  # Debug print
            for obj in self.objects:
                if obj.is_inside(mouse_pos):
                    print(f"Clicked on {type(obj).__name__}")  # Debug print
                    obj.click()
                    break

    def keydown(self, event):
        """Handle keyboard events"""
        if event.key == K_ESCAPE:
            global current_screen
            current_screen = HomeScreen()

    def draw(self, screen):
        """Draw the screen and all its objects"""
        super().draw(screen)  # Draw background first
        for obj in self.objects:
            obj.draw(screen)


class EndDrawLabel(ClickableLabel):
    def __init__(self, game_state):
        super().__init__(
            "resources/images/ui/labels/end_draw_from_deck.png",
            "resources/images/ui/labels/clickable_end_draw_from_deck.png",
            (WINDOW_WIDTH / 2 + CARD_WIDTH + 100, WINDOW_HEIGHT / 2),  # Position right of deck
            0.07  # Scale factor
        )
        self.game_state = game_state
        self.visible = False  # Start invisible

    def update(self):
        # Only show and allow interaction when cards are drawn
        self.visible = (self.game_state.draw_mode_active and
                        len(self.game_state.drawn_cards) > 0 and self.game_state.current_player == 0)
        if self.visible:
            super().update()

    def draw(self, screen):
        if self.visible:
            super().draw(screen)

    def click(self):
        if self.visible:
            # self.game_state.confirm_drawn_cards()
            self.game_state.human_input.end_draw_card_from_deck()


class EndTurnLabel(ClickableLabel):
    def __init__(self, game_state):
        super().__init__(
            "resources/images/ui/labels/end_turn_label.png",
            "resources/images/ui/labels/clickable_end_turn_label.png",
            (WINDOW_WIDTH / 1.15, WINDOW_HEIGHT / 2),  # Position right of deck
            0.1  # Scale factor
        )

    def click(self):
        pass


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
                (WINDOW_WIDTH / 2.10, WINDOW_HEIGHT / 2.18),
                0.16
            ),
            'pass': ClickableLabel(
                "resources/images/ui/labels/game_pass_label.png",
                "resources/images/ui/labels/clickable_game_pass_label.png",
                (WINDOW_WIDTH / 1.7, WINDOW_HEIGHT / 1.055),
                0.065
            ),
            'drawfromdeck': ClickableLabel(
                "resources/images/ui/labels/draw_from_deck_label.png",
                "resources/images/ui/labels/clickable_draw_from_deck_label.png",
                (WINDOW_WIDTH / 2.9, WINDOW_HEIGHT / 1.6),
                0.15
            ),
            'drawfromplayer': ClickableLabel(
                "resources/images/ui/labels/draw_from_player_label.png",
                "resources/images/ui/labels/clickable_draw_from_player_label.png",
                (WINDOW_WIDTH / 1.6, WINDOW_HEIGHT / 1.6),
                0.15
            ),
            'discard': ClickableLabel(
                "resources/images/ui/labels/discard_label.png",
                "resources/images/ui/labels/clickable_discard_label.png",
                (WINDOW_WIDTH / 2.2, WINDOW_HEIGHT / 1.055),
                0.065
            ),
            'playforme': ClickableLabel(
                "resources/images/ui/labels/play_for_me_label.png",
                "resources/images/ui/labels/clickable_play_for_me_label.png",
                (WINDOW_WIDTH / 3.65, WINDOW_HEIGHT / 1.055),
                0.065
            ),
            'quitgame': QuitGameLabel(
                "resources/images/ui/labels/quit_game_label.png",
                "resources/images/ui/labels/clickable_quit_game_label.png",
                (WINDOW_WIDTH / 1.07, WINDOW_HEIGHT / 1.075),
                0.12),
            'end_draw': EndDrawLabel(self.game_state),
            'end_turn': ClickableLabel(
                "resources/images/ui/labels/end_turn_label.png",
                "resources/images/ui/labels/clickable_end_turn_label.png",
                (WINDOW_WIDTH / 1.35, WINDOW_HEIGHT / 1.055),
                0.06),
            'end_draw_from_player': ClickableLabel(image_path1="resources/images/ui/labels/end_draw_from_player.png",
                                                   image_path2="resources/images/ui/labels/clickable_end_draw_from_player.png",
                                                   pos=(WINDOW_WIDTH / 2 - CARD_WIDTH - 100, WINDOW_HEIGHT / 3),
                                                   scale_factor=0.07),
        }

        self.buttons['pass'].add_click_listener(self.game_state.human_input.pass_turn)
        self.buttons['drawfromdeck'].add_click_listener(self.game_state.human_input.start_draw_from_deck)
        self.buttons['end_turn'].add_click_listener(self.game_state.human_input.pass_turn)

        def draw_from_player():
            other_player = self.game_state.players[1].logic_player
            self.game_state.human_input.start_draw_from_other_player(other_player)
            self.buttons['drawfromplayer'].enabled = False

        self.buttons['drawfromplayer'].add_click_listener(draw_from_player)
        self.buttons['discard'].add_click_listener(self.game_state.human_input.dispose_selected)
        self.buttons['deck'].add_click_listener(self.game_state.human_input.draw_card_from_deck)
        self.buttons['end_draw_from_player'].add_click_listener(self.game_state.human_input.draw_from_other_player)

        self.buttons['playforme'].add_click_listener(self.handle_play_for_me)
        self.buttons['quitgame'].add_click_listener(self.handle_quitgame)

        self.player1_profile = RenderableImage("resources/images/ui/labels/you_icon.png",
                                               (WINDOW_WIDTH * 0.05, WINDOW_HEIGHT * 0.815), (0.04, 0.04), (1, 0))
        self.player2_profile = RenderableImage("resources/images/ui/labels/computer.png",
                                               (WINDOW_WIDTH * 0.05, WINDOW_HEIGHT * 0.145), (0.04, 0.04), (1, 0))
        self.objects.append(self.player1_profile)
        self.objects.append(self.player2_profile)

        # Add buttons to objects list
        self.objects.extend(self.buttons.values())

        button_list = list(self.buttons.values())
        for button in button_list:
            set_label_cursor_anim_effect(button)
            set_label_enable_anim_effect(button)
        button_list.extend([self.player1_profile, self.player2_profile])
        pop_up_buttons(button_list)

    def _set_buttons_enabled(self, enabled):
        self.buttons['drawfromdeck'].enabled = enabled
        self.buttons['drawfromplayer'].enabled = enabled
        self.buttons['playforme'].enabled = enabled
        self.buttons['discard'].enabled = enabled
        self.buttons['pass'].enabled = enabled
        self.buttons['end_turn'].enabled = enabled

    def hide_buttons(self):
        self._set_buttons_enabled(False)

    def resume_buttons(self):
        self._set_buttons_enabled(True)

    def set_enable_end_draw_from_other_player(self, enabled):
        button = self.buttons['end_draw_from_player']
        button.visible = enabled
        button.enabled = enabled

    def handle_card_click(self, pos):
        """Handle clicking on cards"""
        if self.game_state.animation_in_progress:
            return False

        # First check current player's cards
        current_player = self.game_state.players[self.game_state.current_player]
        clicked_card = current_player.handle_click(pos)
        if clicked_card:
            if clicked_card.selected:
                print(f"Card clicked and deselected: {clicked_card.color}_{clicked_card.number}")
                self.game_state.human_input.deselect_card(clicked_card.logic_card)
            else:
                print(f"Card clicked and selected: {clicked_card.color}_{clicked_card.number}")
                self.game_state.human_input.select_card(clicked_card.logic_card)
            return True

        # Then check opponent's cards
        for i, player in enumerate(self.game_state.players):
            if i != self.game_state.current_player:
                clicked_card = player.handle_click(pos)
                if clicked_card and self.game_state.current_player == 0:
                    self.game_state.human_input.select_from_other_player(clicked_card.logic_card)
                    return True

        return False

    def handle_pass(self):
        """Handle pass button click"""
        if not self.game_state.animation_in_progress:
            self.game_state.end_turn()

    def handle_drawfromplayer(self):
        """Handle draw button click"""
        if not self.game_state.animation_in_progress:
            self.game_state.toggle_take_opponent_mode()

    def handle_drawfromdeck(self):
        """Handle clicking the deck"""
        if not self.game_state.animation_in_progress:
            self.game_state.draw_single_card()

    def handle_deck_click(self):
        """Handle clicking the deck"""
        if not self.game_state.animation_in_progress:
            self.game_state.draw_single_card()

    def handle_discard(self):
        """Handle discard button click"""
        if not self.game_state.animation_in_progress:
            current_player = self.game_state.players[self.game_state.current_player]
            if len(current_player.selected_cards) >= 3:
                if self.game_state.is_valid_group(current_player.selected_cards):
                    self.game_state.discard_cards(current_player.selected_cards)

    def handle_play_for_me(self):
        """Handle auto-play button click"""
        ai_input = core.AIPlayerInput()
        self.game_state.players[0].logic_player.set_input(ai_input)
        self.game_state.human_input.deactivate()
        ai_input.other_player_memory = self.game_state.players[1].logic_player

        def resume_play_for_me():
            """Resume play button click"""
            ai_input = self.game_state.players[0].logic_player.player_input
            human_input = self.game_state.human_input
            if isinstance(ai_input, core.AIPlayerInput):
                ai_input.player = None
                self.game_state.players[0].logic_player.set_input(human_input)

        ai_input.add_on_deactivate_listener(resume_play_for_me)
        ai_input.activate()
        ai_input.evaluate_situation_and_response()
        self.buttons['playforme'].enabled = False

    def handle_quitgame(self):
        if not self.game_state.animation_in_progress:
            self.game_state.end_turn()

    def mouseup(self, event):
        """Handle mouse button release"""
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
        """Handle keyboard input"""
        if event.key == K_SPACE:
            # self.game_state.take_opponent_card()
            if self.buttons['end_draw_from_player'].enabled:
                self.game_state.human_input.draw_from_other_player()
        elif event.key == K_RETURN:
            if self.buttons['end_turn'].enabled:
                self.game_state.human_input.pass_turn()
        elif event.key == K_ESCAPE:
            global current_screen
            current_screen = HomeScreen()

    def draw(self, screen):
        """Draw the game screen"""
        # Draw background
        super().draw(screen)

        # Draw game state
        self.game_state.draw(screen)

        # Draw UI elements
        for button in self.buttons.values():
            button.draw(screen)

        # Draw turn indicator
        font = pygame.font.Font(None, 36)

        # Define player names based on their index
        player_names = ["YOUR", "COMPUTER'S"]

        # Get the current player's name based on the current player index
        current_player_name = player_names[self.game_state.current_player]

        # Create the text to display
        text = font.render(f"{current_player_name} TURN", True, (255, 255, 255))
        screen.blit(text, (WINDOW_WIDTH / 6.5, WINDOW_HEIGHT / 2.25))

        # For three player mode only - draw player labels
        if hasattr(self, 'draw_player_labels'):
            self.draw_player_labels(screen)

    def update(self):
        """Update game state"""
        self.game_state.game_logic_server.update()  # update the game logic server
        for button in self.buttons.values():
            button.update()

        # Update deck appearance based on state
        if self.game_state.deck_highlighted:
            self.buttons['deck'].image_src = self.buttons['deck'].img_src_hover
        else:
            self.buttons['deck'].image_src = self.buttons['deck'].img_src_normal

        if self.game_state.current_player == 0 and self.game_state.selected_opponent_card is not None:
            button = self.buttons['end_draw_from_player']
            button.visible = True
            button.enabled = True
        else:
            button = self.buttons['end_draw_from_player']
            button.visible = False
            button.enabled = False


class ThreePlayerScreen(ScreenBase):
    def __init__(self):
        super().__init__(background_filename='resources/images/ui/screens/PlayScreen.png')
        self.game_state = GameState(num_players=3)
        self.active_opponent = None  # Track which opponent we're currently drawing from
        self.available_opponents = []  # Store opponents with cards
        self.opponent_indices = []  # Store opponent indices

        # Initialize buttons
        button_scale = 0.1
        button_y = WINDOW_HEIGHT - 30

        self.buttons = {
            'deck': ClickableLabel(
                "resources/images/ui/labels/deck_label.png",
                "resources/images/ui/labels/clickable_deck_label.png",
                (WINDOW_WIDTH / 2.10, WINDOW_HEIGHT / 2.18),
                0.16
            ),
            'pass': ClickableLabel(
                "resources/images/ui/labels/game_pass_label.png",
                "resources/images/ui/labels/clickable_game_pass_label.png",
                (WINDOW_WIDTH / 1.7, WINDOW_HEIGHT / 1.055),
                0.065
            ),
            'drawfromdeck': ClickableLabel(
                "resources/images/ui/labels/draw_from_deck_label.png",
                "resources/images/ui/labels/clickable_draw_from_deck_label.png",
                (WINDOW_WIDTH * 0.5, WINDOW_HEIGHT / 1.6),
                0.15
            ),
            'drawfromleftplayer': ClickableLabel("resources/images/ui/labels/draw_from_left_player.png",
                                                 "resources/images/ui/labels/clickable_draw_from_left_player.png",
                                                 (WINDOW_WIDTH * 0.22, WINDOW_HEIGHT * 0.4),
                                                 0.06),
            'drawfromrightplayer': ClickableLabel("resources/images/ui/labels/draw_from_right_player.png",
                                                  "resources/images/ui/labels/clickable_draw_from_right_player.png",
                                                  (WINDOW_WIDTH * 0.78, WINDOW_HEIGHT * 0.4),
                                                  0.06),
            'discard': ClickableLabel(
                "resources/images/ui/labels/discard_label.png",
                "resources/images/ui/labels/clickable_discard_label.png",
                (WINDOW_WIDTH / 2.2, WINDOW_HEIGHT / 1.055),
                0.065
            ),
            'playforme': ClickableLabel(
                "resources/images/ui/labels/play_for_me_label.png",
                "resources/images/ui/labels/clickable_play_for_me_label.png",
                (WINDOW_WIDTH / 3.65, WINDOW_HEIGHT / 1.055),
                0.065
            ),
            'quitgame': QuitGameLabel(
                "resources/images/ui/labels/quit_game_label.png",
                "resources/images/ui/labels/clickable_quit_game_label.png",
                (WINDOW_WIDTH / 1.07, WINDOW_HEIGHT / 1.075),
                0.12),
            'end_draw': EndDrawLabel(self.game_state),
            'end_turn': ClickableLabel(
                "resources/images/ui/labels/end_turn_label.png",
                "resources/images/ui/labels/clickable_end_turn_label.png",
                (WINDOW_WIDTH / 1.35, WINDOW_HEIGHT / 1.055),
                0.06),
            'end_draw_from_player': ClickableLabel(image_path1="resources/images/ui/labels/end_draw_from_player.png",
                                                   image_path2="resources/images/ui/labels/clickable_end_draw_from_player.png",
                                                   pos=(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 3), scale_factor=0.07)

        }

        # Set up button click handlers
        self.buttons['pass'].add_click_listener(self.game_state.human_input.pass_turn)
        self.buttons['drawfromdeck'].add_click_listener(self.game_state.human_input.start_draw_from_deck)

        def draw_from_player_1():
            if self.active_opponent is not None:
                return
            self.active_opponent = self.game_state.players[1]
            other_player = self.game_state.players[1].logic_player
            self.game_state.human_input.start_draw_from_other_player(other_player)
            self.buttons['drawfromleftplayer'].enabled = False
            self.buttons['drawfromrightplayer'].enabled = False

        def draw_from_player_2():
            if self.active_opponent is not None:
                return
            self.active_opponent = self.game_state.players[2]
            other_player = self.game_state.players[2].logic_player
            self.game_state.human_input.start_draw_from_other_player(other_player)
            self.buttons['drawfromleftplayer'].enabled = False
            self.buttons['drawfromrightplayer'].enabled = False

        # self.buttons['drawfromplayer'].add_click_listener(self.handle_drawfromplayer)
        self.buttons['drawfromleftplayer'].add_click_listener(draw_from_player_1)
        self.buttons['drawfromrightplayer'].add_click_listener(draw_from_player_2)
        self.buttons['discard'].add_click_listener(self.game_state.human_input.dispose_selected)
        self.buttons['deck'].add_click_listener(self.game_state.human_input.draw_card_from_deck)
        self.buttons['end_draw_from_player'].add_click_listener(self.game_state.human_input.draw_from_other_player)
        self.buttons['playforme'].add_click_listener(self.handle_play_for_me)
        self.buttons['quitgame'].add_click_listener(self.handle_quitgame)
        self.buttons['end_turn'].add_click_listener(self.game_state.human_input.pass_turn)

        # adding player icon
        self.player1_profile = RenderableImage("resources/images/ui/labels/you_icon.png",
                                               (WINDOW_WIDTH * 0.06, WINDOW_HEIGHT * 0.82), (0.04, 0.04), (1, 0))
        self.player2_profile = RenderableImage("resources/images/ui/labels/computer_1.png",
                                               (WINDOW_WIDTH * 0.22, WINDOW_HEIGHT * 0.07), (0.04, 0.04), (1, 0))
        self.player3_profile = RenderableImage("resources/images/ui/labels/computer_2.png",
                                               (WINDOW_WIDTH * 0.78, WINDOW_HEIGHT * 0.07), (0.055, 0.055), (1, 0))
        self.objects.append(self.player1_profile)
        self.objects.append(self.player2_profile)
        self.objects.append(self.player3_profile)

        # Add buttons to objects list
        self.objects.extend(self.buttons.values())

        button_list = list(self.buttons.values())
        for button in button_list:
            set_label_cursor_anim_effect(button)
            set_label_enable_anim_effect(button)
        button_list.extend([self.player1_profile, self.player2_profile, self.player3_profile])
        pop_up_buttons(button_list)

    def _set_buttons_enabled(self, enabled):
        self.buttons['drawfromleftplayer'].enabled = enabled
        self.buttons['drawfromrightplayer'].enabled = enabled
        self.buttons['drawfromdeck'].enabled = enabled
        self.buttons['playforme'].enabled = enabled
        self.buttons['discard'].enabled = enabled
        self.buttons['pass'].enabled = enabled
        self.buttons['end_turn'].enabled = enabled

    def hide_buttons(self):
        self._set_buttons_enabled(False)

    def resume_buttons(self):
        self._set_buttons_enabled(True)

    def set_enable_end_draw_from_other_player(self, enabled):
        button = self.buttons['end_draw_from_player']
        button.visible = enabled
        button.enabled = enabled

    def handle_drawfromplayer(self):
        """Enable selection from either opponent"""
        current_idx = self.game_state.current_player

        # Reset any previous selections
        if self.game_state.selected_opponent_card:
            self.game_state.selected_opponent_card.highlighted = False
            self.game_state.selected_opponent_card = None

        # Get both opponent indices
        self.opponent_indices = [(current_idx + i) % 3 for i in range(1, 3)]

        # Reset and store both opponents
        self.available_opponents = []
        for idx in self.opponent_indices:
            opponent = self.game_state.players[idx]
            if opponent.cards:  # Only add opponents who have cards
                self.available_opponents.append(opponent)
            # Set all opponent cards face down
            # for card in opponent.cards:
            #     card.set_face_down()
            # opponent.update_card_positions()

        # Enable selection from any opponent with cards
        if self.available_opponents:
            # Initialize with first opponent but allow switching
            self.active_opponent = self.available_opponents[0]
            self.game_state.toggle_take_opponent_mode()
            for opponent in self.available_opponents:
                self.game_state.human_input.start_draw_from_other_player(opponent.logic_player)

    def handle_card_click(self, pos):
        """Handle clicking on cards"""
        if self.game_state.animation_in_progress:
            return False

        # First check current player's cards
        current_player = self.game_state.players[self.game_state.current_player]
        clicked_card = current_player.handle_click(pos)
        if clicked_card:
            if clicked_card.selected:
                self.game_state.human_input.deselect_card(clicked_card.logic_card)
                print(f"Card deselected: {clicked_card.color}_{clicked_card.number}")
            else:
                self.game_state.human_input.select_card(clicked_card.logic_card)
                print(f"Card selected: {clicked_card.color}_{clicked_card.number}")
            return True

        # Then check opponent's cards
        for i, player in enumerate(self.game_state.players):
            if i != self.game_state.current_player:
                clicked_card = player.handle_click(pos)
                if clicked_card:
                    if self.game_state.current_player == 0 and self.active_opponent is not None and clicked_card in self.active_opponent.cards:
                        self.game_state.human_input.select_from_other_player(clicked_card.logic_card)
                    else:
                        print("Selected cards is not in your current selected opponent's hand")
                    return True

        return False

    def handle_play_for_me(self):
        """Handle auto-play button click"""
        ai_input = core.AIPlayerInput()
        self.game_state.players[0].logic_player.set_input(ai_input)
        if self.active_opponent is not None:
            ai_input.other_player_memory = self.active_opponent.logic_player
        self.game_state.human_input.deactivate()

        def resume_play_for_me():
            """Resume play button click"""
            ai_input = self.game_state.players[0].logic_player.player_input
            human_input = self.game_state.human_input
            if isinstance(ai_input, core.AIPlayerInput):
                ai_input.player = None
                self.game_state.players[0].logic_player.set_input(human_input)

        ai_input.add_on_deactivate_listener(resume_play_for_me)
        ai_input.activate()
        ai_input.evaluate_situation_and_response()
        self.buttons['playforme'].enabled = False

    def handle_quitgame(self):
        """Handle quit game button click"""
        if not self.game_state.animation_in_progress:
            global current_screen
            current_screen = HomeScreen()

    def mouseup(self, event):
        """Handle mouse button release"""
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
        """Handle keyboard input"""
        if event.key == K_SPACE:
            # self.game_state.take_opponent_card()
            if self.buttons['end_draw_from_player'].enabled:
                self.game_state.human_input.draw_from_other_player()
        elif event.key == K_RETURN:
            if self.buttons['end_turn'].enabled:
                self.game_state.human_input.pass_turn()
        elif event.key == K_ESCAPE:
            global current_screen
            current_screen = HomeScreen()

    def draw(self, screen):
        """Draw the game screen"""
        # Draw background
        super().draw(screen)

        # Draw game state
        self.game_state.draw(screen)

        # Draw UI elements
        for button in self.buttons.values():
            button.draw(screen)

        # Draw turn indicator
        font = pygame.font.Font(None, 36)

        # Define player names based on their index
        player_names = ["YOUR", "COMPUTER 1'S", "COMPUTER 2'S"]

        # Get the current player's name based on the current player index
        current_player_name = player_names[self.game_state.current_player]

        # Create the text to display
        text = font.render(f"{current_player_name} TURN", True, (255, 255, 255))
        screen.blit(text, (WINDOW_WIDTH / 2.5, 50))

        # For three player mode only - draw player labels
        if hasattr(self, 'draw_player_labels'):
            self.draw_player_labels(screen)

    def update(self):
        """Update game state"""
        self.game_state.game_logic_server.update()  # Add this line
        for button in self.buttons.values():
            button.update()

        # Update deck appearance based on state
        if self.game_state.deck_highlighted:
            self.buttons['deck'].image_src = self.buttons['deck'].img_src_hover
        else:
            self.buttons['deck'].image_src = self.buttons['deck'].img_src_normal

        if self.game_state.current_player == 0 and self.game_state.selected_opponent_card is not None:
            button = self.buttons['end_draw_from_player']
            button.visible = True
            button.enabled = True
        else:
            button = self.buttons['end_draw_from_player']
            button.visible = False
            button.enabled = False


class CongratsScreen(ScreenBase):
    def __init__(self):
        super().__init__(background_filename='resources/images/ui/screens/CongratulationsScreen.png')

        self.newgame_label = NewGameLabel("resources/images/ui/labels/new_game_label.png",
                                          "resources/images/ui/labels/clickable_new_game_label.png",
                                          (WINDOW_WIDTH / 2, WINDOW_HEIGHT / 1.18), 0.13)
        self.exit_label = ExitGameLabel("resources/images/ui/labels/exit_label.png",
                                        "resources/images/ui/labels/clickable_exit_label.png",
                                        (WINDOW_WIDTH / 2, WINDOW_HEIGHT / 1.08), 0.13)

        self.objects.append(self.newgame_label)
        self.objects.append(self.exit_label)

    def keydown(self, event):
        if event.key == K_ESCAPE:
            global game_over
            game_over = True


class LoseScreen(ScreenBase):
    def __init__(self):
        super().__init__(background_filename='resources/images/ui/screens/SorryScreen.png')

        self.newgame_label = NewGameLabel("resources/images/ui/labels/new_game_label.png",
                                          "resources/images/ui/labels/clickable_new_game_label.png",
                                          (WINDOW_WIDTH / 2, WINDOW_HEIGHT / 1.18), 0.13)
        self.exit_label = ExitGameLabel("resources/images/ui/labels/exit_label.png",
                                        "resources/images/ui/labels/clickable_exit_label.png",
                                        (WINDOW_WIDTH / 2, WINDOW_HEIGHT / 1.08), 0.13)

        self.objects.append(self.newgame_label)
        self.objects.append(self.exit_label)

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
        animation.update()
        current_screen.draw(screen)
        pygame.display.flip()
        pygame.time.delay(30)

    pygame.quit()


if __name__ == "__main__":
    main()
