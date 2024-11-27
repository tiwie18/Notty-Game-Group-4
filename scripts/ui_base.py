import pygame
import os
import scripts.math_util as math_util

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
        return self.pos[0] - self.width * 0.5 <= pos[0] <= self.pos[0] + self.width * 0.5 and \
            self.pos[1] - self.height * 0.5 <= pos[1] <= self.pos[1] + self.height * 0.5

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


def load_and_scale_image(image_path, scale_factor=0.2):
    """Memuat gambar dan mengubah ukurannya berdasarkan scale_factor."""
    img = pygame.image.load(image_path)
    new_width = int(img.get_width() * scale_factor)
    new_height = int(img.get_height() * scale_factor)
    return pygame.transform.scale(img, (new_width, new_height))