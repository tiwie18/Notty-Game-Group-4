import math

import pygame
from pygame.locals import *
import random
from scripts.animation import *
import scripts.math_util as math_util
from scripts.math_util import vec_2d_minus, normalize_vec2d, vec_2d_mul, euler_angle_to_rotation

WINDOW_WIDTH = 700
WINDOW_HEIGHT = 500

game_over = False
current_screen = None


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
        background = Background("resources/images/ui/screen/StartScreenObject/Rectangle.png")
        # ball = RenderableImage("ball.png",position2d=(100, 100), scale2d=(0.1, 0.1))
        rotation_identity = math_util.euler_angle_to_rotation(0)
        bg_ratio = 500 / 3546
        pos_0 = (3670 * bg_ratio,809 * bg_ratio)
        pos_1 = (499 * bg_ratio, 1049 * bg_ratio)
        pos_2 = (668 * bg_ratio, 777 * bg_ratio)
        pos_3 = (971 * bg_ratio, 849 * bg_ratio)
        pos_4 = (1156 * bg_ratio, 545 * bg_ratio)
        pos_5 = (1560 * bg_ratio, 593 * bg_ratio)
        pos_6 = (3096 * bg_ratio, 625 * bg_ratio)
        pos_7 = (3462 * bg_ratio, 689 * bg_ratio)
        pos_8 = (3825 * bg_ratio, 750 * bg_ratio)
        pos_9 = (4137 * bg_ratio, 945 * bg_ratio)
        pos_10 = (1972 * bg_ratio, 2729 * bg_ratio)
        pos_11 = (2356 * bg_ratio, 2641 * bg_ratio)
        pos_12 = (2755 * bg_ratio, 2689 * bg_ratio)

        card_red_1 = RenderableImage("resources/images/ui/screen/StartScreenObject/Object 1.png", position2d=pos_1, scale2d=(0.16, 0.16),
                                     rotation2d=rotation_identity)
        card_red_2 = RenderableImage("resources/images/ui/screen/StartScreenObject/Object 1 (1).png", position2d=pos_2, scale2d=(0.16, 0.16),
                                     rotation2d=rotation_identity)
        card_red_3 = RenderableImage("resources/images/ui/screen/StartScreenObject/Object 1 (2).png", position2d=pos_3, scale2d=(0.16, 0.16),
                                     rotation2d=rotation_identity)
        card_red_4 = RenderableImage("resources/images/ui/screen/StartScreenObject/Object 1 (3).png", position2d=pos_4, scale2d=(0.16, 0.16),
                                     rotation2d=rotation_identity)
        card_red_5 = RenderableImage("resources/images/ui/screen/StartScreenObject/Object 1 (4).png", position2d=pos_5, scale2d=(0.16, 0.16),
                                     rotation2d=rotation_identity)
        card_red_6 = RenderableImage("resources/images/ui/screen/StartScreenObject/Object 1 (8).png", position2d=pos_6, scale2d=(0.16, 0.16),
                                     rotation2d=rotation_identity)
        card_red_7 = RenderableImage("resources/images/ui/screen/StartScreenObject/Object 1 (7).png", position2d=pos_7, scale2d=(0.16, 0.16),
                                     rotation2d=rotation_identity)
        card_red_8 = RenderableImage("resources/images/ui/screen/StartScreenObject/Object 1 (6).png", position2d=pos_8, scale2d=(0.16, 0.16),
                                     rotation2d=rotation_identity)
        card_red_9 = RenderableImage("resources/images/ui/screen/StartScreenObject/Object 1 (5).png", position2d=pos_9, scale2d=(0.16, 0.16),
                                     rotation2d=rotation_identity)

        title_image = RenderableImage("resources/images/ui/screen/StartScreenObject/NottyGame.png", position2d=(WINDOW_WIDTH * 0.5, WINDOW_HEIGHT * 0.5), scale2d=(0.16, 0.16),
                                     rotation2d=rotation_identity)

        card_yellow_1 = RenderableImage("resources/images/ui/screen/StartScreenObject/Object 1 (10).png", position2d=pos_10, scale2d=(0.16, 0.16),
                                     rotation2d=rotation_identity)
        card_yellow_2 = RenderableImage("resources/images/ui/screen/StartScreenObject/Object 1 (11).png", position2d=pos_11, scale2d=(0.16, 0.16),
                                     rotation2d=rotation_identity)
        card_yellow_3 = RenderableImage("resources/images/ui/screen/StartScreenObject/Object 1 (12).png", position2d=pos_12, scale2d=(0.16, 0.16),
                                     rotation2d=rotation_identity)

        self.objects.append(background)
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

        start_screen_upper_group = [card_red_1, card_red_2, card_red_3, card_red_4, card_red_5, card_red_6, card_red_7, card_red_8, card_red_9]
        start_screen_lower_group = [card_yellow_1, card_yellow_2, card_yellow_3]
        start_screen_group = [card_red_1, card_red_2, card_red_3, card_red_4, card_red_5, card_red_6, card_red_7, card_red_8, card_red_9, title_image, card_yellow_1, card_yellow_2,card_yellow_3]

        # animation.play_animation(self.ball, move_to("position2d",(100,100),(200,200),1))
        # animation.play_animation(self.ball, ease_in_out_2d("position2d",(100,100),(300, 300),1))
        # animation.play_animation(card_red_1, ping_pong("position2d", (100, 100), (150, 200), 1))
        # animation.play_animation(card_red_1, hop_2d("position2d", pos_1, (-10, -10), 0.3))

        central_point = (WINDOW_HEIGHT * 0.5, WINDOW_HEIGHT)
        pretime = 0
        posttime = 2
        for card in start_screen_upper_group:
            # calc the motion offset for each card
            offset = math_util.vec_2d_mul(normalize_vec2d(vec_2d_minus(card.position2d, central_point)),10)
            end_pos =  math_util.vec_2d_plus(card.position2d, offset)
            pretime += 0.1
            posttime -= 0.1
            animation.play_animation(card,
                                     hop_with_overshoot_sequence("position2d", card.position2d, offset, pretime, posttime))

            card.scale2d = (0, 0)
            scale_animation_sequence = AnimationSequenceTask(loop=False)

            animation_task_1 = constant_2d("scale2d", (0, 0), pretime + 1)
            animation_task_2 = overshoot_2d("scale2d", (0, 0), (0.15, 0.15), 0.5, overshoot=0.6)
            animation_task_3 = constant_2d("scale2d", (0.15, 0.15), posttime)

            scale_animation_sequence.add_sub_task(animation_task_1)
            scale_animation_sequence.add_sub_task(animation_task_2)
            scale_animation_sequence.add_sub_task(animation_task_3)

            animation.play_animation(card, scale_animation_sequence, layer=1)

        animation.play_animation(title_image, ping_pong("scale2d", (0.15,0.15),(0.16,0.16), 2))
        title_image.alpha = 0

        alpha_animation_sequence = AnimationSequenceTask(loop=False)
        alpha_animation_sequence.add_sub_task(constant_1d("alpha", 0,2))
        alpha_animation_sequence.add_sub_task(ease_in_out_1d("alpha", 0, 255, 2))
        alpha_animation_sequence.add_sub_task(constant_1d("alpha", 255,3))

        animation.play_animation(title_image, alpha_animation_sequence, layer=1)
        animation.play_animation(card_yellow_1, hop_with_overshoot_sequence("rotation2d",card_yellow_1.rotation2d, euler_angle_to_rotation(5),0,4,hop_time=0.7))
        animation.play_animation(card_yellow_3, hop_with_overshoot_sequence("rotation2d",card_yellow_3.rotation2d, euler_angle_to_rotation(-5),2,2,hop_time=0.7))

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