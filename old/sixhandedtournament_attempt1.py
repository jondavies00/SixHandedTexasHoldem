
from typing import Type
from poker import Hand, Card, Rank, Combo, Suit, Range
from random import shuffle, randint, uniform, choice
from itertools import cycle
from operator import attrgetter, truediv

score_to_rank = {1:'high card', 2:'pair', 3:'two pair', 4:'three of a kind', 5:'straight', 6:'flush', 7:'full house', 8:'four of a kind', 9:'straight flush', 10:'royal flush'}


class Tournament():

    def __init__(self, bb_doubling_speed, starting_chips=20000):
        p1, p2, p3, p4, p5, p6 = RangePlayer('Player 1'), ManualPlayer('Player 2'), RandomPlayer('Player 3'), RandomPlayer('Player 4'), RandomPlayer('Player 5'), RandomPlayer('Player 6')
        self.players = [p1, p2, p3, p4, p5, p6]
        self.players_in_hand = []
        shuffle(self.players)
        self.table_positions = cycle(self.players)
        self.player_pool = self.table_positions
        self.deck = list(Card)
        self.pot = 0
        self.start_chips = starting_chips
        for p in self.players:
            p.stack = self.start_chips
        self.bb, self.sb = 10, 5
        self.tournament_over = False
        self.hand_count, self.showdown_count = 0, 0
        self.community_cards,  self.chip_history = [], []
        self.winner = None
        self.win_percents = {1:0, 2:0, 3:0, 4:0, 5:0, 6:0, 7:0, 8:0, 9:0, 10:0}
        self.bb_doubling_speed = bb_doubling_speed
        self.human_player = p2

    def begin(self):
        button = 0
        while not self.is_tournament_over():
            #new round
            
            print('HAND #%i' % self.hand_count)
            if (self.hand_count+2) % self.bb_doubling_speed == 0:
                self.bb *= 2
                self.sb = self.bb / 2
            stacktotal = 0
            for p in self.players:
                print('%s has stack size of %i.' % (p.name, p.stack))
                stacktotal += p.stack
            print('stack total = %i, should be %i' % (stacktotal, self.start_chips * len(self.players)))
            if stacktotal != self.start_chips * len(self.players):
                pass
                print('error in chips')
            self.begin_action(button)
            button += 1
            self.hand_count += 1

    def get_hand_count(self):
        return self.hand_count + 1

    def get_winner(self):
        return self.winner

    def is_tournament_over(self):
        out = 0
        for p in self.players:
            if p.stack == 0:
                out += 1
        if out == 5:
            self.winner = [w for w in self.players if w.stack != 0][0]
            
            return True
        else:
            return self.tournament_over

    def begin_action(self, button):
        positions = {1:'Dealer',2:'Small blind',3:'Big blind',4:'UTG',5:'UTG+1',6:'Cutoff'}
        self.chip_history.append(self.update_player_chips())
        self.pot = 0
        self.deck = list(Card)
        self.community_cards =  []
        self.new_hand()
        self.populate_player_pool(button, True)

        if self.hand_count != 0:
            for i in range((self.hand_count % 6)):
                next(self.player_pool)

        for i in range(1, len(self.players_in_hand) + 1):
            player = next(self.player_pool)
            player.position = positions[i]
            if player.position == 'Big blind':
                self.pot += self.bb
                player.add_to_pot(self.bb)
            elif player.position == 'Small blind':
                self.pot += self.sb
                player.add_to_pot(self.sb)

        print('Shuffling')
        shuffle(self.deck)
        print('Dealing')
        for i in range(1, len(self.players_in_hand) + 1):

            to_deal = next(self.player_pool)
            to_deal.deal(self.deck.pop(), self.deck.pop())
            if to_deal == self.human_player:
                print(to_deal.name + ' is ' + to_deal.position + ', dealt: ' + str(to_deal.hand), end='')
            print('')
        
        next(self.player_pool)
        next(self.player_pool)
        next(self.player_pool)
        print('Beginning action. Pot = ' + str(self.pot))
        #preflop
        self.begin_round_stages(0, button)

    def get_player_history(self, p_name):
        players_chip_history = []
        player = [p for p in self.players if p.name == p_name][0]

        players_chip_history = [h[player] for h in self.chip_history]
        return players_chip_history
                
    def update_player_chips(self):
        player_chips = {}
        for p in self.players:
            player_chips[p] = p.stack
        
        return player_chips

    def begin_round_stages(self, p_round, button):
        showdown = False
        while not showdown:
            is_preflop = False
            if p_round == 0:
                #preflop
                is_preflop = True
            elif p_round == 1:
                #flop
                print('FLOP: ')
                self.community_cards = [self.deck.pop() for __ in range(3)]
            elif p_round == 2 or p_round == 3:
                #turn
                if p_round == 2:
                    pass
                    print('TURN: ')
                else:
                    pass
                    print('RIVER: ')
                self.community_cards.append(self.deck.pop())
            else:
                showdown = True
                break
            if not is_preflop:
                pass
                print('')
                print('%s: ' % p_round, end='')
                print(' '.join(str(c) for c in self.community_cards))
                print('')
            self.action_loop(is_preflop)
            self.populate_player_pool(button)
            if len(self.players_in_hand) == 1:
                self.hand_won(self.players_in_hand[0])
                break
            elif self.all_in_showdown():
                if p_round == 0:
                    self.community_cards.append(self.deck.pop())
                    self.community_cards.append(self.deck.pop())
                    self.community_cards.append(self.deck.pop())
                    self.community_cards.append(self.deck.pop())
                    self.community_cards.append(self.deck.pop())
                elif p_round == 1:
                    self.community_cards.append(self.deck.pop())
                    print('TURN: %s' % ' '.join(str(c) for c in self.community_cards))
                    self.community_cards.append(self.deck.pop())
                    print('RIVER: %s'% ' '.join(str(c) for c in self.community_cards))
                elif p_round == 2:
                    self.community_cards.append(self.deck.pop())
                    print('RIVER: %s'% ' '.join(str(c) for c in self.community_cards))
                showdown = True
                break
            p_round += 1
        if showdown:
            self.calculate_showdown()

        # if p_round == 'FLOP':
        #     next_round = 'TURN'
        # elif p_round == 'TURN':
        #     next_round = 'RIVER'
        # else:
        #     next_round = 'SHOWDOWN'

        # if p_round == 'SHOWDOWN':
        #     #print(p_round)
        #     p_left = [p for p in self.players_in_hand if not p.out]

        #     winners, score = self.showdown(p_left)
        #     if len(winners) == 1:
        #         #print('%s wins with hand: %s %s' % (winners[0].name, score_to_rank[score], winners[0].winning_hand))
        #         winners[0].stack += self.pot
                
        #         for p in p_left:
        #             if p.stack == 0 and p != winners[0]:
        #                 p.out_of_tournament = True
        #     else:
        #         # TODO: Must have a way to deal with side pots
        #         #print('chop pot!')
        #         each_gain = self.pot / len(p_left)
        #         if int(each_gain) < each_gain:
        #             flip_for = round(each_gain) - int(each_gain)
        #         else:
        #             flip_for = 0
        #         flip = randint(1, len(p_left))
        #         for p in winners:
        #             if winners.index(p) == flip:
        #                 p.stack += flip_for
        #             p.stack += int(each_gain)
        #         print(winners)
        # else:
        #     print('')
        #     print('%s: ' % p_round, end='')
        #     if p_round == 'FLOP':
        #         self.community_cards = [self.deck.pop() for __ in range(3)]
        #     else:
        #         self.community_cards.append(self.deck.pop())
        #     print(' '.join(str(c) for c in self.community_cards))
        #     print('')
        #     total_money = 0
        #     for p in self.players:
        #         total_money += p.stack
        #     print(total_money)
        #     self.action_loop()
        #     self.populate_player_pool()
        #     if len(self.players_in_hand) == 1:
        #         # the winner will be the next to act
        #         self.hand_won(self.players_in_hand[0])
        #     elif self.all_in_showdown():
        #         if p_round == 'FLOP':
        #             self.community_cards.append(self.deck.pop())
        #             print('TURN: %s' % ' '.join(str(c) for c in self.community_cards))
        #             self.community_cards.append(self.deck.pop())
        #             print('RIVER: %s'% ' '.join(str(c) for c in self.community_cards))
        #         elif p_round == 'TURN':
        #             self.community_cards.append(self.deck.pop())
        #             print('RIVER: %s'% ' '.join(str(c) for c in self.community_cards))
        #         self.begin_round_stages('SHOWDOWN')
        #     else:
        #         self.begin_round_stages(next_round)

    def calculate_showdown(self):

        p_left = [p for p in self.players_in_hand if not p.out]

        winners, score = self.showdown(p_left)
        if len(winners) == 1:
            print('%s wins with hand: %s %s' % (winners[0].name, score_to_rank[score], winners[0].winning_hand))
            winners[0].stack += self.pot
            
            for p in p_left:
                if p.stack == 0 and p != winners[0]:
                    p.out_of_tournament = True
        else:
            # TODO: Must have a way to deal with side pots
            print('chop pot!')
            each_gain = self.pot / len(p_left)
            if int(each_gain) < each_gain:
                flip_for = round(each_gain) - int(each_gain)
            else:
                flip_for = 0
            flip = randint(1, len(p_left))
            for p in winners:
                if winners.index(p) == flip:
                    p.stack += flip_for
                p.stack += int(each_gain)
            print(winners)

    def all_in_showdown(self):
        all_in = 0
        for p in self.players_in_hand:
            if p.all_in:
                all_in +=1
        if len(self.players_in_hand) - all_in < 2:
            return True
        else:
            return False

    def populate_player_pool(self, button, newround=False):
        
        self.players_in_hand = []
        out_of_tournament = 0
        for p in self.players:
            p.on_table = 0
            if not p.out_of_tournament:
                if not p.out or newround:
                    self.players_in_hand.append(p)
            else:
                out_of_tournament += 1
        if out_of_tournament == 5:
            self.tournament_over = True
        else:
            self.player_pool = cycle(self.players_in_hand)
            next_to_act = next(self.player_pool)
            # if newround:
            #     for i in range(button):
            #         next(self.player_pool)
                
            if self.players_in_hand[0].position == 'Dealer' and not newround:
                next(self.player_pool)

    def new_hand(self):
        for p in self.players:
            if p.stack != 0:
                p.out = False

    def action_loop(self, preflop=False):
        if preflop:
            current_bet = self.bb
        else:
            current_bet = 0
        min_bet = self.bb

        action_left = len(self.players_in_hand)
        out = 6 - action_left
        all_in = 0
        to_return = 0
        while action_left > 0:
            player_to_act = next(self.player_pool)
        
            if not player_to_act.out and player_to_act.stack > 0:
                print('%s to act...' % player_to_act.position)
                
                action_type = player_to_act.get_action_type(current_bet, preflop)
                amount = player_to_act.get_action_amount(action_type, min_bet, current_bet)

                if action_type == 1:
                    #fold
                    player_to_act.out = True
                    action_left -=1
                    out+=1
                    print('Fold. stack = %i' % player_to_act.stack)
                elif action_type == 2:
                    #call
                    action_left -= 1
                    amount_to_call = current_bet - player_to_act.on_table
                    if amount_to_call >= player_to_act.stack:
                        #TODO: money needs to go back to raiser if caller doesn't have enough
                        
                        to_return += current_bet - player_to_act.stack

                        player_stack = player_to_act.stack
                        player_to_act.add_to_pot(player_stack)
                        self.pot += player_stack
                    else:
                        player_to_act.add_to_pot(amount_to_call)
                        self.pot += amount_to_call
                    print('Call. Pot = %i, stack = %i' % (self.pot, player_to_act.stack))
                elif action_type == 3:
                    #check
                    action_left -= 1
                    print('Check. stack = %i' % player_to_act.stack)
                elif action_type == 4:
                    #bet
                    better = player_to_act
                    action_left = 5 - (out)
                    player_to_act.add_to_pot(amount)
                    current_bet = amount
                    self.pot += current_bet
                    print('Bet, size = %i, pot = %i, stack = %i' % (amount, self.pot, player_to_act.stack))
                elif action_type == 5:
                    better = player_to_act
                    #raise
                    action_left = 5 - (out)
                    # amount raiser wants to raise it to subtract what they have in the pot
                    raise_amount = amount - player_to_act.on_table
                    self.pot += raise_amount
                    player_to_act.add_to_pot(raise_amount)
                    current_bet = amount
                    
                    print('Raise, size %i, pot = %i, stack = %i' % (amount, self.pot, player_to_act.stack))
                else:
                    raise ValueError('invalid action')
            if player_to_act.stack == 0:
                player_to_act.all_in = True
                all_in +=1
            if len(self.players_in_hand) - all_in < 2:
                break
            if out == 5:
                break
            if len(self.players_in_hand) - all_in == 1:
                #if everyone has gone all in to call bar 1 person who has enough to chips to cover, the amount they have on the table should be returned6
                better.add_to_stack(to_return)
        print('Round over, %s players left, %i in the pot' % (str(6 - out), self.pot))
        
    def hand_won(self, player):
        print('%s wins the hand' % player.position)
        
        player.add_to_stack(self.pot)

    def showdown(self, players):
        score_to_kicker = {1:4,2:3,3:1,4:2,5:0,6:4,7:0,8:1,9:0}
        player_score = {}
        if len(players) == 0:
            raise ValueError('No players given for showdown')
        
        for p in players:
            hole_and_community = p.get_hand() + self.community_cards
            player_score[p] = self.get_highest_combo(hole_and_community)
            self.showdown_count +=1
            p_score = player_score[p]
        p_win = max(player_score, key=player_score.get)
        
        # if there is more than one person with the winning hand, check for highest card
        if sum(value == player_score[p_win] for value in player_score.values()) > 1:
            
            winner_score = max(player_score.values())
            kickers_to_check = score_to_kicker[winner_score]
            #list of players also with that hand
            winners = [p for p in player_score.keys() if player_score[p]==p_score]

            ### reworking
            same_hand = False
            same_handed = []
            #calculate the highest card that makes each winning hand a winner
            for winner in winners:
                cards = winner.get_hand() + self.community_cards
                if p_score == 1:
                    winner.win_combo = max(cards).rank
                    winner.winning_hand = winner.win_combo
                elif p_score == 2:
                    winner.win_combo = max(self.get_x_of_a_kind(cards, 2))
                    winner.winning_hand = winner.win_combo
                elif p_score == 3:
                    pairs = self.get_two_pair(cards)
                    pairs.sort()
                    pairs.reverse()
                    new_pairs =[pairs[0], pairs[1]]
                    winner.win_combo = new_pairs
                    winner.winning_hand = winner.win_combo
                elif p_score == 4:
                    winner.win_combo = max(self.get_x_of_a_kind(cards, 3))
                    winner.winning_hand = winner.win_combo
                elif p_score == 5:
                    winner.win_combo = max(self.get_straight(cards))
                    winner.winning_hand = winner.win_combo
                elif p_score == 6:
                    winner.win_combo = max(self.get_flush(cards))
                    winner.winning_hand = winner.win_combo
                elif p_score == 7:
                    #like two pair, return list. when comparing
                    winner.win_combo = self.get_full_house(cards)
                    winner.winning_hand = winner.win_combo
                elif p_score == 8:
                    #foak
                    winner.win_combo = max(self.get_x_of_a_kind(cards, 4))
                    winner.winning_hand = winner.win_combo
                elif p_score == 9:
                    winner.win_combo = max(self.get_straight(cards))
                    winner.winning_hand = winner.win_combo
                else:
                    raise ValueError('Invalid p_score')

            largest_combo = max(winners, key=attrgetter('win_combo')).win_combo
            for w in winners:
                if w.win_combo == largest_combo:
                    same_handed.append(w)
            if len(same_handed) > 1 and kickers_to_check != 0:
                if len(same_handed) == 0:
                    raise ValueError('List of players with same winning hand not populated.')
                #check kickers
                check_kickers = []
                highest = False
                player_win_combo = {}
                current_kickers = set()
                cards_checked = set()
                kickers_checked = 0
                
                if kickers_to_check == 0:
                    raise ValueError('shouldnt be here')
                while not highest:
                    current_kickers = set()
                    player_win_combo = {}
                    for p in same_handed:
                        #remove the 'winning' (same) combo 
                        
                        # only with two pair does a win combination contain two cards
                        # In this case, they will be equal
                        check_ranks = self.cards_to_ranks(self.community_cards + p.get_hand())
                        check_kickers = []
                        
                        
                        for r in check_ranks:
                            if r not in cards_checked:
                                if isinstance(p.win_combo, list):
                                    #if the win combo is a 2 pair list
                                    if r not in p.win_combo:
                                        check_kickers.append(r)
                                    else:
                                        cards_checked.add(r)
                                elif r != p.win_combo:
                                    check_kickers.append(r)
                                else:
                                    cards_checked.add(r)
                        
                        if len(check_kickers) != 0:
                            #no more kickers to check
                            
                            p.win_combo = max(check_kickers)
                            player_win_combo[p] = max(check_kickers)
                            current_kickers.add(max(check_kickers))
                        else:
                            draw = True
                            p_win = same_handed
                            return p_win, winner_score
                    if len(current_kickers) == 0:
                        raise ValueError('No kickers left to check, should have been caught in previous if statement.')
                    if sum(value == max(current_kickers) for value in player_win_combo.values()) == 1:    
                        highest = True
                        p_win = max(player_win_combo, key=player_win_combo.get)
                        return [p_win], winner_score
                    next_handed = []
                    for p in same_handed:
                        if p.win_combo == max(current_kickers):
                            next_handed.append(p)
                            cards_checked.add(p.win_combo)
                    if len(next_handed)==0:
                        raise ValueError('No players left to check kickers from...')
                    same_handed = next_handed
                    
                    kickers_checked +=1
                    if kickers_checked == kickers_to_check:
                        #if we've exhausted the number of possible kickers (highest five cards)
                        return same_handed, winner_score
                if p_win == None:
                    raise TypeError('Shits FUcked')
                return p_win, winner_score
                
            else:
                winner = same_handed
                if winner == None:
                    raise TypeError('Shits FUcked')
                else:
                    return winner, winner_score
        else:
            if [p_win] == None:
                raise ValueError('P_win cannot be empty')
            return [p_win], p_score

    def check_bigger_winner(self, players):
        for p in players:
            pass

    def cards_to_ranks(self, cards):
        return [c.rank for c in cards]

    def check_same_cards(self, players, number_of_kickers, cards_left):
        player_and_kicker = {}
        for p in players:
            player_and_kicker[p] = p.win_combo
        largest_kicker = max(player_and_kicker.values())
        if sum(value == largest_kicker for value in player_and_kicker.values()) > 1 and number_of_kickers > 0:
                # check_cards = self.community_cards + p.get_hand()
                # check_ranks = []
                # for c in check_cards:
                #     check_ranks.append(c.rank)
                others_cards = []
                for p in players:
                    others_cards.append(p.hand.first.rank)
                    others_cards.append(p.hand.second.rank)
                for p in players:
                    remove_win = []
                    #remove win should be only the players cards + community - win combo
                    #remove_win = [r for r in cards_left if r != p.win_combo and r != largest_kicker]
                    for r in cards_left:
                        if r in others_cards and (r == p.hand.first.rank or r == p.hand.second.rank):
                            remove_win.append(r)
                        elif r in others_cards and r != p.hand.first.rank:
                            pass
                        elif r in others_cards and r != p.hand.first.rank:
                            pass
                        elif r not in others_cards and r != p.win_combo and r != largest_kicker:
                            remove_win.append(r)
                    if remove_win == []:
                        draw = True
                    else:
                        draw = False
                        p.win_combo = max(remove_win)
                if not draw:
                    return self.check_same_cards(players, number_of_kickers-1, remove_win)
        else:
            if number_of_kickers == 0:
                return players
            else:
                if max(player_and_kicker, key=player_and_kicker.get) == None:
                    raise TypeError('shits fucked')
                return [max(player_and_kicker, key=player_and_kicker.get)]

    def is_royal_flush(self, cards):
        '''
        cards: seven cards composed of community and hole cards
        '''
        rf_cards = 0
        suits = [0,0,0,0]
        if self.is_flush(cards):
            flush = self.get_flush(cards)
        else:
            return False
        for c in flush: #loop 7 times
            if c.is_face:
                rf_cards += 1
            elif c.rank == Rank('T'):
                rf_cards +=1
            elif c.rank == Rank('A'):
                rf_cards +=1

        if rf_cards >= 5:
            return True
        else:
            return False

    def is_x_of_a_kind(self, cards, x):
        count = 0
        ranks = []
        for c in cards:
            ranks.append(c.rank)
        for r in ranks:
            if ranks.count(r) == x:
                return True
        return False

    def get_x_of_a_kind(self, cards, x):
        count = 0
        ranks = []
        pairs = []
        for c in cards:
            ranks.append(c.rank)
        for r in ranks:
            if ranks.count(r) == x:
                pairs.append(r)
        return pairs

    def is_straight(self, cards):
        count = 0
        ranks = []
        straight = False
        check_ace = False
        for c in cards:
            ranks.append(c.rank)
        ranks.sort()
        ranks = set(ranks)
        ranks = list(ranks)
        ranks.sort()

        for i in range(len(ranks)-1):
            if Rank.difference(ranks[i], ranks[i+1]) == 1:
                count+=1
                if count == 4:
                    straight = True
                    break
                if count == 3:
                    check_ace = True
            else:
                count = 0
        if straight:
            return True
        elif check_ace and len(ranks) >= 5:
            if ranks[0] == Rank('2') and ranks[1] == Rank('3') and ranks[2] == Rank('4') and ranks[3] == Rank('5') and Rank('A') in ranks:
                #need a way to check if there is an A2345 straight
                return True
        else:
            return False

    def get_straight(self, cards):
        ranks = []
        straight = []
        count = 0
        check_ace = False
        for c in cards:
            ranks.append(c.rank)
        ranks.sort()
        for i in range(len(ranks)-1):


            if Rank.difference(ranks[i], ranks[i+1]) == 1:
                
                if ranks[i] not in straight:
                    straight.append(ranks[i])
                straight.append(ranks[i+1])
                count += 1
            elif count == 3:
                check_ace = True
            else:
                count = 0
        if check_ace:
            if ranks[0] == Rank('2') and ranks[1] == Rank('3') and ranks[2] == Rank('4') and ranks[3] == Rank('5') and ranks[6] == Rank('A'):
                straight.append(Rank('A'))
                straight.sort()

        return straight
    
    def is_flush(self, cards):
        suits = self.count_suits(cards)
        if suits[0] >= 5 or suits[1] >= 5 or suits[2] >= 5 or suits[3] >= 5:
            return True
        else:
            return False

    def count_suits(self, cards):
        suits = [0,0,0,0]
        for c in cards:
            if c.suit == Suit('h'):
                suits[0] += 1
            elif c.suit == Suit('d'):
                suits[1] += 1
            elif c.suit == Suit('s'):
                suits[2] += 1
            else:
                suits[3] += 1
        return suits

    def get_flush(self, cards):
        if self.is_flush(cards):
            suits = self.count_suits(cards)
            for i in range(5, 8):
                if i in suits:
                    suit = suits.index(i)
            if suit == 0:
                suit = Suit('h')
            elif suit == 1:
                suit = Suit('d')
            elif suit == 2:
                suit = Suit('s')
            else:
                suit = Suit('c')
            l = [c for c in cards if c.suit == suit]
            l.sort()
            return l
        else:
            raise ValueError('error: not a flush, code broken')

    def conv_suits(self, cards):
        suits = [c.suit for c in cards]
        return suits

    def conv_rankings(self, cards):
        pass

    def is_straight_flush(self, cards):
        if self.is_flush(cards) and self.is_straight(cards):
            flush = self.get_flush(cards)
            flush_ranks = [f.rank for f in flush]
            straight_ranks = self.get_straight(cards)
            if len(set(flush_ranks) & set(straight_ranks)) >= 5:
                return True
            else:
                return False
        else:
            return False

    def is_two_pair(self, cards):
        ranks = []
        pairs = 0
        seen_ranks = []
        for c in cards:
            ranks.append(c.rank)
        for r in ranks:
            if ranks.count(r) == 2 and r not in seen_ranks:
                seen_ranks.append(r)
                pairs += 1
        if pairs >= 2:
            return True
        else:
            return False

    def get_two_pair(self, cards):
        ranks = []
        pairs = []
        seen_ranks = []
        for c in cards:
            ranks.append(c.rank)
        for r in ranks:
            if ranks.count(r) == 2 and r not in seen_ranks:
                seen_ranks.append(r)
                pairs.append(r)
        return pairs

    def is_full_house(self, cards):
        ranks=[]
        seen_ranks = []
        seen_two = False
        seen_three = False
        for c in cards:
            ranks.append(c.rank)
        for r in ranks:
            if ranks.count(r) == 2 and r not in seen_ranks:
                seen_two = True
                seen_ranks.append(r)
            elif ranks.count(r) == 3 and r not in seen_ranks:
                seen_three = True
                seen_ranks.append(r)
        return seen_two and seen_three

    def get_full_house(self, cards):
        ranks=[]
        seen_ranks = []
        seen_two = False
        seen_three = False
        full_house = []
        for c in cards:
            ranks.append(c.rank)
        for r in ranks:
            if ranks.count(r) == 2 and r not in seen_ranks:
                seen_two = True
                seen_ranks.append(r)
                full_house.append(r)
            elif ranks.count(r) == 3 and r not in seen_ranks:
                seen_three = True
                seen_ranks.append(r)
                full_house.append(r)
        return full_house

    def get_highest_combo(self, cards):
        '''
        takes seven cards and returns a number corresponding to the poker hand ranking ()
        '''
        ranking = 0
        if self.is_royal_flush(cards):
            
            ranking = 10
        elif self.is_straight_flush(cards):
            ranking = 9
        elif self.is_x_of_a_kind(cards, 4):
            ranking = 8
        elif self.is_full_house(cards):
            ranking = 7
        elif self.is_flush(cards):
            ranking = 6
        elif self.is_straight(cards):
            ranking = 5
        elif self.is_x_of_a_kind(cards, 3):
            ranking = 4
        elif self.is_two_pair(cards):
            ranking = 3
        elif self.is_x_of_a_kind(cards, 2):
            ranking = 2
        else:
            # high card
            ranking = 1
        self.win_percents[ranking] += 1
        return ranking


class Player(object):

    def __init__(self, name):
        self.name = name
        self.stack = 0
        self.hand = None
        self.position = None
        self.out = False
        self.on_table = 0
        self.win_combo = None
        self.winning_hand = None
        self.out_of_tournament = False
        self.all_in = False
        self.action_numbers = {'fold':1,'call':2,'check':3,'bet':4,'raise':5}

    def position(self, p):
        self.position = p

    def deal(self, c1, c2):
        #Combos can be compared
        self.hand = Combo.from_cards(c1, c2)

    def get_action_type(self):
        '''
        cbet: the amount the player wishes to bet
        returns: an integer between 1 and 5 which corresponds to action (fold,call,check,bet,raise) 
        '''
        return int(input('enter type: '))

    def get_action_amount(self, action, min_bet, current_bet):
        return int(input('enter amount: '))

    def add_to_pot(self, amount):
        if int(amount) > self.stack:
            amount = self.stack
            self.stack = 0
        else:
            self.stack -= amount
        print('adding %i to pot' % amount)
        self.on_table += amount

    def add_to_stack(self, amount):
        self.stack += amount

    def get_hand(self):
        c1, c2 = self.hand.first, self.hand.second
        return [c1, c2]

class ManualPlayer(Player):
    def __init__(self, name):
        super().__init__(name)
        #self.action_numbers = {'fold':1,'call':2,'check':3,'bet':4,'raise':5}
    def get_action_type(self, cbet, preflop):
        action = input('Action: ')
        return self.action_numbers[action]

    def get_action_amount(self, action, min_bet, current_bet):
        amount = input('Amount: ')
        return amount
class RandomPlayer(Player):

    def get_action_type(self, cbet, preflop):
        action_type = randint(1, 5)
        if cbet > 0:
            action_type = randint(1, 3)
            if action_type == 1:
                return 1
            if action_type == 2:
                return 2
            if action_type == 3:
                if cbet > self.stack:
                    return 2
                else:
                    return 5
        elif cbet == 0:
            if action_type == 2:
                return 3
            if action_type == 5:
                return 4
            else:
                return action_type
        elif action_type == 1:
            return 2
        else:
            return action_type


    def get_action_amount(self, action, min_bet, current_bet):
        if action == 4:
            #bet must be min bet or higher
            amount = randint(min_bet, min_bet *2)
            if amount > self.stack:
                amount = self.stack
            return amount
        elif action == 5:
            #raise must be current bet*2 or higher
            amount = randint(current_bet*2, current_bet*3)
            if amount > self.stack:
                amount = self.stack
            return amount
        else:
            return 0

class RangePlayer(Player):

    def __init__(self, name):
        super().__init__(name)
        #Here we define a range for the player
        self.hand_range = list(Range("A8o+ KTo+ QJo+ KTs+ JT+ A2s+ 22+ T9 98 87s 76s T9o 98o").combos)
        
    def get_action_type(self, cbet, preflop):
        '''
        cbet = current bet
        '''
        if preflop:
            #preflop we will bet our hands in range 3x the big blind
            if self.hand in self.hand_range:
                if cbet > 0:
                    raise_chance = 70
                    call_chance = 20
                    bet_chance = 0
                else:
                    bet_chance =90
                    raise_chance=0
                    call_chance = 0
                fold_chance = 10
                check_chance = 0
            else:
                fold_chance = 100
                call_chance = 0
                raise_chance = 0
                bet_chance = 0
                check_chance = 0
        
        
        else:
            #TODO: now want to see if we have made hands
            if cbet > 0:
                raise_chance = 20
                call_chance = 40
                fold_chance = 40
                check_chance = 0
                bet_chance = 0
            else:
                check_chance = 60
                bet_chance = 35
                fold_chance = 5
                call_chance = 0
                raise_chance = 0
        r = uniform(0,1)
        action_types = ['fold'] * fold_chance + ['call'] * call_chance + ['check'] * check_chance + ['bet'] * bet_chance + ['raise'] * raise_chance
        action = choice(action_types)
        return self.action_numbers[action]

    def get_action_amount(self, action, min_bet, current_bet):
        if action == 4:
            #bet must be min bet or higher
            amount = randint(min_bet, min_bet *2)
            if amount > self.stack:
                amount = self.stack
            return amount
        elif action == 5:
            #raise must be current bet*2 or higher
            amount = randint(current_bet*2, current_bet*3)
            if amount > self.stack:
                amount = self.stack
            return amount
        else:
            return 0

# t = Tournament()

# t.begin()

# #print('tournament over after %i rounds. Blinds were %i. Winner stack was %i.' % (t.hand_count, t.bb, t.get_winner()[0].stack))
# w =list(t.win_percents.values())
# wp = [x/t.showdown_count * 100 for x in w]
# #print(wp)