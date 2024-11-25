from scripts.ui_base import VisualObject

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