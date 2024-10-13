from flask import Blueprint, render_template, current_app, request
from flask_socketio import emit

import os
import json

game_bp = Blueprint('game', __name__)

@game_bp.route('/gameboard')
def board():
    # Retrieve query parameters from the URL
    seat = request.args.get('seat')
    username = request.args.get('username')
    deckname = request.args.get('deck')

    # Assume a list of all available Pokémon cards (could load from a global JSON file)
    file_path = os.path.join(current_app.root_path, "static/pokemon_cards_data.json")
    with open(file_path, 'r') as json_file:
        all_cards = json.load(json_file)["data"]

    # Load user's collection from a file or database (for now, using a mock structure)
    # For example, you can load a JSON file that stores the number of each card for the user.
    users_dir = os.path.join(current_app.root_path, 'users')
    user_dir = os.path.join(users_dir, username)
    deck_dir = os.path.join(user_dir, 'decks', deckname)
    deck_file = os.path.join(deck_dir, 'deck.json')
    with open(deck_file, 'r') as file:
        deck = json.load(file)

    all_cards = [card for card in all_cards if card['id'] in deck and deck[card['id']] > 0]

    return render_template('gameboard.html', seat=seat, all_cards=all_cards)

# SocketIO event for handling real-time updates
def register_socketio_events(socketio):
    @socketio.on('card_selected')
    def handle_card_selected(data):
        # Broadcast the card selection to all clients except the sender
        emit('update_card_selection', data, broadcast=True)
