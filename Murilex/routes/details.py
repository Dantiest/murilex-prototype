import sqlite3, json
from collections import namedtuple
from flask import Blueprint, request, render_template, session, jsonify
from routes.auth import login_required
from routes.database import get_number_of_bids_or_asks, get_user_shares, get_user_available_balance
from routes.detailsdb import get_artist_data_by_id

details_bp = Blueprint("details", __name__)

# Define a connection to the database
def connect_db():
    return sqlite3.connect('murilex.db')

@details_bp.route('/artists/<int:artist_id>')
def artists(artist_id):
    connection = sqlite3.connect("murilex.db")
    cursor = connection.cursor()

    artist_data = {}
    song_data = []
    album_data = []
    catalogue_data = {}
    song_watchlist_count = {}
    album_watchlist_count = {}
    catalogue_watchlist_count = {}

    if artist_id is not None:
        cursor.execute("""SELECT
                        name,
                        image,
                        category_id,
                        description
                    FROM artist
                    WHERE id = ?""", (artist_id,))
        artist_raw = cursor.fetchone()
        if artist_raw:
            artist_data = {
                'name': artist_raw[0],
                'image': artist_raw[1],
                'category': artist_raw[2],
                'description': artist_raw[3]
            }

        cursor.execute("""SELECT
                        id AS song_id,
                        name AS song_name,
                        image AS song_image,
                        albumname AS song_albumname,
                        price AS song_price,
                        availability AS song_availability
                    FROM song
                    WHERE artist_id = ?""", (artist_id,))
        songs_raw = cursor.fetchall()
        song_data = [
            {
                'id': song_raw[0],
                'name': song_raw[1],
                'image': song_raw[2],
                'albumname': song_raw[3],
                'price': song_raw[4],
                'availability': song_raw[5]
            }
            for song_raw in songs_raw
        ]

        cursor.execute("""SELECT
                        id AS album_id,
                        name AS album_name,
                        image AS album_image,
                        price AS album_price,
                        availability AS album_availability
                    FROM album
                    WHERE artist_id = ?""", (artist_id,))
        albums_raw = cursor.fetchall()
        album_data = [
            {
                'id': album_raw[0],
                'name': album_raw[1],
                'image': album_raw[2],
                'price': album_raw[3],
                'availability': album_raw[4]
            }
            for album_raw in albums_raw
        ]

        cursor.execute("""SELECT
                        id AS catalogue_id,
                        price AS catalogue_price,
                        shares AS catalogue_shares
                    FROM catalogue
                    WHERE artist_id = ?""", (artist_id,))
        catalogue_raw = cursor.fetchone()

        if catalogue_raw:
            catalogue_data = {
                'id': catalogue_raw[0],
                'price': catalogue_raw[1],
                'shares': catalogue_raw[2]
            }

        user_id = session.get('user_id')

        for item in song_data:
            cursor.execute('SELECT COUNT(*) FROM watchlist WHERE user_id = ? AND item_id = ? AND item_type = ?',
                        (user_id, item['id'], "song"))
            count = cursor.fetchone()[0]
            song_watchlist_count[item['id']] = count

        for item in album_data:
            cursor.execute('SELECT COUNT(*) FROM watchlist WHERE user_id = ? AND item_id = ? AND item_type = ?',
                        (user_id, item['id'], "album"))
            count = cursor.fetchone()[0]
            album_watchlist_count[item['id']] = count

        if catalogue_data:
            cursor.execute('SELECT COUNT(*) FROM watchlist WHERE user_id = ? AND item_id = ? AND item_type = ?',
                        (user_id, catalogue_data['id'], "catalogue"))
            count = cursor.fetchone()[0]
            catalogue_watchlist_count[catalogue_data['id']] = count

    return render_template('artists.html', catalogue=catalogue_data, song_data=song_data, album_data=album_data, artist=artist_data, song_watchlist_count=song_watchlist_count, album_watchlist_count=album_watchlist_count, catalogue_watchlist_count=catalogue_watchlist_count)

@details_bp.route('/asset/<asset_name>')
def asset(asset_name):
    user_id = session.get('user_id')

    type = request.args.get('type')
    connection = sqlite3.connect("murilex.db")
    cursor = connection.cursor()

    # Named tuple structure for Album
    Asset = namedtuple(
        'Asset',
        ['id', 'name', 'image', 'price', 'availability', 'author_name', 'author_image', "artist_id", 'category_name']
    )

    # Default empty dictionary
    asset_data = {}

    asset_id = None

    # Fetch data from both tables and filter by the asset name
    if type == 'song':
        cursor.execute("""
            SELECT song.id, song.name, song.image, song.price, song.availability, artist.name AS author_name, artist.image AS author_image, artist_id, categories.name AS category_name
            FROM song
            INNER JOIN artist ON song.artist_id = artist.id
            INNER JOIN categories ON song.category_id = categories.id
            WHERE song.name = ?""", (asset_name,))
    
        assetRaw = cursor.fetchone()
        asset_id = assetRaw[0]
        asset_tuple = Asset(*assetRaw)
        asset_data = asset_tuple._asdict()

    elif type == 'album':

        cursor.execute("""           
            SELECT album.id, album.name, album.image, album.price, album.availability, artist.name AS author_name, artist.image AS author_image, artist_id, categories.name AS category_name
            FROM album
            INNER JOIN artist ON album.artist_id = artist.id
            INNER JOIN categories ON album.category_id = categories.id
            WHERE album.name = ? """, (asset_name,))
        
        assetRaw = cursor.fetchone()
        asset_id = assetRaw[0]
        asset_tuple = Asset(*assetRaw)
        asset_data = asset_tuple._asdict()

    elif type == 'catalogue':

        Catalogue = namedtuple(
        'Catalogue',
        ['id', 'name', 'image', 'price', 'shares', 'category_name', 'artist_id']
        )

        cursor.execute("""
            SELECT catalogue.id, artist.name AS name, artist.image AS image, catalogue.price, catalogue.shares, artist.category_id AS category_name , artist_id
            FROM catalogue
            INNER JOIN artist ON catalogue.artist_id = artist.id
            WHERE artist.name = ?""", (asset_name,))

        assetRaw = cursor.fetchone()
        asset_id = assetRaw[0]
        if assetRaw is not None:
            asset_tuple = Catalogue(*assetRaw)
            asset_data = asset_tuple._asdict()
            # Process asset_data here
        else:
            print("No data found for the given asset_name.")

    else:
        print("HTML error.")

    if user_id:
        cursor.execute('SELECT COUNT(*) FROM watchlist WHERE user_id = ? AND item_id = ? AND item_type = ?',
                        (user_id, asset_id, type))
        count = cursor.fetchone()[0]
    else:
        count = 0


    Bid = namedtuple('Bid', ['price', 'quantity'])
    Ask = namedtuple('Ask', ['price', 'quantity'])
    History = namedtuple('History', ['timestamp', 'price', 'quantity'])

    bid_data = []
    ask_data = []
    transaction_history_data = []

    cursor.execute("""
        SELECT price, quantity
        FROM bids
        WHERE asset_id = ? AND asset_type = ?
        ORDER BY price DESC, created_at ASC""", (asset_id, type))
    bidRaw = cursor.fetchall()
    if bidRaw:
        bid_data.extend([Bid(*bid) for bid in bidRaw])
    else:
        bid_data = None

    cursor.execute("""
        SELECT price, quantity
        FROM asks
        WHERE asset_id = ? AND asset_type = ?
        ORDER BY price ASC, created_at ASC""", (asset_id, type))
    askRaw = cursor.fetchall()
    if askRaw:
        ask_data.extend([Ask(*ask) for ask in askRaw])
    else:
        ask_data = None

    cursor.execute("""
        SELECT timestamp, price, quantity
        FROM transaction_history
        WHERE asset_id = ? AND asset_type = ? AND transaction_type = ?
        ORDER BY timestamp DESC
        LIMIT 10""", (asset_id, type, 'purchase'))
    tranRaw = cursor.fetchall()
    if tranRaw:
        transaction_history_data.extend([History(*point) for point in tranRaw])
    else:
        transaction_history_data = None

    owned_shares = get_user_shares(user_id, asset_id, type)
    ask_count = get_number_of_bids_or_asks(asset_id, type, 'ask')
    bid_count = get_number_of_bids_or_asks(asset_id, type, 'bid')

    cursor.execute('SELECT timestamp, price FROM transaction_history LIMIT 10')
    data = cursor.fetchall()

    serialized_data = json.dumps(data)
    print(serialized_data)

    connection.close()

    return render_template('asset.html', asset=asset_data, asset_type=type, count=count,  bids=bid_data, asks=ask_data, history=transaction_history_data, ask_count=ask_count, bid_count=bid_count, owned_shares=owned_shares, data=serialized_data)

@details_bp.route('/review_order')
@login_required
def review_order():

    #COMMISSION RATE 
    commission_rate = 2

    user_id = session.get('user_id')
    totalShares = None
    balance = None

    connection = sqlite3.connect("murilex.db")
    cursor = connection.cursor()

    asset_id = request.args.get('asset-id')
    asset_type = request.args.get('asset-type')
    quantity = request.args.get('quantity')
    limit_price = request.args.get('limit-price')
    transaction_type = request.args.get('transaction-type')
    order_type = request.args.get('order-type')

    Asset = namedtuple(
        'Asset',
        ['id', 'name', 'image', 'price', 'availability', 'author_name', 'author_image', 'category_name']
    )

    asset_data = None

    try:

        totalShares = get_user_shares(user_id, asset_id, asset_type)
        balance = get_user_available_balance(user_id)

        if asset_type == 'song':
            cursor.execute("""
                SELECT song.id, song.name, song.image, song.price, song.availability, artist.name AS author_name, artist.image AS author_image, categories.name AS category_name
                FROM song
                INNER JOIN artist ON song.artist_id = artist.id
                INNER JOIN categories ON song.category_id = categories.id
                WHERE song.id = ?""", (asset_id,))

            assetRaw = cursor.fetchone()
            asset_tuple = Asset(*assetRaw)
            asset_data = asset_tuple._asdict()

        elif asset_type == 'album':

            cursor.execute("""
                SELECT album.id, album.name, album.image, album.price, album.availability, artist.name AS author_name, artist.image AS author_image, categories.name AS category_name
                FROM album
                INNER JOIN artist ON album.artist_id = artist.id
                INNER JOIN categories ON album.category_id = categories.id
                WHERE album.id = ? """, (asset_id,))

            assetRaw = cursor.fetchone()
            asset_tuple = Asset(*assetRaw)
            asset_data = asset_tuple._asdict()

        elif asset_type == 'catalogue':

            Catalogue = namedtuple(
            'Catalogue',
            ['id', 'name', 'image', 'price', 'shares', 'category_name']
            )

            print(asset_id)

            cursor.execute("""
                SELECT catalogue.id, artist.name AS name, artist.image AS image, catalogue.price, catalogue.shares, artist.category_id AS category_name 
                FROM catalogue
                INNER JOIN artist ON catalogue.artist_id = artist.id
                WHERE catalogue.id = ?""", (asset_id,))

            assetRaw = cursor.fetchone()
            if assetRaw is not None:
                asset_tuple = Catalogue(*assetRaw)
                asset_data = asset_tuple._asdict()
                # Process asset_data here
            else:
                print("No data found for the given asset_name.")

        else:
            print("HTML error.")
    except Exception:

        # Handle exceptions here, e.g., log the error
        print(f"An error occurred: {Exception}")
    finally:
        connection.close()

    print("Order Type:", order_type)

    return render_template('review_order.html', asset=asset_data, asset_type=asset_type, quantity=quantity, limit_price=limit_price, transaction_type=transaction_type, user_id=user_id, totalShares=totalShares, balance=balance, order_type=order_type, commission=commission_rate)

@details_bp.route('/leaderboard')
def leaderboard():

    user_id = session.get('user_id')


    connection = sqlite3.connect("murilex.db")
    cursor = connection.cursor()

    Users = namedtuple("User", ["id", "username", "profile_image", "balance"])


    cursor.execute("""
            SELECT id, username, profile_Image, ROUND(balance, 2) AS balance
            FROM user
            ORDER BY balance DESC
        """)
    users = [Users(*row) for row in cursor.fetchall()]

    return render_template('leaderboard.html', users=users, user_id=user_id) 

@details_bp.route('/updateProfile', methods=['POST'])
def update_profile():
    conn = None

    try:
        with connect_db() as conn:
            cursor = conn.cursor()
            data = request.get_json()
            email = data['email']
            username = data['username']
            profile_image = data['profile_image']

            print('email:', email, ', username:', username, ', profile_image:', profile_image)

            # Assuming you have a user_id for the user you want to update
            user_id = session.get('user_id')  # Replace with the actual user_id

            if email is not None:
                cursor.execute('UPDATE user SET email = ? WHERE id = ?', (email, user_id))
            if username is not None:
                cursor.execute('UPDATE user SET username = ? WHERE id = ?', (username, user_id))
            if profile_image is not None:
                cursor.execute('UPDATE user SET profile_Image = ? WHERE id = ?', (profile_image, user_id))

            message = 'Profile updated'
            status_code = 200
    except Exception as e:
        print(f"Error updating profile: {str(e)}")
        message = 'Error updating profile'
        status_code = 500

    return jsonify({'message': message}), status_code

@details_bp.route('/thought_leadership')
def thought_leadership():
    return render_template('thought.html')
