import pygame
import os

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

    def add_visual_object(self, obj):
        # render queue
        if hasattr(obj, 'z_index'):
            current_render_queue_length = len(self.objects)
            obj.z_index = current_render_queue_length  # append render queue
            self.objects.append(obj)

    def sort_render_queue(self):
        self.objects.sort(key=lambda obj: obj.z_index)

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




import scripts.global_variables as global_variables

def change_screen(screen_instance):
    global_variables.current_screen = screen_instance
