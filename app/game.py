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
game_state = "waiting"

@game_bp.route('/gameboard')
def board():
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
    user_cards = [card for card in all_cards if card['id'] in deck and deck[card['id']] > 0]
    return user_cards

def set_game_state(state):
    global game_state
    game_state = state
    emit('game_state_change', state, broadcast=True)    

# SocketIO event for handling real-time updates
def register_socketio_events(socketio):
    # @socketio.on('card_selected')
    # def handle_card_selected(data):
    #     # Broadcast the card selection to all clients except the sender
    #     emit('update_card_selection', data, broadcast=True)
    
    # @socketio.on('deck_selected')
    # def handle_deck_selected(data):
    #     # Mock card image paths (or use the actual ones you loaded earlier)
    #     card_images = [{'id': card["id"]} for card in data["all_cards"]]

    #     # Send the card images back to the client
    #     emit('display_deck_cards', {'cards': card_images}, broadcast=False)


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
                if game_state == "waiting":
                    set_game_state("ready")
                else:
                    set_game_state(game_state)
            elif game_state == "waiting":
                set_game_state("waiting")

        else:
            emit('error', {'message': 'Seat {} already taken by user {}'.format(seat, players[seat]["username"])})
        emit('player_update', {
            'user1': players[1]['username'],
            'deck1': players[1]['deckname'],
            'user2': players[2]['username'],
            'deck2': players[2]['deckname'],
        }, broadcast=True)

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
                if game_state == "ready":
                    set_game_state("waiting")
                break
    
    @socketio.on('new_game')
    def new_game():
        # Shuffle both decks
        random.shuffle(players[1]['cards'])
        random.shuffle(players[2]['cards'])

        # Deal cards
        emit('add_cards', {'spot': 'seat1-prizes', 'cards': players[1]['cards'][0:6]}, broadcast=True)
        emit('add_cards', {'spot': 'seat1-hand', 'cards': players[1]['cards'][6:13]}, broadcast=True)
        emit('add_cards', {'spot': 'seat1-deck', 'cards': players[1]['cards'][13:]}, broadcast=True)

        emit('add_cards', {'spot': 'seat2-prizes', 'cards': players[2]['cards'][0:6]}, broadcast=True)
        emit('add_cards', {'spot': 'seat2-hand', 'cards': players[2]['cards'][6:13]}, broadcast=True)
        emit('add_cards', {'spot': 'seat2-deck', 'cards': players[2]['cards'][13:]}, broadcast=True)

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
