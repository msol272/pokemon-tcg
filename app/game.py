from flask import Blueprint, render_template, current_app, request
from flask_socketio import emit

import random
import os
import json

game_bp = Blueprint('game', __name__)
players = {
    1: {'username': '', 'deckname': '', 'sid': -1},
    2: {'username': '', 'deckname': '', 'sid': -1},
}
board = {
    "seat1-deck"    : [],
    "seat1-discard" : [],
    "seat1-prizes"  : [],
    "seat1-hand"    : [],
    "seat1-spare1"  : [],
    "seat1-spare2"  : [],
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
    "seat2-spare1"  : [],
    "seat2-spare2"  : [],
    "seat2-b1"      : [],
    "seat2-b2"      : [],
    "seat2-b3"      : [],
    "seat2-b4"      : [],
    "seat2-b5"      : [],
    "seat2-active"  : [],
}
game_state = "ready"

@game_bp.route('/gameboard')
def gameboard():
    # Retrieve query parameters from the URL
    seat = int(request.args.get('seat'))
    return render_template('gameboard.html', seat=seat)

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
            for i in range(0, count):
                user_cards.append(card)
    return user_cards

def set_game_state(state):
    global game_state
    game_state = state
    emit('game_state_change', state, broadcast=True)    

def set_card_stack(spot, cards):
    global board
    board[spot] = cards
    emit('set_card_stack', {'spot': spot, 'cards': cards}, broadcast=True)

def reset_board():
    global board
    for key in board:
        board[key] = []
    emit('sync_board', board, broadcast=True)

# SocketIO event for handling real-time updates
def register_socketio_events(socketio):
    @socketio.on('cell_selected')
    def handle_cell_selected(data):
        emit('set_right_panel', board[data['spot']])
    
    @socketio.on('join_game')
    def handle_player_join(data):
        username = data['username']
        deckname = data['deckname']
        seat = int(data['seat'])
        if players[seat]["sid"] == -1:
            cards = load_card_list(username, deckname)
            players[seat] = {'username': username, 'deckname': deckname, 'sid': request.sid, 'cards': cards}
            emit('action_log', '{} joined in seat {}'.format(username, seat), broadcast=True)
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
        emit('sync_board', board, broadcast=True)
        emit('game_state_change', game_state, broadcast=True)    

    @socketio.on('disconnect')
    def handle_disconnect():
        # Find out which seat the player occupied, if any, and handle player leave
        for seat, player in players.items():
            if player and player['sid'] == request.sid:
                emit('action_log', '{} left seat {}'.format(players[seat]['username'], seat), broadcast=True)
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
        # Shuffle both decks
        random.shuffle(players[1]['cards'])
        random.shuffle(players[2]['cards'])

        reset_board()

        # Deal cards
        set_card_stack('seat1-prizes', players[1]['cards'][0:6])
        set_card_stack('seat1-hand', players[1]['cards'][6:13])
        set_card_stack('seat1-deck', players[1]['cards'][13:])

        set_card_stack('seat2-prizes', players[2]['cards'][0:6])
        set_card_stack('seat2-hand', players[2]['cards'][6:13])
        set_card_stack('seat2-deck', players[2]['cards'][13:])

        players[1]['ready'] = False
        players[2]['ready'] = False

        set_game_state('setup')

    @socketio.on('coin_button')
    def coin_flip(user):
        result = random.choice(['Heads', 'Tails'])
        emit('coin_flip_result', {'user': user, 'result': result}, broadcast=True)

    @socketio.on('action_button')
    def action_button(data):
        seat = int(data['seat'])
        if data['action'] == "Ready":
            players[seat]['ready'] = True
            if players[1]['ready'] and players[2]['ready']:
                set_game_state('p1-turn')
        elif data['action'] == "End Turn":
            if game_state == 'p1-turn':                
                set_game_state('p2-turn')
            elif game_state == 'p2-turn':                
                set_game_state('p1-turn')   
