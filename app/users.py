from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
import os

users_bp = Blueprint('users', __name__)

@users_bp.route('/new_user', methods=['GET', 'POST'])
def new_user():
    users_dir = os.path.join(current_app.root_path, 'users')
    
    if request.method == 'POST':
        new_username = request.form['username'].strip()

        # Check if the directory already exists
        if os.path.exists(os.path.join(users_dir, new_username)):
            flash('User already exists. Please choose another name.')
            return redirect(url_for('users.new_user'))
        else:
            # Create a new directory for the user
            os.makedirs(os.path.join(users_dir, new_username))
            flash(f'User "{new_username}" created successfully.')
            return redirect(url_for('home.home'))

    return render_template('new_user.html')

@users_bp.route('/user/<username>')
def user_page(username):
    users_dir = os.path.join(current_app.root_path, 'users')
    user_dir = os.path.join(users_dir, username)

    if not os.path.exists(user_dir):
        flash(f"User '{username}' does not exist.")
        return redirect(url_for('home.home'))

    # List decks for the user (assuming decks are directories or files in a 'decks' folder under each user)
    decks_dir = os.path.join(user_dir, 'decks')
    if not os.path.exists(decks_dir):
        os.makedirs(decks_dir)

    decks = [d for d in os.listdir(decks_dir) if os.path.isdir(os.path.join(decks_dir, d))]

    return render_template('user.html', username=username, decks=decks)

@users_bp.route('/user/<username>/create_deck', methods=['GET', 'POST'])
def create_deck(username):
    users_dir = os.path.join(current_app.root_path, 'users')
    user_dir = os.path.join(users_dir, username)
    decks_dir = os.path.join(user_dir, 'decks')

    if not os.path.exists(user_dir):
        flash(f"User '{username}' does not exist.")
        return redirect(url_for('home.home'))

    if request.method == 'POST':
        new_deck_name = request.form['deck_name'].strip()

        # Check if the deck already exists
        new_deck_path = os.path.join(decks_dir, new_deck_name)
        if os.path.exists(new_deck_path):
            flash(f'Deck "{new_deck_name}" already exists. Please choose another name.', 'error')
            return redirect(url_for('users.create_deck', username=username))

        # Create the new deck
        os.makedirs(new_deck_path)
        flash(f'Deck "{new_deck_name}" created successfully.')
        return redirect(url_for('deck.view_edit_deck', username=username, deckname=new_deck_name))

    return render_template('create_deck.html', username=username)

@users_bp.route('/user/<username>/rename_deck', methods=['POST'])
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
        return redirect(url_for('users.user_page', username=username))

    # Rename the directory
    os.rename(current_deck_path, new_deck_path)
    flash(f'Deck "{current_name}" renamed to "{new_name}" successfully.')
    
    return redirect(url_for('users.user_page', username=username))

@users_bp.route('/user/<username>/delete_deck', methods=['POST'])
def delete_deck(username):
    users_dir = os.path.join(current_app.root_path, 'users')
    user_dir = os.path.join(users_dir, username)
    decks_dir = os.path.join(user_dir, 'decks')

    deck_name = request.form['deck_name'].strip()
    deck_path = os.path.join(decks_dir, deck_name)

    if os.path.exists(deck_path):
        # Delete the directory and its contents
        json_file = os.path.join(deck_path, "deck.json")
        if os.path.exists(json_file):
            os.remove(os.path.join(deck_path, "deck.json"))  # If the directory is empty
        os.rmdir(deck_path)  # If the directory is empty
        flash(f'Deck "{deck_name}" deleted successfully.')
    else:
        flash(f'Deck "{deck_name}" not found.', 'error')

    return redirect(url_for('users.user_page', username=username))
