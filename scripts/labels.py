from scripts.ui_base import *
import scripts.global_variables as global_variables


class PlayGameLabel(ClickableLabel):
    def click(self):
        from scripts.screens import StartGameScreen
        global_variables.current_screen = StartGameScreen()


class RulesLabel(ClickableLabel):
    def click(self):
        from scripts.screens import RuleScreen
        global_variables.current_screen = RuleScreen()


class SettingLabel(ClickableLabel):
    def click(self):
        # todo: add a setting screen
        global_variables.current_screen = SettingScreen()


class QuitGameLabel(ClickableLabel):
    def click(self):
        from scripts.screens import HomeScreen
        global_variables.current_screen = HomeScreen()

class BackLabel(ClickableLabel):
    def click(self):
        from scripts.screens import HomeScreen
        global_variables.current_screen = HomeScreen()

class TwoPlayerLabel(ClickableLabel):
    def click(self):
        from scripts.screens import PlayScreen
        global_variables.current_screen = PlayScreen(2)


class ThreePlayerLabel(ClickableLabel):
    def click(self):
        from scripts.screens import PlayScreen
        global_variables.current_screen = PlayScreen(3)


class DrawCardLabel(ClickableLabel):
    def __init__(self, game):
        self.game = game  # Reference to the PlayGame instance

    def display_action_options(self):
        # Display action options for the player
        choice = input("Choose action:\n1. Take a card from the opponent\n2. Draw cards from the deck\n")

        if choice == '1':
            self.game.take_card_from_opponent()  # Execute the action from PlayGame(we need to make new def in PlayGame Class)
        elif choice == '2':
            self.game.draw_cards_from_deck()  # Execute the action from PlayGame(we need to make new def in PlayGame Class)
        else:
            print("Invalid choice. Please choose again.")

    def reset_turn(self):
        # to make sure that this choice only once per turn
        self.game.reset_turn()


class DiscardLabel(ClickableLabel):
    def __init__(self, game):
        self.game = game

    def click(self):
        self.game.discard_card()  # Execute the action from PlayGame(we need to make new def in PlayGame Class)


class PlayForMeLabel(ClickableLabel):
    def __init__(self, game):
        self.game = game

    def click(self):
        self.game.play_for_me()  # Execute the action from PlayGame(we need to make new def in PlayGame Class)


class GamePassLabel(ClickableLabel):
    def __init__(self, image_path_1, image_path_2, pos, scale_factor=0.2):
        super().__init__(image_path_1, image_path_2, pos, scale_factor=scale_factor)

    def click(self):
        pass


class DeckLabel(ClickableLabel):
    def click(self):
        pass


class NewGameLabel(ClickableLabel):
    def click(self):
        from scripts.screens import HomeScreen
        global_variables.current_screen = HomeScreen()


class ExitGameLabel(ClickableLabel):
    def click(self):
        global_variables.game_over = True