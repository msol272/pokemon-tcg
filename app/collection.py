from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
import os
import json

collection_bp = Blueprint('collection', __name__)

@collection_bp.route('/user/<username>/collection', methods=['GET', 'POST'])
def view_edit_collection(username):
    users_dir = os.path.join(current_app.root_path, 'users')
    user_dir = os.path.join(users_dir, username)
    collection_file = os.path.join(user_dir, 'collection.json')

    if request.method == 'POST':
        # Save the collection to json file
        collection = {}
        for card_number, count in request.form.items():
            collection[card_number] = int(count)

        with open(collection_file, 'w') as file:
            json.dump(collection, file)

        return redirect(url_for('user.user_page', username=username))
    else:
        # Load colletion from json file
        if os.path.exists(collection_file):
            with open(collection_file, 'r') as file:
                collection = json.load(file)
        else:
            collection = {}

    # Assume a list of all available Pokémon cards (could load from a global JSON file)
    file_path = os.path.join(current_app.root_path, "static/pokemon_cards_data.json")
    with open(file_path, 'r') as json_file:
        all_cards = json.load(json_file)["data"]

    # Sort the cards by ID before rendering
    all_cards = sorted(all_cards, key=lambda x: int(x['number']) + (1000 if x['supertype'] == "Energy" else 0))

    # Set card type
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
        count = collection.get(card_id, 0)
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
    return render_template('collection/collection.html', username=username, collection=collection, all_cards=all_cards,
                           unique_pokemon_count=unique_pokemon_count, total_pokemon_count=total_pokemon_count,
                           unique_trainer_count=unique_trainer_count, total_trainer_count=total_trainer_count,
                           unique_energy_count=unique_energy_count, total_energy_count=total_energy_count)

