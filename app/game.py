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

    return render_template('gameboard.html', seat=seat, all_cards=user_cards)

# SocketIO event for handling real-time updates
def register_socketio_events(socketio):
    @socketio.on('card_selected')
    def handle_card_selected(data):
        # Broadcast the card selection to all clients except the sender
        emit('update_card_selection', data, broadcast=True)
    
    @socketio.on('deck_selected')
    def handle_deck_selected(data):
        # Mock card image paths (or use the actual ones you loaded earlier)
        card_images = [{'id': card["id"]} for card in data["all_cards"]]

        # Send the card images back to the client
        emit('display_deck_cards', {'cards': card_images}, broadcast=False)
