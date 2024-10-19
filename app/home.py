from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
import os

home_bp = Blueprint('home', __name__)

# ------------------------------------------------------------------------------
# Helper Functions
# ------------------------------------------------------------------------------
def load_users():
    # Load a list of all users that exist to pass to client
    users_dir = os.path.join(current_app.root_path, 'users')
    if not os.path.exists(users_dir):
        os.makedirs(users_dir)
    users = [d for d in os.listdir(users_dir) if os.path.isdir(os.path.join(users_dir, d))]
    return users

# ------------------------------------------------------------------------------
# Flask Routes
# ------------------------------------------------------------------------------
@home_bp.route('/')
def home():
    return render_template('home/home.html', users=load_users())

@home_bp.route('/new_user', methods=['GET', 'POST'])
def new_user():
    users_dir = os.path.join(current_app.root_path, 'users')
    
    if request.method == 'POST':
        new_username = request.form['username'].strip()

        # Check if the directory already exists
        if os.path.exists(os.path.join(users_dir, new_username)):
            flash('User already exists. Please choose another name.')
            return redirect(url_for('home.new_user'))
        else:
            # Create a new directory for the user
            os.makedirs(os.path.join(users_dir, new_username))
            flash(f'User "{new_username}" created successfully.')
            return redirect(url_for('home.home'))

    return render_template('home/new_user.html')

@home_bp.route('/join_seat<seat>/select_user')
def join_seat_select_user(seat):
    return render_template('home/join_select_user.html', users=load_users(), seat=seat)

@home_bp.route('/join_seat<seat>/select_deck/<username>')
def join_seat_select_deck(username, seat):
    users_dir = os.path.join(current_app.root_path, 'users')
    user_dir = os.path.join(users_dir, username)

    if not os.path.exists(user_dir):
        flash(f"User '{username}' does not exist.")
        return redirect(url_for('home.join_seat_select_user', seat=seat))

    # List decks for the user (assuming decks are directories in a 'decks' folder under each user)
    decks_dir = os.path.join(user_dir, 'decks')
    if not os.path.exists(decks_dir):
        os.makedirs(decks_dir)
    decks = [d for d in os.listdir(decks_dir) if os.path.isdir(os.path.join(decks_dir, d))]
    return render_template('home/join_select_deck.html', username=username, decks=decks, seat=seat)
