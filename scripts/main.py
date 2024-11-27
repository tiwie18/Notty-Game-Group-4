import re

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


class CollectionOfCards:
    def __init__(self, string_list):
        self.collection = []
        for card_string in string_list:
            color, number = card_string.split()
            self.collection.append(Card(color, int(number)))

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


# There are 2 possible solutions to this problem
# one is to try to add every card in the deck to the collection of the first player,
# and check whether a new valid group is formed (only need to check 1 color and 1 number)
# another is to find all the qualified cards beforehand, and calculate the portion of these cards in the deck
# In some cases the second one is more sufficient
# for example, Player 1 have 2 card in his collection, I only have to check whether there is a card in the middle or
# of the same number but different colors, in which case I only need to search 3 unique cards in the deck,
# but using the first method will still check all the cards in the deck
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





if __name__ == "__main__":
    c = CollectionOfCards(["red 5", "red 7", "red 9"])
    c2 = CollectionOfCards(["red 6", "red 8"])
    candidate_card_list = probability_of_valid_group([c, c2])
    print(candidate_card_list)