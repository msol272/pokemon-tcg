from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
import os
import json

deck_bp = Blueprint('deck', __name__)

@deck_bp.route('/user/<username>/<deckname>', methods=['GET', 'POST'])
def view_edit_deck(username, deckname):
    users_dir = os.path.join(current_app.root_path, 'users')
    user_dir = os.path.join(users_dir, username)
    deck_dir = os.path.join(user_dir, 'decks', deckname)

    collection_file = os.path.join(user_dir, 'collection.json')
    deck_file = os.path.join(deck_dir, 'deck.json')
    settings_file =  os.path.join(deck_dir, 'settings.json')

    if request.method == 'POST':
        # Save the deck
        deck = {}
        for card_number, count in request.form.items():
            deck[card_number] = int(count)

        with open(deck_file, 'w') as file:
            json.dump(deck, file)

        return redirect(url_for('user.user_page', username=username))

    # Load user's card colletion
    if os.path.exists(collection_file):
        with open(collection_file, 'r') as file:
            collection = json.load(file)
    else:
        collection = {}

    # Load this deck
    if os.path.exists(deck_file):
        with open(deck_file, 'r') as file:
            deck = json.load(file)
    else:
        deck = {}

    # Load this deck's settings
    if os.path.exists(settings_file):
        with open(settings_file, 'r') as file:
            settings = json.load(file)
    else:
        settings = {
            "unlimited_energy": False, 
            "unlimited_dupes": False, 
            "unlimited_evolvers": False, 
            "unlimited_cards": False, 
        }

    # Load a list of all available pokemon
    file_path = os.path.join(current_app.root_path, "static/pokemon_cards_data.json")
    with open(file_path, 'r') as json_file:
        all_cards = json.load(json_file)["data"]

    # Create a list of pokemon that evolve into cards you own
    evolver_names = []
    if settings["unlimited_evolvers"]:
        # First pass - direct evolvers
        for card in all_cards:
            if card['id'] in collection and collection[card["id"]] > 0:
                if "evolvesFrom" in card:
                    evolver_names.append(card["evolvesFrom"])
        # Second pass - evolvers of evolvers
        for card in all_cards:
            if card["name"] in evolver_names:
                if "evolvesFrom" in card:
                    evolver_names.append(card["evolvesFrom"])   

    # Created filtered list of cards to display based on settings
    filtered_cards = []

    for card in all_cards:
        # Set card type
        superType = card["supertype"]
        if superType == "Trainer":
            cardType = "Trainer"
        elif superType == "Energy":
            cardType = "Energy"
        elif superType == "Pok\u00e9mon":
            cardType = card["types"][0]
        card["cardtype"] = cardType

        if settings["unlimited_cards"]:
            if cardType == "Energy":
                card["count"] = 60
            else:
                card["count"] = 4
            filtered_cards.append(card)
        elif settings["unlimited_energy"] and cardType == "Energy":
            card["count"] = 60
            filtered_cards.append(card)
        else:
            if card["name"] in evolver_names:
                if cardType == "Energy":
                    card["count"] = 60
                else:
                    card["count"] = 4   
                filtered_cards.append(card)
            elif card['id'] in collection and collection[card["id"]] > 0:
                if settings["unlimited_dupes"]:
                    if cardType == "Energy":
                        card["count"] = 60
                    else:
                        card["count"] = 4   
                else:
                    if cardType == "Energy":
                        card["count"] = collection[card["id"]]
                    else:
                        card["count"] = min(4, collection[card["id"]])
                filtered_cards.append(card)
            
    # Sort the cards by ID before rendering
    filtered_cards = sorted(filtered_cards, key=lambda x: int(x['number']) + (1000 if x['supertype'] == "Energy" else 0))

    # Calculate summary statistics
    unique_pokemon_count = 0
    total_pokemon_count = 0
    unique_trainer_count = 0
    total_trainer_count = 0
    unique_energy_count = 0
    total_energy_count = 0

    for card in filtered_cards:
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
    return render_template('deck/deck.html', username=username, deckname=deckname, deck=deck, all_cards=filtered_cards,
                           unique_pokemon_count=unique_pokemon_count, total_pokemon_count=total_pokemon_count,
                           unique_trainer_count=unique_trainer_count, total_trainer_count=total_trainer_count,
                           unique_energy_count=unique_energy_count, total_energy_count=total_energy_count)

