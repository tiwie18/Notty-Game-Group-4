import math

import pygame
from pygame.locals import *
import random
from scripts.animation import *
import scripts.math_util as math_util

WINDOW_WIDTH = 600
WINDOW_HEIGHT = 500

game_over = False
current_screen = None


class VisualObject:
    def __init__(self, position2d=(0, 0), scale2d=(1, 1), rotation2d=(1, 0)):
        self.position2d = position2d
        self.scale2d = scale2d
        self.rotation2d = rotation2d
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
    def __init__(self, image_src, position2d=(0, 0), scale2d=(1, 1), rotation2d=(1, 0)):
        super().__init__(position2d=position2d, scale2d=scale2d, rotation2d=rotation2d)
        self.image_src = image_src
        self.image = pygame.image.load(image_src)
        self._store_cache()

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
        transformed_image = pygame.transform.scale(transformed_image,
                                                   (rect.width * scale_ratio, rect.height * scale_ratio))
        # t (not needed to be processed here)
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
        self._cached_transformed_image = self._transform_image()
        self._cached_size2d = self._size2d()
        self._cached_rotation2d = self.rotation2d

    # when properties changed e.g. scale or the whole image src, it requires a resample, which means update the cache
    def _update_cache_if_dirty(self):
        if self.image_src != self._cached_image_src:
            self.image = pygame.image.load(self.image_src)
            self._store_cache()
        elif self._cached_size2d != self._size2d() or self.rotation2d != self._cached_rotation2d:
            self._store_cache()

    def draw(self, screen):
        self._update_cache_if_dirty()
        rect = self._cached_transformed_image.get_rect(center=self.position2d)
        screen.blit(self._cached_transformed_image, rect.topleft)

    def update(self):
        pass


class Background(VisualObject):
    def __init__(self, image_src):
        super().__init__(position2d=(0, 0), scale2d=(1, 1))
        self.image = pygame.transform.scale(pygame.image.load(image_src), (WINDOW_WIDTH, WINDOW_HEIGHT))

    def draw(self, screen):
        screen.blit(self.image, (0, 0))


class Label(VisualObject):
    def __init__(self, text, pos, colour):
        self.text = text
        self.pos = pos
        self.colour = colour
        self.size = 36
        self.font = pygame.font.SysFont(None, self.size)

    def draw(self, screen):
        img = self.font.render(self.text, True, self.colour)
        self.width = img.get_width()
        self.height = img.get_height()
        screen.blit(img, self.pos)


class ClickableLabel(Label):
    def __init__(self, text, pos, colour1, colour2):
        super().__init__(text, pos, colour1)
        self.colour1 = colour1
        self.colour2 = colour2

    def is_inside(self, pos):
        return self.pos[0] <= pos[0] <= self.pos[0] + self.width \
            and self.pos[1] <= pos[1] <= self.pos[1] + self.height

    def update(self):
        if self.is_inside(pygame.mouse.get_pos()):
            self.colour = self.colour2
        else:
            self.colour = self.colour1

    def mouseup(self, event):
        if event.button == 1 and self.is_inside(event.pos):
            self.click()

    def click(self):
        pass


class NewGameLabel(ClickableLabel):
    def click(self):
        global current_screen
        current_screen = MainScreen()


class CloseWindowLabel(ClickableLabel):
    def click(self):
        global game_over
        game_over = True


class ScreenBase:
    def __init__(self, background_colour, background_filename=None):
        self.background_colour = background_colour
        self.objects = []
        if background_filename is not None:
            self.background_image = pygame.image.load(background_filename)
            pass
        else:
            self.background_image = None

    def draw(self, screen):
        screen.fill(self.background_colour)

        if self.background_image is not None:
            screen.blit(self.background_image, (0, 0))

        for o in self.objects:
            o.draw(screen)

    def update(self):
        for o in self.objects:
            o.update()


class MainScreen(ScreenBase):
    def __init__(self):
        super().__init__(pygame.Color('black'), None)
        background = Background("resources/images/ui/screen/PlayScreen.png")
        # ball = RenderableImage("ball.png",position2d=(100, 100), scale2d=(0.1, 0.1))
        rotation_15_deg = math_util.euler_angle_to_rotation(15)
        bg_ratio = 500 / 3546
        pos_1 = (499 * bg_ratio, 1049 * bg_ratio)
        pos_2 = (668 * bg_ratio, 777 * bg_ratio)
        pos_3 = (971 * bg_ratio, 849 * bg_ratio)
        pos_4 = (1156 * bg_ratio, 545 * bg_ratio)
        pos_5 = (1499 * bg_ratio, 617 * bg_ratio)

        card_red_1 = RenderableImage("resources/images/card/red_1.png", position2d=pos_1, scale2d=(0.3, 0.3),
                                     rotation2d=rotation_15_deg)
        card_red_2 = RenderableImage("resources/images/card/red_2.png", position2d=pos_2, scale2d=(0.3, 0.3),
                                     rotation2d=rotation_15_deg)
        card_red_3 = RenderableImage("resources/images/card/red_3.png", position2d=pos_3, scale2d=(0.3, 0.3),
                                     rotation2d=rotation_15_deg)
        card_red_4 = RenderableImage("resources/images/card/red_4.png", position2d=pos_4, scale2d=(0.3, 0.3),
                                     rotation2d=rotation_15_deg)
        card_red_5 = RenderableImage("resources/images/card/red_5.png", position2d=pos_5, scale2d=(0.3, 0.3),
                                     rotation2d=rotation_15_deg)

        self.objects.append(background)
        self.objects.append(card_red_1)
        self.objects.append(card_red_2)
        self.objects.append(card_red_3)
        self.objects.append(card_red_4)
        self.objects.append(card_red_5)

        # animation.play_animation(self.ball, sine_scale_AnimationTask("size2d"))
        # animation.play_animation(self.ball, move_to("position2d",(100,100),(200,200),1))
        # animation.play_animation(self.ball, ease_in_out_2d("position2d",(100,100),(300, 300),1))
        # animation.play_animation(card_red_1, ping_pong("position2d", (100, 100), (150, 200), 1))
        # animation.play_animation(card_red_1, hop_2d("position2d", pos_1, (-10, -10), 0.3))
        animation.play_animation(card_red_1, hop_sequence("position2d", pos_1, (-10, -10), pre_time=0.5, post_time=1))
        animation.play_animation(card_red_2, hop_sequence("position2d", pos_2, (-10, -10), pre_time=0.6, post_time=0.9))
        animation.play_animation(card_red_3, hop_sequence("position2d", pos_3, (-10, -10), pre_time=0.7, post_time=0.8))
        animation.play_animation(card_red_4, hop_sequence("position2d", pos_4, (-10, -10), pre_time=0.8, post_time=0.7))
        animation.play_animation(card_red_5, hop_sequence("position2d", pos_5, (-10, -10), pre_time=0.9, post_time=0.6))


class GameOverScreen(ScreenBase):
    def __init__(self):
        super().__init__(pygame.Color('blue'))
        self.objects.append(NewGameLabel('Start a new game', (100, 100), pygame.Color('white'), pygame.Color('red')))
        self.objects.append(
            CloseWindowLabel('Close the window', (100, 200), pygame.Color('white'), pygame.Color('red')))

    def keydown(self, event):
        if event.key == K_ESCAPE:
            global game_over
            game_over = True


def run_game():
    global current_screen

    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))

    pygame.display.set_caption('Hello World!')

    current_screen = MainScreen()

    while not game_over:
        # Handling the events
        for event in pygame.event.get():
            if event.type == QUIT:
                return

        # Rendering the picture
        current_screen.draw(screen)

        pygame.display.flip()

        # Updating the objects
        current_screen.update()
        animation.update()

        # A delay
        pygame.time.wait(10)


run_game()
pygame.quit()