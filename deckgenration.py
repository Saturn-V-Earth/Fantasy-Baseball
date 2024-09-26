import time

class DeckShuffler:
    def __init__(self, deck=None):
        self.seed = int(time.time() * 1000)  # Initialize the seed
        self.deck = deck if deck is not None else self.create_default_deck()

    def custom_random_number(self, min_value, max_value):
        self.seed = (self.seed * 1103515245 + 12345) & 0x7FFFFFFF
        random_value = self.seed % (max_value - min_value + 1)
        return min_value + random_value

    def riffle_shuffle(self):
        if len(self.deck) <= 1:
            return self.deck

        split_point = self.custom_random_number(1, len(self.deck) - 1)
        left_half = self.deck[:split_point]
        right_half = self.deck[split_point:]

        shuffled_deck = []

        # Simulate the riffle shuffle by interleaving the two halves
        while left_half or right_half:
            if left_half and right_half:
                if self.custom_random_number(0, 1) == 0:
                    shuffled_deck.append(left_half.pop(0))
                else:
                    shuffled_deck.append(right_half.pop(0))
            elif left_half:
                shuffled_deck.append(left_half.pop(0))
            elif right_half:
                shuffled_deck.append(right_half.pop(0))

        self.deck = shuffled_deck
        return self.deck

    def overhand_shuffle(self):
        shuffled_deck = []
        while self.deck:
            num_cards = self.custom_random_number(1, min(5, len(self.deck)))
            shuffled_deck = self.deck[:num_cards] + shuffled_deck
            self.deck = self.deck[num_cards:]
        self.deck = shuffled_deck
        return self.deck

    def smoosh_shuffle(self):
        for i in range(len(self.deck)):
            j = self.custom_random_number(0, len(self.deck) - 1)
            self.deck[i], self.deck[j] = self.deck[j], self.deck[i]
        return self.deck

    def mega_shuffle(self):
        shuffle_funcs = [self.riffle_shuffle, self.overhand_shuffle, self.smoosh_shuffle]
        for _ in range(3):
            for shuffle in sorted(shuffle_funcs, key=lambda _: self.custom_random_number(0, 2)):
                shuffle()
        return self.deck

    def create_default_deck(self):
        deck = []
        deck.extend(["ball"] * 10)
        deck.extend(["strike"] * 10)
        deck.extend(["fly_out"] * 2)
        deck.extend(["foul_ball"] * 2)
        deck.extend(["out_double_play_first"] * 1)
        deck.extend(["out_double_play_second"] * 1)
        deck.extend(["foul_out"] * 1)
        deck.extend(["hit_by_pitcher"] * 1)
        deck.extend(["stolen_base"] * 1)
        deck.extend(["balk"] * 1)
        deck.extend(["home_run"] * 1)
        deck.extend(["triple"] * 1)
        deck.extend(["double"] * 2)
        deck.extend(["single"] * 2)
        self.deck = deck
        return self.deck

    def get_deck(self):
        return self.deck

    def shuffle_and_get_deck(self):
        return self.mega_shuffle()

# Example usage:
deck_shuffler = DeckShuffler()
shuffled_deck = deck_shuffler.shuffle_and_get_deck()
print(f"Shuffled deck: {shuffled_deck}")
