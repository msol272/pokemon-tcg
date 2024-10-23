from flask import Blueprint, render_template, current_app, request
from flask_socketio import emit

import random
import os
import json
import copy

game_bp = Blueprint('game', __name__)
players = {
    1: {'username': '', 'deckname': '', 'sid': -1, 'ready': False},
    2: {'username': '', 'deckname': '', 'sid': -1, 'ready': False},
}
board = {
    "seat1-deck"    : [],
    "seat1-discard" : [],
    "seat1-prizes"  : [],
    "seat1-hand"    : [],
    "seat1-b1"      : [],
    "seat1-b2"      : [],
    "seat1-b3"      : [],
    "seat1-b4"      : [],
    "seat1-b5"      : [],
    "seat1-active"  : [],
    
    "seat2-deck"    : [],
    "seat2-discard" : [],
    "seat2-prizes"  : [],
    "seat2-hand"    : [],
    "seat2-b1"      : [],
    "seat2-b2"      : [],
    "seat2-b3"      : [],
    "seat2-b4"      : [],
    "seat2-b5"      : [],
    "seat2-active"  : [],
}
labels = {
    "seat1-deck"    : 'Deck',
    "seat1-discard" : 'Discard',
    "seat1-prizes"  : 'Prizes',
    "seat1-hand"    : 'Hand',
    "seat1-b1"      : 'Bench',
    "seat1-b2"      : 'Bench',
    "seat1-b3"      : 'Bench',
    "seat1-b4"      : 'Bench',
    "seat1-b5"      : 'Bench',
    "seat1-active"  : 'Active',
    
    "seat2-deck"    : 'Deck',
    "seat2-discard" : 'Discard',
    "seat2-prizes"  : 'Prizes',
    "seat2-hand"    : 'Hand',
    "seat2-b1"      : 'Bench',
    "seat2-b2"      : 'Bench',
    "seat2-b3"      : 'Bench',
    "seat2-b4"      : 'Bench',
    "seat2-b5"      : 'Bench',
    "seat2-active"  : 'Active',
}

game_state = "ready"
game_round = 1

history_messages = []

# ##############################################################################
# Helper functions
# ##############################################################################
def load_card_list(username, deckname):
    # Load all available Pokémon cards
    file_path = os.path.join(current_app.root_path, "static/pokemon_cards_data.json")
    with open(file_path, 'r') as json_file:
        all_cards = json.load(json_file)["data"]

    # Load user's deck
    users_dir = os.path.join(current_app.root_path, 'users')
    user_dir = os.path.join(users_dir, username)
    deck_dir = os.path.join(user_dir, 'decks', deckname)
    deck_file = os.path.join(deck_dir, 'deck.json')
    with open(deck_file, 'r') as file:
        deck = json.load(file)

    # Filter the cards that are in the deck
    user_cards = []
    for card in all_cards:
        if card['id'] in deck:
            count = deck[card['id']]
            card['damage'] = 0
            card['condition'] = 'NML'
            for i in range(0, count):
                user_cards.append(copy.deepcopy(card))
    return user_cards

def set_game_state(state):
    global game_state
    game_state = state
    emit('game_state_change', state, broadcast=True)    

def set_cell_cards(spot, cards):
    global board
    board[spot] = cards
    emit('set_cell_cards', {'spot': spot, 'cards': cards}, broadcast=True)

def reset_board():
    global board
    for key in board:
        board[key] = []
    emit('sync_board', board, broadcast=True)

def add_history_message(msg):
    history_messages.append(msg)
    emit('add_history_message', msg, broadcast=True)

def clear_history():
    history_messages.clear()
    emit('clear_history', broadcast=True)

# ##############################################################################
# Flask Routes
# ##############################################################################
@game_bp.route('/game')
def game():
    # Retrieve query parameters from the URL
    seat = int(request.args.get('seat'))
    username = request.args.get('username')
    deckname = request.args.get('deck')
    return render_template('game/game.html', seat=seat, username=username, deckname=deckname)

# ##############################################################################
# Socket IO
# ##############################################################################
def register_socketio_events(socketio):
    
    @socketio.on('join_game')
    def handle_player_join(data):
        global game_state

        username = data['username']
        deckname = data['deckname']
        seat = int(data['seat'])

        for msg in history_messages:
            emit('add_history_message', msg)

        if players[seat]["sid"] == -1:
            cards = load_card_list(username, deckname)
            players[seat] = {'username': username, 'deckname': deckname, 'sid': request.sid, 'cards': cards}
            add_history_message('{} joined seat {}'.format(username, seat))
            if players[1]['username'] != '' and players[2]['username'] != '':
                emit('set_new_game_enable', True, broadcast=True)
        else:
            emit('error', {'message': 'Seat {} already taken by user {}'.format(seat, players[seat]["username"])})
        emit('player_update', {
            'user1': players[1]['username'],
            'deck1': players[1]['deckname'],
            'user2': players[2]['username'],
            'deck2': players[2]['deckname'],
        }, broadcast=True)
        emit('game_state_change', game_state, broadcast=True)    
        emit('sync_board', board, broadcast=True)

    @socketio.on('disconnect')
    def handle_disconnect():
        # Find out which seat the player occupied, if any, and handle player leave
        for seat, player in players.items():
            if player and player['sid'] == request.sid:
                add_history_message('{} left seat {}'.format(players[seat]['username'], seat))
                players[seat]['username'] = ''
                players[seat]['deckname'] = ''
                players[seat]['sid'] = -1
                emit('player_update', {
                    'user1': players[1]['username'],
                    'deck1': players[1]['deckname'],
                    'user2': players[2]['username'],
                    'deck2': players[2]['deckname'],
                }, broadcast=True)
                emit('set_new_game_enable', False, broadcast=True)
                break
    
    @socketio.on('new_game')
    def new_game():
        global game_round
        # Shuffle both decks
        random.shuffle(players[1]['cards'])
        random.shuffle(players[2]['cards'])

        reset_board()
        game_round = 1

        # Deal cards
        set_cell_cards('seat1-prizes', players[1]['cards'][0:6])
        set_cell_cards('seat1-hand', players[1]['cards'][6:13])
        set_cell_cards('seat1-deck', players[1]['cards'][13:])

        set_cell_cards('seat2-prizes', players[2]['cards'][0:6])
        set_cell_cards('seat2-hand', players[2]['cards'][6:13])
        set_cell_cards('seat2-deck', players[2]['cards'][13:])

        players[1]['ready'] = False
        players[2]['ready'] = False

        set_game_state('setup')
        clear_history()
        add_history_message('---New Game---')

    @socketio.on('cell_selected')
    def handle_cell_selected(data):
        emit('set_view_panel_cards', {'cards': board[data['spot']], 'spot': data['spot']})
    
    @socketio.on('coin_button')
    def coin_flip(user):
        result = random.choice(['Heads', 'Tails'])
        emit('coin_flip_result', {'user': user, 'result': result}, broadcast=True)
        add_history_message('{} flipped a coin: {}'.format(user, result));

    @socketio.on('action_button')
    def action_button(data):
        global game_round
        seat = int(data['seat'])
        if data['action'] == "Ready":
            players[seat]['ready'] = True
            add_history_message("{} is ready".format(players[seat]['username']))
            if players[1]['ready'] and players[2]['ready']:
                set_game_state('p1-turn')
                add_history_message("Starting game!")
                add_history_message("---{}'s Turn {}---".format(players[1]['username'], game_round))
                emit('sync_board', board, broadcast=True)
        elif data['action'] == "End Turn":
            if game_state == 'p1-turn':
                add_history_message('End of turn')
                add_history_message("---{}'s turn {}---".format(players[2]['username'], game_round))
                set_game_state('p2-turn')
            elif game_state == 'p2-turn':                
                game_round += 1
                add_history_message('End of turn')
                add_history_message("---{}'s turn {}---".format(players[1]['username'], game_round))
                set_game_state('p1-turn')

    @socketio.on('move_card')
    def move_card(data):
        to_stack = data['to_stack']
        from_stack = data['from_stack']
        card_idx = data['card_idx']
        visible = data['visible']
        user = data['username']
        card = board[from_stack][card_idx]
        # Reset condition any time a card is moved
        card['condition'] = 'NML'
        # if this is an energy or trainer being added to a card in play (bench
        # or active), then put it at the bottom. Otherwise, put it on top.
        if ("-b" in to_stack or "-active" in to_stack) and card["supertype"] != "Pok\u00e9mon":
            board[to_stack].append(card)
        else:
            if len(board[to_stack]) > 0:
                card['damage'] = board[to_stack][0]['damage']
            board[to_stack].insert(0, card)
        # remove from the other stack
        board[from_stack].pop(card_idx)
        set_cell_cards(from_stack, board[from_stack])
        set_cell_cards(to_stack, board[to_stack])
        if visible:
            card_name = card['name']
        else:
            card_name = 'a card'
        msg = '{} moved {} from {} to {}'.format(user, card_name, labels[from_stack], labels[to_stack])
        add_history_message(msg)
        emit('set_view_panel_cards', {'cards': board[from_stack], 'spot': from_stack})

    @socketio.on('move_stack')
    def move_stack(data):
        to_stack = data['to_stack']
        from_stack = data['from_stack']
        in_play = data['in_play']
        user = data['username']
        # Reset condition any time a card is moved
        for card in board[from_stack]:
            card['condition'] = 'NML'
        for card in board[to_stack]:
            card['condition'] = 'NML'
        if in_play:
            # Swap the contents of these two stacks
            spare = copy.deepcopy(board[from_stack])
            board[from_stack] = copy.deepcopy(board[to_stack])
            board[to_stack] = copy.deepcopy(spare)
            if len(board[from_stack]) > 0:
                msg = '{} swapped {} and {}'.format(user, labels[from_stack], labels[to_stack])
            else:
                msg = '{} moved all from {} to {}'.format(user, labels[from_stack], labels[to_stack])
        else:
            # Remove any damage
            for card in board[from_stack]:
                card['damage'] = 0
            # Append all to destination
            board[to_stack].extend(board[from_stack])
            board[from_stack] = []
            msg = '{} moved all cards from {} to {}'.format(user, labels[from_stack], labels[to_stack])
        set_cell_cards(from_stack, board[from_stack])
        set_cell_cards(to_stack, board[to_stack])
        add_history_message(msg)
        emit('set_view_panel_cards', {'cards': board[from_stack], 'spot': from_stack})

    @socketio.on('shuffle_stack')
    def shuffle_stack(stack):
        random.shuffle(board[stack])
        set_cell_cards(stack, board[stack])

    @socketio.on('log_event')
    def log_event(msg):
        add_history_message(msg)

    @socketio.on('add_damage')
    def add_damage(data):
        stack = data['stack']
        user = data['username']
        card_name = board[stack][0]['name']
        for card in board[stack]:
            card['damage'] = card['damage'] + 10
        emit('set_damage', {'stack': stack, 'damage': board[stack][0]['damage']}, broadcast=True)
        add_history_message('{} added 10 damage to {}'.format(user, card_name))

    @socketio.on('remove_damage')
    def remove_damage(data):
        stack = data['stack']
        user = data['username']
        card_name = board[stack][0]['name']
        for card in board[stack]:
            card['damage'] = max(0, card['damage'] - 10)
        emit('set_damage', {'stack': stack, 'damage': board[stack][0]['damage']}, broadcast=True)
        add_history_message('{} removed 10 damage from {}'.format(user, card_name))

    @socketio.on('toggle_condition')
    def toggle_condition(data):
        user = data['username']
        spot = data['spot']
        curr_condition = board[spot][0]['condition']
        card_name = board[spot][0]['name']
        if curr_condition == 'NML':
            new_condition = 'PAR'
        elif curr_condition == 'PAR':
            new_condition = 'SLP'
        elif curr_condition == 'SLP':
            new_condition = 'CON'
        elif curr_condition == 'CON':
            new_condition = 'BRN'
        elif curr_condition == 'BRN':
            new_condition = 'POI'
        elif curr_condition == 'POI':
            new_condition = 'GAY'
        elif curr_condition == 'GAY':
            new_condition = 'NML'
        board[spot][0]['condition'] = new_condition
        emit('set_condition', {'spot': spot, 'condition': new_condition}, broadcast=True)
        add_history_message('{} set {} to {}'.format(user, card_name, new_condition))
