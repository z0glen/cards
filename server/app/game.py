import random
import string
import json

from app import app
from app.models import CallCard, ResponseCard

class Game:
    def __init__(self):
        self.id = self.generate_game_code()
        self.deck = {}
        self.state = 'lobby'
        self.black_card = None
        self.players = {}
        self.judge = None
        self.played_cards = {}
        self.card_group_mapping = {}
        self.judge_num = 0
        self.round_num = 1
        self.history = {}  # an int to string dict

        self.load_cards()

    @staticmethod
    def generate_game_code():
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))

    def load_cards(self):
        # TODO: use struct with more efficient front of list pops
        self.deck['calls'] = [card.to_dict() for card in CallCard.query.all()]
        random.shuffle(self.deck['calls'])
        self.deck['responses'] = [card.to_dict() for card in ResponseCard.query.all()]
        random.shuffle(self.deck['responses'])

    def to_json(self):
        ps = {}
        for name, player in self.players.items():
            ps[name] = player.min_to_json()
        obj = {
            "id": self.id,
            "state": self.state,
            "black_card": self.black_card,
            "players": ps,
            "history": self.history
        }
        return json.dumps(obj)

    def draw_black_card(self):
        self.black_card = self.deck['calls'].pop(0)
        self.deck['calls'].append(self.black_card)

    def assign_judge(self):
        for name, p in self.players.items():
            if p.judge_num == self.judge_num:
                self.judge = name
        self.reset_judging()
        if not self.judge:
            self.judge = list(self.players.keys())[0]
        self.players[self.judge].is_judge = True
        self.players[self.judge].can_play_card = False

    def reset_judging(self):
        for name, p in self.players.items():
            p.is_judge = False

    def find_player_by_name(self, name):
        for n, p in self.players.items():
            if n == name:
                return p
        return None

    def has_all_played(self):
        for n, p in self.players.items():
            if p.can_play_card:
                app.logger.debug("Player " + p.name + " has not finished playing")
                return False
        return True

    def find_card_by_id(self, card_id):
        for card in self.deck['responses']:
            if card.id == card_id:
                return card

    def award_point(self, group_id):
        for group, cards in self.played_cards.items():
            if group == group_id:
                name = self.card_group_mapping[group]
                p = self.find_player_by_name(name)
                if p:
                    p.score += 1
                card_text = '; '.join([c['text'][0] for c in cards])
                black_card_text = '_____'.join(self.black_card['text'])
                self.history[self.round_num] = name + " has won the card '" + black_card_text + "' with the card(s): " + card_text
                return {'player': name, 'cards': cards}

    def end_round(self):
        self.played_cards = {}
        self.card_group_mapping = {}
        for name, p in self.players.items():
            p.is_judge = False
            p.playedCard = []
            p.can_play_card = True
            p.handle_cards()
        if self.judge_num >= len(self.players) - 1:
            self.judge_num = 0
        else:
            self.judge_num += 1
        self.round_num += 1
        self.assign_judge()
        self.draw_black_card()

    def reset_round(self):
        self.played_cards = {}
        self.card_group_mapping = {}
        for name, p in self.players.items():
            p.is_judge = False
            p.playedCard = []
            p.can_play_card = True
            p.handle_cards()
        self.assign_judge()
        self.draw_black_card()

    def add_player(self, player):
        self.players[player.name] = player
        player.judge_num = len(self.players) - 1

    def remove_player(self, sid):
        target = None
        for p in self.players.values():
            if p.sid == sid:
                target = p.name
        del self.players[target]
        self.reset_judge_order()

    def is_valid_username(self, name):
        for n in self.players.keys():
            if n == name:
                return False
        return True

    def update_played_cards(self, name, cards):
        app.logger.debug("update_played_cards")
        ind = 'card-group-' + str(len(self.played_cards))
        self.card_group_mapping[ind] = name
        self.played_cards[ind] = cards
        app.logger.debug(self.card_group_mapping)
        app.logger.debug(self.played_cards)

    def shuffle_played_cards(self):
        app.logger.debug("shuffling played cards")
        card_group_list = list(self.played_cards.keys())
        random.shuffle(card_group_list)
        list_form = dict([(card_group, self.played_cards[card_group]) for card_group in card_group_list])
        app.logger.debug(list_form)
        self.played_cards = list_form

    def reset_judge_order(self):
        for idx, p in enumerate(self.players.values()):
            p.judge_num = idx
