from flask import Blueprint, render_template, request, redirect, url_for, flash
import os
import json

collection_bp = Blueprint('collection', __name__)

@collection_bp.route('/user/<username>/collection', methods=['GET', 'POST'])
def view_edit_collection(username):
    users_dir = os.path.join(os.getcwd(), 'users')
    user_dir = os.path.join(users_dir, username)

    if not os.path.exists(user_dir):
        flash(f"User '{username}' does not exist.")
        return redirect(url_for('home'))

    # Load user's collection from a file or database (for now, using a mock structure)
    # For example, you can load a JSON file that stores the number of each card for the user.
    collection_file = os.path.join(user_dir, 'collection.json')
    
    if os.path.exists(collection_file):
        with open(collection_file, 'r') as file:
            collection = json.load(file)
    else:
        collection = {}

    if request.method == 'POST':
        # Handle updating the collection based on form submission
        for card_number, count in request.form.items():
            collection[card_number] = int(count)

        # Save the updated collection
        with open(collection_file, 'w') as file:
            json.dump(collection, file)

        flash('Collection updated successfully!')
        return redirect(url_for('users.user_page', username=username))

    # Assume a list of all available Pokémon cards (could load from a global JSON file)
    try:
        file_path = "app/static/pokemon_cards_data.json"
        with open(file_path, 'r') as json_file:
            all_cards = json.load(json_file)["data"]
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
    except json.JSONDecodeError:
        print("Error: The file contains invalid JSON.")

    for card in all_cards:
        superType = card["supertype"]
        if superType == "Trainer":
            cardType = "Trainer"
        elif superType == "Energy":
            cardType = "Energy"
        elif superType == "Pok\u00e9mon":
            cardType = card["types"][0]
        card["cardtype"] = cardType

    return render_template('collection.html', username=username, collection=collection, all_cards=all_cards)
