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