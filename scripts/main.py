import re
import pygame
import random
from enum import Enum

# when you want to mute all the print in the module, this is a good way
# print = lambda x : None

def verify_cards(string_list):
    checked_list = []
    for card_string in string_list:
        '''
        (regular expressions) module that checks for a match only at the beginning of a string. 
        This function returns a match object if the beginning of the string matches the pattern, 
        or None if there is no match.
        '''
        res = re.match(r'^(red|blue|green|yellow)\x20([1-9]|10)$', card_string)
        if res is None:
            return False
        # No more than 2 cards, this implementation will result in no more than 1 card, which is a mistake
        if checked_list.count(card_string) > 1:
            return False
        checked_list.append(card_string)
    return True

class Card:
    def __init__(self, colour, number):
        assert isinstance(number, int)
        self.colour = colour
        self.number = number

    def __str__(self):
        return f'{self.colour} {self.number}'

    @property
    def color(self):
        return self.colour

    @color.setter
    def color(self, value):
        self.colour = value

class CollectionOfCards:
    def __init__(self):
        self.collection = []

    @property
    def count(self):
        return len(self.collection)

    def push_cards(self, card_list):
        self.collection += card_list

    def push_card(self, card):
        self.collection.append(card)

    def pop_card(self, index = None):
        if index is None:
            return self.collection.pop()
        return self.collection.pop(index)

    def remove_card(self, card):
        self.collection.remove(card)

    def shuffle(self):
        random.shuffle(self.collection)

    @staticmethod
    def static_is_valid_group(card_list):
        card_count = len(card_list)
        if card_count < 3:
            return False
        if len([card for card in card_list if card.number == 3 and card.colour == "green" ]) != 0:
            print(card_list)

        # case 1: same color
        same_color_flag = True
        for i in range(card_count-1):
            if card_list[i].colour != card_list[i+1].colour:
                same_color_flag = False
                break
        if same_color_flag:
            # sort the list to check continuity
            card_list.sort(key=lambda card: card.number)
            consecutive_flag = True
            for i in range(card_count - 1):
                if card_list[i+1].number-card_list[i].number != 1:
                    consecutive_flag = False
                    break
            return consecutive_flag

        # case 2: same number
        same_number_flag = True
        for i in range(card_count-1):
            if card_list[i].number != card_list[i+1].number:
                same_number_flag = False
                break
        if not same_number_flag:
            return False
        if card_count > 4:
            return False
        # This part is better done with a Counter, but using a dictionary do not need to import another collection
        # Using set is even a better choice, but list is not ideal because it produces O(x) Time complexity
        # set and dictionary use hashing so the time complexity is generally O(1)
        color_count_dict = {'red': 0, 'blue': 0, 'green': 0, 'yellow': 0}
        for card in card_list:
            if color_count_dict[card.colour] > 0:
                # Once a colour is already detected, it returns false immediately because that means same colors
                return False
            color_count_dict[card.colour] = 1
        return True

    def is_valid_group(self):
        # If they are of the same color, then all the numbers must be consecutive
        # if they are of the same number, then they cannot have duplicate colors
        # I should optimize the implementation of the method based on the aforementioned features
        card_list = self.collection
        card_count = len(card_list)
        if card_count < 3:
            return False

        # case 1: same color
        same_color_flag = True
        for i in range(card_count-1):
            if card_list[i].colour != card_list[i+1].colour:
                same_color_flag = False
                break
        if same_color_flag:
            # sort the list to check continuity
            card_list.sort(key=lambda card: card.number)
            consecutive_flag = True
            for i in range(card_count - 1):
                if card_list[i+1].number-card_list[i].number != 1:
                    consecutive_flag = False
                    break
            return consecutive_flag

        # case 2: same number
        same_number_flag = True
        for i in range(card_count-1):
            if card_list[i].number != card_list[i+1].number:
                same_number_flag = False
                break
        if not same_number_flag:
            return False
        if card_count > 4:
            return False
        # This part is better done with a Counter, but using a dictionary do not need to import another collection
        # Using set is even a better choice, but list is not ideal because it produces O(x) Time complexity
        # set and dictionary use hashing so the time complexity is generally O(1)
        color_count_dict = {'red': 0, 'blue': 0, 'green': 0, 'yellow': 0}
        for card in card_list:
            if color_count_dict[card.colour] > 0:
                # Once a colour is already detected, it returns false immediately because that means same colors
                return False
            color_count_dict[card.colour] = 1
        return True

    def find_valid_group(self):
        # In consideration of efficiency it returns the first valid group it found

        # find by color
        for color in ['red', 'blue', 'green', 'yellow']:
            # spilt the collection in 4 groups
            same_color_list = [card for card in self.collection if card.colour == color]
            if len(same_color_list) < 3:
                continue
            same_color_list.sort(key=lambda card: card.number)
            # sort each group to check whether they contain a subgroup which is consecutive
            candidate_cards = []
            for card in same_color_list:
                # always compare the current number with the last number in the candidate_cards list
                # this is consecutive case
                if len(candidate_cards) == 0 or candidate_cards[-1].number + 1 == card.number:
                    candidate_cards.append(card)
                elif candidate_cards[-1].number + 1 < card.number:  # if not consecutive, clear the list
                    candidate_cards.clear()
                    candidate_cards.append(card)
                # maybe I missed the case that the current number is the same as the previous one
                # but in that case nothing needs to be done,so I didn't write that branch
                # once it has 3 consecutive numbers, a valid group is found, and it immediately returns that candidate
                if len(candidate_cards) >= 3:
                    return candidate_cards

        # find by number
        for number in range(1, 11):
            # group all the cards by number, somehow I don't want to declare 10 separate lists even if it saves time
            # so in by implementation I check all the cards ten times
            same_number_list = [card for card in self.collection if card.number == number]
            if len(same_number_list) < 3:
                continue
            # For doing this a set is sufficient, but I used a dict to record its index
            # But I have to convert a Card object into the tuple form e.g. ('red',5),
            # otherwise I will not be able to utilize the feature of set
            # I can also implement a __hash__ method in Card class but modifying the implementation if Card is banned
            color_index_dict = {}
            for i in range(len(same_number_list)):
                # record its index so that if multiple cards of the same number exist
                # the later one will cover the previous one
                color_index_dict[same_number_list[i].colour] = i
            if len(color_index_dict) >= 3:
                # more than 3 unique cards
                # in this case I have to retrieve all the cards again using the index stored
                return [same_number_list[index] for index in color_index_dict.values()]
        return None

    def find_largest_valid_group(self):
        # Quite identical to the previous method but I have to check all the possible valid groups
        # rather than return immediately when I found 3 qualified cards
        # largest valid group is initially set to be an empty list
        largest_valid_group = []
        # split all the cards in 4 groups by their colors
        for color in ['red', 'blue', 'green', 'yellow']:
            same_color_list = [card for card in self.collection if card.colour == color]
            if len(same_color_list) < 3:
                continue
            # sort for continuity check
            same_color_list.sort(key=lambda card: card.number)
            candidate_cards = []
            for card in same_color_list:
                if len(candidate_cards) == 0 or candidate_cards[-1].number + 1 == card.number:
                    candidate_cards.append(card)
                elif candidate_cards[-1].number + 1 < card.number:
                    # check before clear
                    # maybe there is already a valid group in candidate_cards list
                    # if the valid group is larger than existing largest valid group, just supersede them
                    # otherwise discard the candidate
                    if len(candidate_cards) > len(largest_valid_group) and len(candidate_cards) >= 3:
                        largest_valid_group = candidate_cards
                        # use new list to avoid conflict between references
                        # candidate and largest valid group should always be to different lists
                        candidate_cards = []
                    else:
                        # clear the candidate list, no need to instantiate a new list
                        candidate_cards.clear()
                    candidate_cards.append(card)
            if len(candidate_cards) > len(largest_valid_group) and len(candidate_cards) >= 3:
                largest_valid_group = candidate_cards
        if len(largest_valid_group) >= 4:
            # the size of valid group by color cannot surpass 4
            # so if I already have a valid group contains 4 or more cards,
            # there will be no need to check the valid group of the same number
            return largest_valid_group

        for number in range(1, 11):
            same_number_list = [card for card in self.collection if card.number == number]
            if len(same_number_list) < 3:
                continue
            # Again I used a dict
            color_index_dict = {}
            for i in range(len(same_number_list)):
                # use the color as key, the index as value
                color_index_dict[same_number_list[i].colour] = i
            if len(color_index_dict) >= 3 and len(color_index_dict) > len(largest_valid_group):
                # use the index stored to retrieve the full valid group
                largest_valid_group = [same_number_list[index] for index in color_index_dict.values()]

        if len(largest_valid_group) >= 3:
            return largest_valid_group
        return None

def probability_of_valid_group(player_list):
    p0_card_list = player_list[0].collection
    # now I start to use set
    candidate_card_set = set()

    # check by color
    for color in ['red', 'blue', 'green', 'yellow']:
        same_color_list = [card for card in p0_card_list if card.colour == color]
        if len(same_color_list) <= 1:
            continue
        same_color_list.sort(key=lambda card: card.number)
        # find valid groups while finding qualified cards, once consecutive count reaches 3 a valid group is found,
        # and it will return 1 directly
        consecutive_count = 0
        for i in range(len(same_color_list)):
            if i == 0 or same_color_list[i].number == same_color_list[i-1].number + 1:
                # If the latter card is numerically consecutive with the previous card, add 1 to consecutive count
                consecutive_count += 1
            elif same_color_list[i].number == same_color_list[i-1].number:
                pass
            elif same_color_list[i].number > same_color_list[i-1].number + 1:
                # In this branch, a consecutive sublist ends, and we should check the both ends of this list
                # if the count haven't reached 3
                # check
                if consecutive_count >= 3:  # A valid group is already detected, return 1
                    return 1
                if consecutive_count == 2:  # Add left end and right end to candidates
                    left_end_number = same_color_list[i-1].number - 2
                    if left_end_number >= 0:
                        candidate_card_set.add((color, left_end_number))
                    right_end_number = same_color_list[i-1].number + 1
                    if right_end_number <= 10:
                        candidate_card_set.add((color, right_end_number))
                if consecutive_count == 1:
                    # check whether there is an empty position between two numbers
                    # to the left and the right of the current number
                    # there might be duplicated checks for a single number but the python set will handle it
                    left_end_number = same_color_list[i-1].number - 1
                    if i >= 2 and same_color_list[i-2].number == same_color_list[i-1].number - 2:
                        candidate_card_set.add((color, left_end_number))
                    right_end_number = same_color_list[i-1].number + 1
                    if i < len(same_color_list) and same_color_list[i].number == same_color_list[i-1].number + 2:
                        candidate_card_set.add((color, right_end_number))
                consecutive_count = 1
        # Final Check after loop
        # the loop already ends, so I need to do an extra check
        if consecutive_count >= 3:
            return 1
        if consecutive_count == 2:  # Add left end and right end to candidates
            left_end_number = same_color_list[len(same_color_list) - 1].number - 2
            if left_end_number >= 0:
                candidate_card_set.add((color, left_end_number))
            right_end_number = same_color_list[len(same_color_list) - 1].number + 1
            if right_end_number <= 10:
                candidate_card_set.add((color, right_end_number))

    # check by number
    for number in range(1, 11):
        same_number_list = [card for card in p0_card_list if card.number == number]
        # if a number group contains 2 different colors, then the other 2 colors are qualified
        color_set = {'red', 'blue', 'green', 'yellow'}
        for card in same_number_list:
            # every time it removes the color of the already
            # discard() is a safe way of removing a color that don't even in the set
            color_set.discard(card.colour)
        if len(color_set) <= 1:
            return 1
        if len(color_set) == 2:
            candidate_card_set.add((color_set.pop(), number))
            candidate_card_set.add((color_set.pop(), number))

    # unique candidate set was formed
    # now figure out what remains in card deck
    # map every unique card to an integer from 0 to 39
    def card_to_index(color, number):
        return ['red', 'blue', 'green', 'yellow'].index(color) * 10 + number - 1

    card_deck = [2] * (4 * 10)  # full card deck
    for player in player_list:
        for card in player.collection:
            index = card_to_index(card.colour, card.number)
            card_deck[index] -= 1

    deck_count = sum(card_deck)  # How many cards are there left in the deck
    effective_card_count = 0
    for card_tuple in candidate_card_set:
        index = card_to_index(card_tuple[0], card_tuple[1])  # calculate the number of qualified cards left in the deck
        effective_card_count += card_deck[index]

    # print(candidate_card_set)
    # print(deck_count)
    # print(card_deck)
    return effective_card_count / deck_count   # the final result

class GameLogicActor:
    def __init__(self, game_manager):
        self.game_manager = game_manager
        if game_manager != self:
            game_manager.add_actor(self)

    def send_request(self, job):
        self.game_manager.receive_request(job)
        return job

    def start(self):
        pass

    def update(self, dt):
        pass

class PlayerOptions(Enum):
    DRAW_START_5_CARDS = 0
    START_DRAW_CARD_FROM_DECK = 1
    DRAW_CARD_FROM_DECK = 2
    END_DRAW_CARD_FROM_DECK = 3
    START_TURN = 4
    START_DRAW_FROM_OTHER_PLAYER = 5
    SELECT_CARD_FROM_OTHER_PLAYER = 6
    DRAW_CARD_FROM_PLAYER = 7
    END_DRAW_FROM_OTHER_PLAYER = 8
    SELECT_CARD_FROM_COLLECTION = 9
    DESELECT_CARD_FROM_COLLECTION = 10
    DISPOSE_VALID_GROUP = 11
    PASS = 12

class PlayerInput:
    def __init__(self):
        self.player = None
        self.active = False
        self.on_activate_listener_list = []
        self.on_deactivate_listener_list = []

    def activate(self):
        self.active = True
        for listener in self.on_activate_listener_list:
            listener()

    def deactivate(self):
        self.active = False
        for listener in self.on_deactivate_listener_list:
            listener()

    def evaluate_situation_and_response(self):
        pass

    def add_on_activate_listener(self, on_activate_listener):
        self.on_activate_listener_list.append(on_activate_listener)

    def add_on_deactivate_listener(self, on_deactivate_listener):
        self.on_deactivate_listener_list.append(on_deactivate_listener)

class AIPlayerInput(PlayerInput):
    def __init__(self):
        super().__init__()
        self.valid_group_memory = None
        self.other_player_memory = None

    def activate(self):
        super().activate()
        print("Player AI input activated")

    def deactivate(self):
        super().deactivate()
        print("Player AI input deactivated")

    def evaluate_situation_and_response(self):
        if not self.active:
            print("Player AI input is deactivated")
            return
        player_status = self.player.game_manager.get_player_status(self.player)
        draw_from_other_player = random.choice([True, False])
        if player_status.turn_end:
            self.deactivate()
        elif not player_status.draw_from_other_player_start and not player_status.start_draw_from_deck and draw_from_other_player and self.player.card_count() < 20:
            players = self.player.game_manager.players
            players.remove(self.player)
            other_player = random.choice(players)
            if other_player.card_count() <= 1:
                players.remove(other_player)
                if len(players) > 0:
                    other_player = random.choice(players)
            if other_player.card_count() <= 1:
                self.player.pass_turn() # todo:
            else:
                self.player.start_draw_from_other_player(other_player)
                self.other_player_memory = other_player
        elif player_status.draw_from_other_player_start and not player_status.have_selected_from_other_player:
            other_player_card_count = self.other_player_memory.card_count()
            random_number = random.randint(0, other_player_card_count - 1)
            card = self.other_player_memory.card_at(random_number)
            self.player.select_from_other_player(self.other_player_memory, card)
            # self.player.draw_from_other_player(self.other_player_memory, card)
            print("player.select_from_other_player(self.other_player_memory, card)")
        elif player_status.have_selected_from_other_player and not player_status.have_drawn_from_other_player:
            self.player.draw_from_other_player(self.other_player_memory)
            print("player.draw_from_other_player(self.other_player_memory, card)")
        elif not player_status.draw_from_other_player_end and player_status.have_drawn_from_other_player:
            self.player.end_draw_from_other_player()
        elif not player_status.start_draw_from_deck and not player_status.draw_from_other_player_start and not draw_from_other_player and self.player.card_count() < 20:
            deck = self.player.game_manager.deck
            if not deck.empty():
                self.player.start_draw_from_deck()
            else:
                self.player.pass_turn()
        elif player_status.start_draw_from_deck and not player_status.end_draw_from_deck:
            if player_status.num_card_drawn_from_deck < 3 and self.player.card_count() < 20:
                self.player.draw_card_from_deck()
            else:
                self.player.end_draw_card_from_deck()
        elif self.valid_group_memory is None:
            current_selected = self.player.selected_as_list()
            card_need_deselect = None
            if len(current_selected) > 0:
                card_need_deselect = current_selected.pop()
            if card_need_deselect is not None:
                self.player.deselect_card(card_need_deselect)
            else:
                self.valid_group_memory = self.player.find_largest_valid_group()
                if self.valid_group_memory is None:
                    self.player.pass_turn()
                else:
                    self.player.select_card(self.valid_group_memory.pop())
        elif self.valid_group_memory is not None:
            if len(self.valid_group_memory) > 0:
                card = self.valid_group_memory.pop()
                self.player.select_card(card)
            elif self.player.selected_valid_group():
                self.player.dispose_selected()
                self.valid_group_memory = None
            else:
                print("This branch should not be executed")

class IPlayerAgentListener:
    def draw_start_cards(self, job):
        pass

    def start_turn(self,job):
        pass

    def start_draw_from_deck(self,job):
        pass

    def draw_card_from_deck(self,job):
        pass

    def end_draw_card_from_deck(self,job):
        pass

    def select_card(self, card, job):
        pass

    def deselect_card(self, card,job):
        pass

    def dispose_selected(self, job):
        pass

    def pass_turn(self, job):
        pass

    def start_draw_from_other_player(self, other_player, job):
        pass

    def select_from_other_player(self, other_player, card, job):
        pass

    def draw_from_other_player(self, other_player, card, job):
        pass

    def end_draw_from_other_player(self, job):
        pass

class PlayerAgent(GameLogicActor):
    def __init__(self, game_manager, player_input):
        super().__init__(game_manager)
        self._collection = CollectionOfCards()
        self.player_input = player_input
        self._selected_card_set = set()
        self._other_selected_card = None
        self._action_listeners = []
        player_input.player = self

    def set_input(self, player_input: PlayerInput):
        self.player_input = player_input
        player_input.player = self

    def add_action_listener(self, player_agent_listener: IPlayerAgentListener):
        self._action_listeners.append(player_agent_listener)

    def card_as_list(self):
        return self._collection.collection.copy()

    def card_count(self):
        return self._collection.count

    def push_card(self, card):
        self._collection.push_card(card)

    def mark_card_selected(self, card):
        if card in self._collection.collection:
            self._selected_card_set.add(card)
            print(f"{card} was selected")
        else:
            raise ValueError(f"{card} not in collection!")

    def mark_card_unselected(self, card):
        if card in self._collection.collection:
            self._selected_card_set.remove(card)
            print(f"{card} was unselected")
        else:
            raise ValueError(f"{card} not in collection!")

    def mark_card_other_selected(self, card):
        if card in self._collection.collection:
            self._other_selected_card = card
            print(f"{card} was selected by other")
        else:
            raise KeyError(f"{card} not in collection!")

    def card_at(self, index):
        return self._collection.collection[index]

    def pop_selected(self):
        for card in self._selected_card_set:
            self._collection.remove_card(card)
            print(f"{card} was removed")
        temp = self._selected_card_set
        self._selected_card_set = set()
        return list(temp)

    def clear_selected(self):
        self._selected_card_set.clear()

    def clear_other_selected(self):
        self._other_selected_card = None

    def other_selected_card(self):
        return self._other_selected_card

    def pop_other_selected(self):
        self._collection.remove_card(self._other_selected_card)
        temp = self._other_selected_card
        self._other_selected_card = None
        return temp

    def has_card(self,card):
        return card in self._collection.collection

    def pop_card(self, index):
        self._collection.pop_card(index)

    def remove_card(self, card):
        self._collection.remove_card(card)

    def selected_as_list(self):
        return list(self._selected_card_set)

    def selected_count(self):
        return len(self._selected_card_set)

    def have_selected(self, card):
        return card in self._selected_card_set

    def shuffle(self):
        self._collection.shuffle()

    def selected_valid_group(self):
        return CollectionOfCards.static_is_valid_group(list(self._selected_card_set))

    def find_largest_valid_group(self):
        return self._collection.find_largest_valid_group()

    def draw_start_cards(self):
        deck = self.game_manager.deck
        job = PlayerDrawStartCardJob(deck, self, 0.3)
        for listener in self._action_listeners:
            listener.draw_start_cards(job)
        return self.send_request(job)

    def start_turn(self):
        job = PlayerStartTurnJob(self)
        for listener in self._action_listeners:
            listener.start_turn(job)
        return self.send_request(job)

    def start_draw_from_deck(self):
        job = StartDrawCardFromDeckJob(self)
        for listener in self._action_listeners:
            listener.start_draw_from_deck(job)
        return self.send_request(job)

    def draw_card_from_deck(self):
        job = DrawCardFromDeckJob(self)
        for listener in self._action_listeners:
            listener.draw_card_from_deck(job)
        return self.send_request(job)

    def end_draw_card_from_deck(self):
        job = EndDrawCardFromDeckJob(self)
        for listener in self._action_listeners:
            listener.end_draw_card_from_deck(job)
        return self.send_request(job)

    def select_card(self, card):
        job = SelectCardFromCollectionJob(self,card)
        for listener in self._action_listeners:
            listener.select_card(card,job)
        return self.send_request(job)

    def deselect_card(self, card):
        job = DeselectCardFromCollectionJob(self,card)
        for listener in self._action_listeners:
            listener.deselect_card(card, job)
        return self.send_request(job)

    def dispose_selected(self):
        job = DiscardSelectedFromCollectionJob(self)
        for listener in self._action_listeners:
            listener.dispose_selected(job)
        return self.send_request(job)

    def pass_turn(self):
        job = EndTurnJob(self)
        for listener in self._action_listeners:
            listener.pass_turn(job)
        return self.send_request(job)

    def start_draw_from_other_player(self, other_player):
        job = StartDrawCardFromOtherPlayerJob(self, other_player)
        for listener in self._action_listeners:
            listener.start_draw_from_other_player(other_player, job)
        return self.send_request(job)

    def select_from_other_player(self, other_player,card):
        job = SelectFromOtherPlayerJob(self, other_player, card)
        for listener in self._action_listeners:
            listener.select_from_other_player(other_player, card, job)
        return self.send_request(job)

    def draw_from_other_player(self, other_player):
        job = DrawFromOtherPlayerJob(self, other_player)
        card = other_player.other_selected_card()
        for listener in self._action_listeners:
            listener.draw_from_other_player(other_player, card, job)
        return self.send_request(job)

    def end_draw_from_other_player(self):
        job = EndDrawFromOtherPlayerJob(self)
        for listener in self._action_listeners:
            listener.end_draw_from_other_player(job)
        return self.send_request(job)

class DrawCardBuffer:
    def __init__(self):
        self._collection = CollectionOfCards()

    def push_card(self, card):
        if self._collection.count < 3:
            self._collection.push_card(card)
        else:
            raise ValueError("Can't push more than 3 cards to buffer!")

    def pop_all_cards(self):
        cards = self._collection.collection
        self._collection.collection = []
        return cards

    def card_as_list(self):
        return self._collection.collection.copy()

    def full(self):
        return self._collection.count >= 3

class Deck:
    def __init__(self):
        self._collection = CollectionOfCards()
        # card_name_list = [ f"{color}_{number}" for color in ['red', 'blue', 'green', 'yellow'] for number in range(1, 11) ]
        for color in ['red', 'blue', 'green', 'yellow']:
            for number in range(1, 11):
                self._collection.push_card(Card(color, number))
                self._collection.push_card(Card(color, number))
        self._collection.shuffle()


    def print_deck(self):
        for card in self._collection.collection:
            print(card)

    def empty(self):
        return self._collection.count == 0

    def pop_card(self):
        return self._collection.pop_card()

    def push_card(self, card):
        self._collection.push_card(card)

    def push_cards(self, cards):
        self._collection.push_cards(cards)

    def shuffle(self):
        print("shuffle deck")
        self._collection.shuffle()

    def card_as_list(self):
        return self._collection.collection.copy()

class GameJob:
    def __init__(self, function, duration = 0):
        self._function = function
        self._duration = duration
        self._start_evoke_listener_list = []
        self._end_evoke_listener_list = []
        self._time_left = duration

    def add_start_evoke_listener(self, function):
        self._start_evoke_listener_list.append(function)

    def add_end_evoke_listener(self, function):
        self._end_evoke_listener_list.append(function)

    def evoke(self):
        self._function()
        for listener in self._start_evoke_listener_list:
            listener()

    def end_evoke(self):
        for listener in self._end_evoke_listener_list:
            listener()

    def update(self, dt):
        self._time_left -= dt

    def finished(self):
        return self._time_left <= 0

class PlayerGameJob(GameJob):
    def __init__(self, player_option, player, function, duration = 0):
        super().__init__(function, duration)
        self.player_option = player_option
        self.player = player

def draw_start_card_wrapper(deck, player):
    # python enclosure
    def draw_card():
        for i in range(5):
            card = deck.pop_card()
            print(f"player draw card: {card}")
            player.push_card(card)
    return draw_card

def draw_card_from_deck_wrapper(deck, buffer):
    def draw_card():
        if not buffer.full():
            card = deck.pop_card()
            buffer.push_card(card)
            print(f"player draw card to buffer: {card}")

    return draw_card

def add_card_in_buffer_wrapper(buffer, player):
    def add_card():
        cards = buffer.pop_all_cards()
        for card in cards:
            player.push_card(card)
        print(f"{len(cards)} cards added from buffer: {buffer}")
    return add_card

def start_turn_wrapper(player):
    def start_turn():
        index = player.game_manager.players.index(player)
        player.game_manager.player_turn = index
        print(f"{index} player turn")
    return start_turn

def discard_selected_wrapper(player):
    def discard_card():
        cards = player.pop_selected()
        deck = player.game_manager.deck
        deck.push_cards(cards)
        print(f"{cards} disposed from player: {player}")

    return discard_card

def start_draw_card_from_other_player_wrapper(other_player):
    def start_draw_card():
        other_player.shuffle()
        print(f"start draw from other player {other_player}")
    return start_draw_card

def select_card_from_other_player_wrapper(other_player, card):
    def select_card():
        if other_player.has_card(card):
            other_player.mark_card_other_selected(card)
            print(f"{card} selected from other player: {other_player}")
        else:
            raise KeyError("Card not in collection of other player")
    return select_card

def draw_card_from_other_player_wrapper(player, other_player):
    def draw_card():
        card = other_player.pop_other_selected()
        player.push_card(card)
        print (f"player draw card from other player: {card}")

    return draw_card

def end_turn_wrapper(player):
    def end_turn():
        game_manager = player.game_manager
        deck = game_manager.deck
        buffer = game_manager.draw_card_buffer
        cards = buffer.pop_all_cards()
        for card in cards:
            deck.push_card(card)
        print(f"{len(cards)} return from the buffer to the deck")
        for p in game_manager.players:
            p.clear_selected()
            p.clear_other_selected()
    return end_turn

class PlayerDrawStartCardJob(PlayerGameJob):
    def __init__(self, deck , player, duration = 1):
        super().__init__(PlayerOptions.DRAW_START_5_CARDS, player, draw_start_card_wrapper(deck, player), duration = duration)
        self.add_end_evoke_listener(lambda : player.game_manager.get_player_status(player).finish_start_5_card_draw())

class PlayerStartTurnJob(PlayerGameJob):
    def __init__(self, player, duration = 0.1):
        super().__init__(PlayerOptions.START_TURN, player, start_turn_wrapper(player),
                         duration=duration)
        self.add_start_evoke_listener(lambda : player.game_manager.get_player_status(player).reset_turn())
        self.add_end_evoke_listener(player.player_input.activate)
        self.add_end_evoke_listener(player.player_input.evaluate_situation_and_response)
        # todo: for AI, it should listen to the callback to get into moving

class StartDrawCardFromDeckJob(PlayerGameJob):
    def __init__(self, player, duration = 0.1):
        super().__init__(PlayerOptions.START_DRAW_CARD_FROM_DECK, player, lambda : None, duration = duration)
        self.add_start_evoke_listener(player.game_manager.get_player_status(player).start_draw_card_from_deck)
        self.add_end_evoke_listener(player.player_input.evaluate_situation_and_response)

class DrawCardFromDeckJob(PlayerGameJob):
    def __init__(self, player, duration = 0.1):
        deck = player.game_manager.deck
        buffer = player.game_manager.draw_card_buffer
        super().__init__(PlayerOptions.DRAW_CARD_FROM_DECK, player, draw_card_from_deck_wrapper(deck, buffer),duration)
        self.add_start_evoke_listener(player.game_manager.get_player_status(player).draw_card_from_deck_to_buffer)
        self.add_end_evoke_listener(player.player_input.evaluate_situation_and_response)

class EndDrawCardFromDeckJob(PlayerGameJob):
    def __init__(self, player, duration = 1):
        buffer = player.game_manager.draw_card_buffer
        super().__init__(PlayerOptions.END_DRAW_CARD_FROM_DECK, player, add_card_in_buffer_wrapper(buffer, player),duration)
        self.add_start_evoke_listener(player.game_manager.get_player_status(player).end_draw_card_from_deck)
        self.add_end_evoke_listener(player.player_input.evaluate_situation_and_response)

class StartDrawCardFromOtherPlayerJob(PlayerGameJob):
    def __init__(self, player, other_player, duration = 0.3):
        super().__init__(PlayerOptions.START_DRAW_FROM_OTHER_PLAYER, player, start_draw_card_from_other_player_wrapper(other_player), duration)
        self.add_start_evoke_listener(lambda : player.game_manager.get_player_status(player).start_draw_from_other_player(other_player)) #todo
        self.add_end_evoke_listener(player.player_input.evaluate_situation_and_response)

class DrawFromOtherPlayerJob(PlayerGameJob):
    def __init__(self, player, other_player, duration = 1):
        super().__init__(PlayerOptions.DRAW_CARD_FROM_PLAYER, player, draw_card_from_other_player_wrapper(player, other_player),duration)
        self.add_start_evoke_listener(
            lambda: player.game_manager.get_player_status(player).draw_from_other_player())
        self.add_end_evoke_listener(player.player_input.evaluate_situation_and_response)

class SelectFromOtherPlayerJob(PlayerGameJob):
    def __init__(self, player, other_player, card, duration = 0.1):
        super().__init__(PlayerOptions.SELECT_CARD_FROM_OTHER_PLAYER, player, select_card_from_other_player_wrapper(other_player, card), duration)
        self.add_start_evoke_listener(player.game_manager.get_player_status(player).select_from_other_player)
        self.add_end_evoke_listener(player.player_input.evaluate_situation_and_response)

class EndDrawFromOtherPlayerJob(PlayerGameJob):
    def __init__(self, player, duration = 0.1):
        super().__init__(PlayerOptions.END_DRAW_FROM_OTHER_PLAYER, player, (lambda : print('End draw from other player')),duration)
        self.add_start_evoke_listener(player.game_manager.get_player_status(player).end_draw_from_other_player)
        self.add_end_evoke_listener(player.player_input.evaluate_situation_and_response)

class SelectCardFromCollectionJob(PlayerGameJob):
    def __init__(self, player, card, duration = 0.1):
        super().__init__(PlayerOptions.SELECT_CARD_FROM_COLLECTION, player, lambda : player.mark_card_selected(card), duration = duration)
        self.add_start_evoke_listener(player.game_manager.get_player_status(player).start_select_valid_group)
        self.add_end_evoke_listener(player.player_input.evaluate_situation_and_response)

class DeselectCardFromCollectionJob(PlayerGameJob):
    def __init__(self, player, card, duration = 0.1):
        super().__init__(PlayerOptions.DESELECT_CARD_FROM_COLLECTION, player, lambda : player.mark_card_unselected(card), duration = duration)
        self.add_start_evoke_listener(player.game_manager.get_player_status(player).start_select_valid_group)
        self.add_end_evoke_listener(player.player_input.evaluate_situation_and_response)

class DiscardSelectedFromCollectionJob(PlayerGameJob):
    def __init__(self, player, duration = 1):
        super().__init__(PlayerOptions.DISPOSE_VALID_GROUP, player, discard_selected_wrapper(player), duration=duration)
        self.add_start_evoke_listener(player.game_manager.get_player_status(player).dispose_selected_valid_group)
        self.add_start_evoke_listener(player.game_manager.deck.shuffle)
        self.add_start_evoke_listener(lambda: player.game_manager.check_winner(player))
        self.add_end_evoke_listener(player.player_input.evaluate_situation_and_response)
        
class EndTurnJob(PlayerGameJob):
    def __init__(self, player, duration = 1):
        super().__init__(PlayerOptions.PASS, player, end_turn_wrapper(player), duration = duration)
        self.add_start_evoke_listener(player.game_manager.get_player_status(player).end_turn)
        self.add_start_evoke_listener(player.player_input.deactivate)
        self.add_end_evoke_listener(player.game_manager.start_next_player_turn)

class JobEvokeSystem:
    def __init__(self):
        import queue
        self._job_queue = queue.Queue()
        self._current_job = None
        self.paused = False

    def push_job(self, job):
        self._job_queue.put(job)

    def update(self, dt):
        if self.paused:
            return
        if self._current_job is not None:
            self._current_job.update(dt)
            if self._current_job.finished():
                self._current_job.end_evoke()
                self._current_job = None
        if self._current_job is None:
            while not self._job_queue.empty():
                self._current_job = self._job_queue.get()
                self._current_job.evoke()
                if self._current_job.finished():
                    self._current_job.end_evoke()
                    self._current_job = None
                else:
                    break

class GamePlayerStatus:

    def __init__(self, player):
        self._player = player
        self._start_5_card_drawn = False
        self._turn_end = True

        self._start_draw_from_deck = False
        self._num_card_drawn_from_deck = 0
        self._end_draw_from_deck = False

        self._start_draw_from_other_player = False
        self._draw_from_other_player = False
        self._select_from_other_player = False
        self._other_player = None
        self._end_draw_from_other_player = False

        self._start_select_valid_group = False
        self._end_select_valid_group = False

    @property
    def num_card_drawn_from_deck(self):
        return self._num_card_drawn_from_deck

    @property
    def turn_end(self):
        return self._turn_end

    @property
    def start_draw_from_deck(self):
        return self._start_draw_from_deck

    @property
    def end_draw_from_deck(self):
        return self._end_draw_from_deck

    @property
    def draw_from_other_player_start(self):
        return self._start_draw_from_other_player

    @property
    def have_drawn_from_other_player(self):
        return self._draw_from_other_player

    @property
    def have_selected_from_other_player(self):
        return self._select_from_other_player

    @property
    def draw_from_other_player_end(self):
        return self._end_draw_from_other_player

    def finish_start_5_card_draw(self):
        self._start_5_card_drawn = True
        print ("Player Finished Start Draw In Status")

    def reset_turn(self):
        self._turn_end = False

        self._start_draw_from_deck = False
        self._num_card_drawn_from_deck = 0
        self._end_draw_from_deck = False

        self._start_draw_from_other_player = False
        self._draw_from_other_player = False
        self._select_from_other_player = False
        self._other_player = None
        self._end_draw_from_other_player = False

        self._start_select_valid_group = False
        self._end_select_valid_group = False

    def end_turn(self):
        self._turn_end = True

    def start_draw_card_from_deck(self):
        self._start_draw_from_deck = True

    def draw_card_from_deck_to_buffer(self):
        self._num_card_drawn_from_deck += 1

    def end_draw_card_from_deck(self):
        self._end_draw_from_deck = True

    def start_select_valid_group(self):
        self._start_select_valid_group = True

    def dispose_selected_valid_group(self):
        self._start_select_valid_group = True

    def start_draw_from_other_player(self, other_player):
        self._start_draw_from_other_player = True
        self._other_player = other_player

    def select_from_other_player(self):
        self._select_from_other_player = True

    def draw_from_other_player(self):
        self._draw_from_other_player = True

    def end_draw_from_other_player(self):
        self._end_draw_from_other_player = True

    @property
    def player(self):
        return self._player

    def check_player_job_valid(self, player_game_job):
        if isinstance(player_game_job, PlayerDrawStartCardJob):
            return not self._start_5_card_drawn
        if isinstance(player_game_job, PlayerStartTurnJob):
            player = player_game_job.player
            game_manager = player.game_manager
            players = game_manager.players
            if game_manager.player_turn < 0:
                return True
            player_index = players.index(player)
            if (game_manager.player_turn + 1) % len(players) == player_index:
                curr_player = players[game_manager.player_turn]
                if game_manager.get_player_status(curr_player).turn_end:
                    return True
            return False
        if isinstance(player_game_job, StartDrawCardFromDeckJob):
            print(
                f"start: {self._start_draw_from_deck}, other: {self._start_draw_from_other_player}")
            return not self._start_draw_from_deck
        if isinstance(player_game_job, DrawCardFromDeckJob):
            if self._start_draw_from_deck and not self._end_draw_from_deck:
                if self._num_card_drawn_from_deck < 3:
                    return True
            return False
        if isinstance(player_game_job, EndDrawCardFromDeckJob):
            if self._start_draw_from_deck and not self._end_draw_from_deck:
                return True
            return False
        if isinstance(player_game_job, StartDrawCardFromOtherPlayerJob):
            return not self._start_draw_from_other_player
        if isinstance(player_game_job, SelectFromOtherPlayerJob):
            return self._start_draw_from_other_player and (not self._draw_from_other_player) and self._other_player.card_count() > 0
        if isinstance(player_game_job, DrawFromOtherPlayerJob):
            return self._start_draw_from_other_player and self._select_from_other_player and (not self._draw_from_other_player)
        if isinstance(player_game_job, EndDrawFromOtherPlayerJob):
            return self._draw_from_other_player and (not self._end_draw_from_other_player)
        if isinstance(player_game_job, SelectCardFromCollectionJob):
            return True
        if isinstance(player_game_job, DeselectCardFromCollectionJob):
            player = player_game_job.player
            return player.selected_count() > 0
        if isinstance(player_game_job, DiscardSelectedFromCollectionJob):
            player = player_game_job.player
            selected_as_list = player.selected_as_list()
            return CollectionOfCards.static_is_valid_group(selected_as_list)
        if isinstance(player_game_job, EndTurnJob):
            return True
        return False

class GameProcedure(Enum):
    GAME_START = 0
    PLAYING = 1
    WON = 2
    LOSE = 3

class GameManager(GameLogicActor):
    def __init__(self, game_instance):
        super().__init__(self)
        self._player_status_dict = {}
        self._deck = Deck()
        self._draw_card_buffer = DrawCardBuffer()
        self._job_manager = JobEvokeSystem()
        self.game_procedure = GameProcedure.GAME_START
        self.game_instance = game_instance
        self.player_turn = -1
        game_instance.add_actor(self)
        self._game_result_listeners = []

    @property
    def deck(self):
        return self._deck

    @property
    def draw_card_buffer(self):
        return self._draw_card_buffer

    @property
    def players(self):
        return [player for player in self._player_status_dict.keys()]

    def get_player_status(self, player):
        return self._player_status_dict[player]

    def add_player(self, player):
        self._player_status_dict[player] = GamePlayerStatus(player)

    def add_actor(self, actor):
        self.game_instance.add_actor(actor)

    def add_game_result_listener(self, game_result_listener):
        self._game_result_listeners.append(game_result_listener)

    def receive_request(self, job):
        if self.check_request(job):
            self._job_manager.push_job(job)
            # todo : change status when it starts
        else:
            print(type(job))
            print("denied")

    def check_request(self, job):
        # todo : some requests are not acceptable
        if isinstance(job, PlayerGameJob):
            player = job.player
            status = self._player_status_dict[player]
            return status.check_player_job_valid(job)
        return True

    def start(self):
        print("start")

    def update(self, dt):
        self._job_manager.update(dt)

    def start_next_player_turn(self):
        next_player_index = (self.player_turn + 1) % len(self._player_status_dict)
        player = self.players[next_player_index]
        return player.start_turn()

    def check_winner(self, player: PlayerAgent):
        if player.card_count() == 0:
            for game_result_listener in self._game_result_listeners:
                game_result_listener(player)
            self._job_manager.paused = True

class Game:
    def __init__(self, num_of_players=2):
        self.clock = pygame.time.Clock()
        self.update_object_set = set()
        self.game_end = False
        self.game_manager = GameManager(self)

    def add_actor(self, game_logic_actor):
        if game_logic_actor not in self.update_object_set:
            self.update_object_set.add(game_logic_actor)
            game_logic_actor.start()

    def update(self):
        dt = self.clock.tick(60)/1000
        for o in self.update_object_set:
            o.update(dt)

    def main(self):
        player_1 = PlayerAgent(self.game_manager, AIPlayerInput())
        self.game_manager.add_player(player_1)
        player_2 = PlayerAgent(self.game_manager, AIPlayerInput())
        self.game_manager.add_player(player_2)
        player_3 = PlayerAgent(self.game_manager, AIPlayerInput())
        self.game_manager.add_player(player_3)
        player_1.draw_start_cards()
        player_2.draw_start_cards()
        player_3.draw_start_cards().add_end_evoke_listener(self.game_manager.start_next_player_turn)
        while not self.game_end:
            self.update()
            pygame.time.delay(30)

if __name__ == "__main__":
    Game().main()
    # deck = Deck()
    # deck.print_deck()

    # c = CollectionOfCards(["red 5", "red 7", "red 9"])
    # c2 = CollectionOfCards(["red 6", "red 8"])
    # candidate_card_list = probability_of_valid_group([c, c2])
    # print(candidate_card_list)