from scripts.ui_base import *
import scripts.configs as configs

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