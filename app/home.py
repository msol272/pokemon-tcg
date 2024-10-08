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
