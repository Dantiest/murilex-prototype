import sqlite3
from flask import Blueprint, request, jsonify, session


watchman_bp = Blueprint("watchman", __name__)

@watchman_bp.route('/manage_assets', methods=['POST'])
def manage_assets():
    user_id = session.get('user_id')

    # Get JSON data from the request
    data = request.get_json()
    item_id = data['item_id']
    item_type = data['item_type']
    action = data['action']  # 'add' or 'remove'

    connection = sqlite3.connect("murilex.db") 
    cursor = connection.cursor()

    if action == 'add':
        cursor.execute('INSERT INTO watchlist (user_id, item_id, item_type) VALUES (?, ?, ?)',
                       (user_id, item_id, item_type))
        connection.commit()
        message = "Item added to watchlist"
    elif action == 'remove':
        cursor.execute('DELETE FROM watchlist WHERE user_id = ? AND item_id = ? AND item_type = ?',
                       (user_id, item_id, item_type))
        connection.commit()
        message = "Item removed from watchlist"
    else:
        message = "Invalid action"

    connection.close()

    return jsonify({"message": message})

@watchman_bp.route('/manage_categories', methods=['POST'])
def manage_categories():
    user_id = session.get('user_id')

    # Get JSON data from the request
    data = request.get_json()
    category_id = data['category_id']
    item_type = 'categories'
    action = data['action']  # 'add' or 'remove'

    connection = sqlite3.connect("murilex.db") 
    cursor = connection.cursor()

    if action == 'add':
        cursor.execute('INSERT INTO watchlist (user_id, item_id, item_type) VALUES (?, ?, ?)',
                       (user_id, category_id, item_type))
        connection.commit()
        message = "Item added to watchlist"
    elif action == 'remove':
        cursor.execute('DELETE FROM watchlist WHERE user_id = ? AND item_id = ? AND item_type = ?',
                       (user_id, category_id, item_type))
        connection.commit()
        message = "Item removed from watchlist"
    else:
        message = "Invalid action"

    connection.close()

    return jsonify({"message": message})