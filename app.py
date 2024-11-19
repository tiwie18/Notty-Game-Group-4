import pygame
import random
import os
from dataclasses import dataclass
from typing import List, Tuple

@dataclass
class Card:
    color: str
    number: int
    image: pygame.Surface = None
    rect: pygame.Rect = None

class CardGame:
    def __init__(self):
        self.colors = ['red', 'blue', 'yellow', 'green']
        self.numbers = range(1, 11)  # 1 to 10
        self.deck = []
        self.players_hands = []
        self.card_images = {}  # Dictionary to store loaded images
        self.load_card_images()
        
    def load_card_images(self):
        """
        Load card images from a directory.
        Expected image naming format: 'color_number.png'
        Example: 'red_1.png', 'blue_10.png'
        """
        # Specify the directory where your card images are stored
        image_dir = 'resources/images/cards'  # Create a 'cards' folder in your project directory
        
        # Make sure the images directory exists
        if not os.path.exists(image_dir):
            os.makedirs(image_dir)
            print(f"Created '{image_dir}' directory. Please place your card images there.")
            return
        
        # Load each card image
        for color in self.colors:
            for number in self.numbers:
                # Construct the filename
                filename = f"{color}_{number}.png"
                filepath = os.path.join(image_dir, filename)
                
                try:
                    # Load and scale the image (adjust size as needed)
                    original_image = pygame.image.load(filepath)
                    scaled_image = pygame.transform.scale(original_image, (80, 120))
                    self.card_images[f"{color}_{number}"] = scaled_image
                except pygame.error:
                    print(f"Couldn't load image: {filepath}")
                    # Create a placeholder if image is missing
                    placeholder = pygame.Surface((80, 120))
                    placeholder.fill((200, 200, 200))  # Gray background
                    font = pygame.font.Font(None, 36)
                    text = font.render(f"{color[0]}{number}", True, (0, 0, 0))
                    text_rect = text.get_rect(center=(40, 60))
                    placeholder.blit(text, text_rect)
                    self.card_images[f"{color}_{number}"] = placeholder
        
    def create_deck(self):
        # Create two of each card
        for _ in range(2):
            for color in self.colors:
                for number in self.numbers:
                    card = Card(color, number)
                    # Assign the corresponding image
                    card.image = self.card_images[f"{color}_{number}"]
                    self.deck.append(card)
        
        # Shuffle the deck
        random.shuffle(self.deck)
    
    def deal_initial_hands(self, num_players):
        if num_players not in [2, 3]:
            raise ValueError("Game supports only 2 or 3 players")
        
        self.players_hands = [[] for _ in range(num_players)]
        
        # Deal 5 cards to each player
        for _ in range(5):
            for player in range(num_players):
                if self.deck:  # Check if deck is not empty
                    card = self.deck.pop()
                    self.players_hands[player].append(card)
    
    def draw_cards(self, screen, card_width=80, card_height=120):
        # Draw cards for each player
        for player_idx, hand in enumerate(self.players_hands):
            for card_idx, card in enumerate(hand):
                # Position cards for each player
                if player_idx == 0:  # Bottom player
                    x = 100 + card_idx * (card_width + 10)
                    y = screen.get_height() - card_height - 20
                elif player_idx == 1:  # Top player
                    x = 100 + card_idx * (card_width + 10)
                    y = 20
                else:  # Third player (if exists) on right side
                    x = screen.get_width() - card_width - 20
                    y = 100 + card_idx * (card_height + 10)
                
                # Create rectangle for card position
                card.rect = pygame.Rect(x, y, card_width, card_height)
                
                # Draw the card image
                screen.blit(card.image, card.rect)

def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    clock = pygame.time.Clock()
    
    game = CardGame()
    game.create_deck()
    game.deal_initial_hands(2)  # Change to 3 for three players
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        screen.fill((0, 100, 0))  # Green table background
        game.draw_cards(screen)
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()

if __name__ == "__main__":
    main()