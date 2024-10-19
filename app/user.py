from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
import os
import json

user_bp = Blueprint('user', __name__)

@user_bp.route('/user/<username>')
def user_page(username):
    users_dir = os.path.join(current_app.root_path, 'users')
    user_dir = os.path.join(users_dir, username)

    # List decks for the user (assuming decks are directories or files in a 'decks' folder under each user)
    decks_dir = os.path.join(user_dir, 'decks')
    if not os.path.exists(decks_dir):
        os.makedirs(decks_dir)

    decks = [d for d in os.listdir(decks_dir) if os.path.isdir(os.path.join(decks_dir, d))]

    return render_template('user/user.html', username=username, decks=decks)

@user_bp.route('/user/<username>/create_deck', methods=['GET', 'POST'])
def create_deck(username):
    users_dir = os.path.join(current_app.root_path, 'users')
    user_dir = os.path.join(users_dir, username)
    decks_dir = os.path.join(user_dir, 'decks')

    if request.method == 'POST':
        new_deck_name = request.form['deck_name'].strip()

        # Check if the deck already exists
        new_deck_path = os.path.join(decks_dir, new_deck_name)
        if os.path.exists(new_deck_path):
            flash(f'Deck "{new_deck_name}" already exists. Please choose another name.', 'error')
            return redirect(url_for('user.create_deck', username=username))

        # Create the new deck directory
        os.makedirs(new_deck_path)

        # Capture checkbox states
        settings = {
            'unlimited_energy': 'unlimited_energy' in request.form,
            'unlimited_dupes': 'unlimited_dupes' in request.form,
            'unlimited_evolvers': 'unlimited_evolvers' in request.form,
            'unlimited_cards': 'unlimited_cards' in request.form
        }

        # Write settings to a JSON file in the deck directory
        settings_file = os.path.join(new_deck_path, 'settings.json')
        with open(settings_file, 'w') as f:
            json.dump(settings, f, indent=4)

        return redirect(url_for('deck.view_edit_deck', username=username, deckname=new_deck_name))

    return render_template('user/create_deck.html', username=username)


@user_bp.route('/user/<username>/rename_deck', methods=['POST'])
def rename_deck(username):
    users_dir = os.path.join(current_app.root_path, 'users')
    user_dir = os.path.join(users_dir, username)
    decks_dir = os.path.join(user_dir, 'decks')

    current_name = request.form['current_name'].strip()
    new_name = request.form['new_name'].strip()

    current_deck_path = os.path.join(decks_dir, current_name)
    new_deck_path = os.path.join(decks_dir, new_name)

    # Check if the new deck name already exists
    if os.path.exists(new_deck_path):
        flash(f'A deck with the name "{new_name}" already exists. Please choose another name.', 'error')
        return redirect(url_for('user.user_page', username=username))

    # Rename the directory
    os.rename(current_deck_path, new_deck_path)
    flash(f'Deck "{current_name}" renamed to "{new_name}" successfully.')
    
    return redirect(url_for('user.user_page', username=username))

@user_bp.route('/user/<username>/delete_deck', methods=['POST'])
def delete_deck(username):
    users_dir = os.path.join(current_app.root_path, 'users')
    user_dir = os.path.join(users_dir, username)
    decks_dir = os.path.join(user_dir, 'decks')

    deck_name = request.form['deck_name'].strip()
    deck_path = os.path.join(decks_dir, deck_name)

    if os.path.exists(deck_path):
        # Delete the directory and its contents
        deck_file = os.path.join(deck_path, "deck.json")
        settings_file = os.path.join(deck_path, "settings.json")
        if os.path.exists(deck_file):
            os.remove(deck_file)
        if os.path.exists(settings_file):
            os.remove(settings_file)
        os.rmdir(deck_path)  # If the directory is empty
    else:
        flash(f'Deck "{deck_name}" not found.', 'error')

    return redirect(url_for('user.user_page', username=username))
