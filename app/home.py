from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
import os

home_bp = Blueprint('home', __name__)

@home_bp.route('/')
def home():
    # Path to the 'users' folder
    users_dir = os.path.join(current_app.root_path, 'users')
    if not os.path.exists(users_dir):
        os.makedirs(users_dir)

    # List all subdirectories (i.e., user names)
    users = [d for d in os.listdir(users_dir) if os.path.isdir(os.path.join(users_dir, d))]

    return render_template('home.html', users=users)

@home_bp.route('/join_seat<seat>/select_user')
def select_user(seat):
    # Path to the 'users' folder
    users_dir = os.path.join(current_app.root_path, 'users')
    if not os.path.exists(users_dir):
        os.makedirs(users_dir)

    # List all subdirectories (i.e., user names)
    users = [d for d in os.listdir(users_dir) if os.path.isdir(os.path.join(users_dir, d))]

    return render_template('select_user.html', users=users, seat=seat)

@home_bp.route('/join_seat<seat>/select_deck/<username>')
def select_deck(username, seat):
    users_dir = os.path.join(current_app.root_path, 'users')
    user_dir = os.path.join(users_dir, username)

    if not os.path.exists(user_dir):
        flash(f"User '{username}' does not exist.")
        return redirect(url_for('home.select_user', seat=seat))

    # List decks for the user (assuming decks are directories in a 'decks' folder under each user)
    decks_dir = os.path.join(user_dir, 'decks')
    if not os.path.exists(decks_dir):
        os.makedirs(decks_dir)

    decks = [d for d in os.listdir(decks_dir) if os.path.isdir(os.path.join(decks_dir, d))]

    return render_template('select_deck.html', username=username, decks=decks, seat=seat)

@home_bp.route('/join_seat<seat>/<username>/<deck>', methods=['POST'])
def join_seat(username, deck, seat):
    # Logic to join the game with the selected user and deck
    flash(f"{username} has joined Seat {seat} with the deck '{deck}'.")
    return redirect(url_for('home.home'))
