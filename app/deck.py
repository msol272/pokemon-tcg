from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
import os
import json

deck_bp = Blueprint('deck', __name__)

@deck_bp.route('/user/<username>/<deckname>', methods=['GET', 'POST'])
def view_edit_deck(username, deckname):
    users_dir = os.path.join(current_app.root_path, 'users')
    user_dir = os.path.join(users_dir, username)

    deck_dir = os.path.join(user_dir, 'decks', deckname)

    if not os.path.exists(user_dir):
        flash(f"User '{username}' does not exist.")
        return redirect(url_for('home.home'))

    # Load user's collection from a file or database (for now, using a mock structure)
    # For example, you can load a JSON file that stores the number of each card for the user.
    collection_file = os.path.join(user_dir, 'collection.json')
    
    # Load user's collection from a file or database (for now, using a mock structure)
    # For example, you can load a JSON file that stores the number of each card for the user.
    deck_file = os.path.join(deck_dir, 'deck.json')
    

    if os.path.exists(collection_file):
        with open(collection_file, 'r') as file:
            collection = json.load(file)
    else:
        collection = {}

    if os.path.exists(deck_file):
        with open(deck_file, 'r') as file:
            deck = json.load(file)
    else:
        deck = {}


    if request.method == 'POST':
        # Handle updating the deck based on form submission
        for card_number, count in request.form.items():
            deck[card_number] = int(count)

        # Save the updated deck
        with open(deck_file, 'w') as file:
            json.dump(deck, file)

        flash('deck updated successfully!')
        return redirect(url_for('users.user_page', username=username))

    # Assume a list of all available Pokémon cards (could load from a global JSON file)
    try:
        file_path = os.path.join(current_app.root_path, "static/pokemon_cards_data.json")
        with open(file_path, 'r') as json_file:
            all_cards = json.load(json_file)["data"]
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
    except json.JSONDecodeError:
        print("Error: The file contains invalid JSON.")

    # Filter out only cards in the collection and add count field
    all_cards = [card for card in all_cards if card['id'] in collection and collection[card['id']] > 0]
    for card in all_cards:
        card['count'] = collection[card['id']]

    # Sort the cards by ID before rendering
    all_cards = sorted(all_cards, key=lambda x: int(x['number']) + (1000 if x['supertype'] == "Energy" else 0))

    for card in all_cards:
        superType = card["supertype"]
        if superType == "Trainer":
            cardType = "Trainer"
        elif superType == "Energy":
            cardType = "Energy"
        elif superType == "Pok\u00e9mon":
            cardType = card["types"][0]
        card["cardtype"] = cardType

    # Calculate summary statistics
    unique_pokemon_count = 0
    total_pokemon_count = 0
    unique_trainer_count = 0
    total_trainer_count = 0
    unique_energy_count = 0
    total_energy_count = 0

    for card in all_cards:
        card_id = card["id"]
        count = deck.get(card_id, 0)
        card_type = card["cardtype"]

        if count > 0:
            if card_type == "Energy":
                unique_energy_count += 1
                total_energy_count += count
            elif card_type == "Trainer":
                unique_trainer_count += 1
                total_trainer_count += count
            else:  # It's a Pokémon card
                unique_pokemon_count += 1
                total_pokemon_count += count

    # Pass summary statistics to the template
    return render_template('deck.html', username=username, deckname=deckname, deck=deck, all_cards=all_cards,
                           unique_pokemon_count=unique_pokemon_count, total_pokemon_count=total_pokemon_count,
                           unique_trainer_count=unique_trainer_count, total_trainer_count=total_trainer_count,
                           unique_energy_count=unique_energy_count, total_energy_count=total_energy_count)

