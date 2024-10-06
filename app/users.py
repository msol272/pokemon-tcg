from flask import Blueprint, render_template, request, redirect, url_for, flash
import os

users_bp = Blueprint('users', __name__)

@users_bp.route('/new_user', methods=['GET', 'POST'])
def new_user():
    users_dir = os.path.join(os.getcwd(), 'users')
    
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
    users_dir = os.path.join(os.getcwd(), 'users')
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
