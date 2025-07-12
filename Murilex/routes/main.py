import sqlite3, logging
from collections import namedtuple
from flask import Blueprint, render_template, session, make_response, request, jsonify, redirect
from routes.auth import login_required
from routes.database import (get_user_available_balance, get_user_pending_balance, calculate_user_initial_spend,
                            calculate_price_change, get_price_history, cancel_bid, cancel_ask, get_balance_history,
                            replenish_user_available_balance, get_bid_info, get_user_balance)
from collections import Counter

main_bp = Blueprint("main", __name__)

wk_commission_rate = 0.02

@main_bp.before_request
def before_request():
    session.setdefault('selected_graph_timeframe', '1week')

@main_bp.route('/update_settings', methods=['POST'])
def update_settings():
    selected_timeframe = request.form.get('price_change_timeframe')
    session['selected_price_change_timeframe'] = selected_timeframe
    print('price change timeframe=', session['selected_price_change_timeframe'])

    selected_graph_timeframe = request.form.get('graph_timeframe')
    session['selected_graph_timeframe'] = selected_graph_timeframe
    print('graphs timeframe=', session['selected_graph_timeframe'])

    return redirect('/settings')

@main_bp.route('/api/data_balance')
def get_balance_data():
    try:
        user_id = request.args.get('user_id')

        # Fetch and serialize your data from the database
        data = get_balance_history(user_id)

        # Serialize the data to JSON and return it
        return jsonify(data)
    except Exception as error:
        logging.error("Error in get_chart_data: %s", error)

@main_bp.route('/fetch-existing-orders')
def fetch_existing_orders():
    try:



        # Serialize the data to JSON and return it
        return jsonify(data)
    except Exception as error:
        logging.error("Error in get_chart_data: %s", error)

@main_bp.route('/api/data_rest')
def get_chart_data():
    try:
        asset_id = request.args.get('asset_id')
        asset_type = request.args.get('asset_type')
        timeframe = session.get('selected_graph_timeframe', 'max')

        # Fetch and serialize your data from the database
        data = get_price_history(asset_id, asset_type, timeframe)

        # Serialize the data to JSON and return it
        return jsonify(data)
    except Exception as error:
        logging.error("Error in get_chart_data: %s", error)

@main_bp.route('/api/data_asset')
def get_asset_chart_data():
    try:
        asset_id = request.args.get('asset_id')
        asset_type = request.args.get('asset_type')
        timeframe = request.args.get('timeframe')

        # Fetch and serialize your data from the database
        data = get_price_history(asset_id, asset_type, timeframe)

        # Serialize the data to JSON and return it
        return jsonify(data)
    except Exception as error:
        logging.error("Error in get_chart_data: %s", error)

@main_bp.route('/cancel_the_bid/', methods=['POST'])
def cancel_the_bid():
    try:
        # Get JSON data from the request
        data = request.get_json()

        # Check if 'item_id' is present in the JSON data
        if 'item_id' not in data:
            return jsonify({'error': 'Missing item_id in the request data'}), 400

        bid_id = data['item_id']

        bid_info = get_bid_info(bid_id)

        if bid_info:
            amount = (bid_info['price']*bid_info['quantity'])*(1 + wk_commission_rate)
            replenish_user_available_balance(bid_info['user_id'], amount)

        if cancel_bid(bid_id):
            return jsonify({'message': 'Bid canceled successfully'}), 200
        else:
            return jsonify({'error': 'Failed to cancel the bid'}), 500

    except Exception as error:
        logging.error("Error in cancel_the_bid: %s", error)

@main_bp.route('/cancel_the_ask/', methods=['POST'])
def cancel_the_ask():
    try:
        # Get JSON data from the request
        data = request.get_json()
        
        # Check if 'item_id' is present in the JSON data
        if 'item_id' not in data:
            return jsonify({'error': 'Missing item_id in the request data'}), 400
        
        ask_id = data['item_id']
        print(ask_id)

        if cancel_ask(ask_id):
            return jsonify({'message': 'Ask canceled successfully'}), 200
        else:
            return jsonify({'error': 'Failed to cancel the ask'}), 500

    except Exception as error:
        logging.error("Error in cancel_the_ask: %s", error)

@main_bp.route('/search', methods=['GET'])
def search():
    query = request.args.get('query')
    results = Item.query.filter(Item.name.contains(query)).all()
    return jsonify([r.name for r in results])

@main_bp.route('/')
def home():
    connection = sqlite3.connect("murilex.db")
    cursor = connection.cursor()

    # Define namedtuple
    Artist = namedtuple("Artist", ["id", "name", "image", "price", "shares", "catalogue_id", "price_change"])

    # Fetch artist information and availability (number of shares) from catalogue
    cursor.execute("""
        SELECT
            artist.id AS artist_id,
            artist.name AS artist_name,
            artist.image AS artist_image,
            catalogue.price AS price,
            catalogue.shares AS shares,
            catalogue.id AS catalogue_id
        FROM catalogue
        LEFT JOIN artist ON artist.id = catalogue.artist_id;
    """)
    result_rows = cursor.fetchall()

    # Organize data into appropriate data structures
    artists_data = []

    for row in result_rows:
        if row[4] is not None:
            catalogue_id = row[5]
            asset_id = catalogue_id  # Assuming artist_id corresponds to asset_id
            asset_type = 'catalogue'  # You may need to adjust this based on your database structure

            timestamp = session.get('selected_price_change_timeframe', 'single')

            price_change = 0
            the_price_change = calculate_price_change(asset_id, asset_type, timestamp)
            if the_price_change:
                price_change = the_price_change

            artist = Artist(id=row[0], name=row[1], image=row[2], price=row[3], shares=row[4], catalogue_id=row[5], price_change=price_change)
            artists_data.append(artist)

    connection.close()

    return render_template('home.html', artists=artists_data)

@main_bp.route('/portfolio')
@login_required
def portfolio():
    user_id = session.get('user_id')
    timestamp = session.get('selected_price_change_timeframe', 'single')
    print('timestamp =', timestamp)

    is_transaction = request.args.get('transaction')

    connection = sqlite3.connect("murilex.db")
    cursor = connection.cursor()

    # Define namedtuple
    Catalog = namedtuple("Catalog", ["id", "price", "author_name", "author_image", "artist_id", "quantity", "price_change"])
    Album = namedtuple("Album", ["id", "price", "name", "image", "author_name", "author_image", "artist_id", "quantity", "price_change"])
    Song = namedtuple("Song", ["id", "price", "name", "image", "author_name", "author_image", "artist_id", "quantity", "price_change"])
    Bids = namedtuple("Bids", ["id", "asset_id", "asset_name", "asset_image", "asset_type", "price", "quantity"])
    Asks = namedtuple("Asks", ["id", "asset_id", "asset_name", "asset_image", "asset_type", "price", "quantity"])


    # Fetch data from the watchlist table
    cursor.execute("SELECT asset_id, asset_type FROM portfolio WHERE user_id = ?", (user_id,))
    portfolio_rows = cursor.fetchall()

    catalogs = []
    albums = []
    songs = []
    bid_data = []
    ask_data = []

    for row in portfolio_rows:
        item_id = row[0]
        item_type = row[1]

        # Emit a request to calculate price change for the current asset
        #price_change=price_change_namespace.emit('calculate_price_change', {'asset_id': item_id, 'asset_type': item_type})
        #print('price change=', price_change)

        # Emit a request to price for the current asset
        #price=price_namespace.emit('get_price', {'asset_id': item_id, 'asset_type': item_type})
        #print('price=', price)

        if item_type == 'song':
            cursor.execute("""SELECT song.id, song.price, song.name, song.image, artist.name AS author_name, artist.image AS author_image, artist_id, quantity
                            FROM portfolio
                            INNER JOIN song ON portfolio.asset_id = song.id AND portfolio.asset_type = 'song'
                            JOIN artist ON artist.id = song.artist_id
                           WHERE song.id = ? AND portfolio.user_id = ?""", (item_id, user_id))
            song_data = cursor.fetchone()
            price_change = calculate_price_change(item_id, item_type, timestamp)
            songs.append(Song(*song_data, price_change = price_change))

        elif item_type == 'album':
            cursor.execute("""SELECT album.id, album.price, album.name, album.image, artist.name AS author_name, artist.image AS author_image, artist_id, quantity
                            FROM portfolio
                            INNER JOIN album ON portfolio.asset_id = album.id AND portfolio.asset_type = 'album'
                            JOIN artist ON album.artist_id = artist.id
                           WHERE album.id = ? AND portfolio.user_id = ?""", (item_id, user_id))
            album_data = cursor.fetchone()
            price_change = calculate_price_change(item_id, item_type, timestamp)
            albums.append(Album(*album_data, price_change = price_change))

        elif item_type == 'catalogue':
            cursor.execute("""SELECT catalogue.id, catalogue.price, artist.name AS author_name, artist.image AS author_image, artist_id, portfolio.quantity
                            FROM portfolio
                            JOIN catalogue ON portfolio.asset_id = catalogue.id
                            INNER JOIN artist ON catalogue.artist_id = artist.id 
                           WHERE catalogue.id = ? AND portfolio.user_id = ?""", (item_id, user_id))
            catalog_data = cursor.fetchone()
            price_change = calculate_price_change(item_id, item_type, timestamp)
            catalogs.append(Catalog(*catalog_data, price_change = price_change))

        else:
            print("Error: route(/porfolio).")
            return

    cursor.execute("""
    SELECT 
        b.id,
        b.asset_id,
        CASE 
            WHEN b.asset_type = 'song' THEN s.name
            WHEN b.asset_type = 'album' THEN a.name
            WHEN b.asset_type = 'catalogue' THEN (SELECT name FROM artist WHERE id = (SELECT artist_id FROM catalogue WHERE id = b.asset_id))
            ELSE NULL
        END as asset_name,
        CASE 
            WHEN b.asset_type = 'song' THEN s.image
            WHEN b.asset_type = 'album' THEN a.image
            WHEN b.asset_type = 'catalogue' THEN (SELECT image FROM artist WHERE id = (SELECT artist_id FROM catalogue WHERE id = b.asset_id))
            ELSE NULL
        END as asset_image,
        b.asset_type, 
        b.price, 
        b.quantity
    FROM bids AS b
    LEFT JOIN song AS s ON b.asset_id = s.id AND b.asset_type = 'song'
    LEFT JOIN album AS a ON b.asset_id = a.id AND b.asset_type = 'album'
    LEFT JOIN catalogue AS c ON b.asset_id = c.id AND b.asset_type = 'catalogue'
    WHERE b.user_id = ?
    """, (user_id,))
    bidRaw = cursor.fetchall()
    if bidRaw:
        bid_data = [Bids(*row) for row in bidRaw]


    cursor.execute("""
    SELECT 
        b.id,
        b.asset_id,
        CASE 
            WHEN b.asset_type = 'song' THEN s.name
            WHEN b.asset_type = 'album' THEN a.name
            WHEN b.asset_type = 'catalogue' THEN (SELECT name FROM artist WHERE id = (SELECT artist_id FROM catalogue WHERE id = b.asset_id))
            ELSE NULL
        END as asset_name,
        CASE 
            WHEN b.asset_type = 'song' THEN s.image
            WHEN b.asset_type = 'album' THEN a.image
            WHEN b.asset_type = 'catalogue' THEN (SELECT image FROM artist WHERE id = (SELECT artist_id FROM catalogue WHERE id = b.asset_id))
            ELSE NULL
        END as asset_image,
        b.asset_type, 
        b.price, 
        b.quantity
    FROM asks AS b
    LEFT JOIN song AS s ON b.asset_id = s.id AND b.asset_type = 'song'
    LEFT JOIN album AS a ON b.asset_id = a.id AND b.asset_type = 'album'
    LEFT JOIN catalogue AS c ON b.asset_id = c.id AND b.asset_type = 'catalogue'
    WHERE b.user_id = ?
    """, (user_id,))
    askRaw = cursor.fetchall()
    if askRaw:
        ask_data = [Asks(*row) for row in askRaw]

    balance = get_user_balance(user_id)
    available_balance = get_user_available_balance(user_id)
    pending_balance = get_user_pending_balance(user_id)
    user_initial_spend = calculate_user_initial_spend(user_id)

    connection.close()

    return render_template('portfolio.html', catalogs=catalogs, albums=albums, songs=songs, bids=bid_data, asks=ask_data, transaction=is_transaction, available_balance=available_balance, balance=balance, pending_balance=pending_balance, total_allocated=user_initial_spend)

@main_bp.route('/discover')
def discover():
    connection = sqlite3.connect("murilex.db")
    cursor = connection.cursor()

    # Define namedtuples
    Artist = namedtuple("Artist", ["id", "name", "image", "category_id", "albums", "songs"])
    Album = namedtuple("Album", ["name", "image"])
    Song = namedtuple("Song", ["name", "image", ])
    
    # Fetch data for featured artists and their albums using JOIN
    cursor.execute("""
        SELECT
            artist.id AS artist_id,
            artist.name AS artist_name,
            artist.image AS artist_image,
            artist.category_id AS artist_category_id,
            album.name AS album_name,
            album.image AS album_image
        FROM artist
        LEFT JOIN (
            SELECT album.*, ROW_NUMBER() OVER (PARTITION BY artist_id ORDER BY album.id) AS album_rank
            FROM album
        ) AS album ON artist.id = album.artist_id AND album.album_rank <= 4
        WHERE artist.featured = 1
        ORDER BY artist.id, album.album_rank;
        """)

    result_rows = cursor.fetchall()

    # Organize data into appropriate data structures
    featured_artists_data = {}
    for row in result_rows:
        artist_id = row[0]
        if artist_id not in featured_artists_data:
            artist = Artist(id=row[0], name=row[1], image=row[2], category_id=row[3], albums=[], songs=[])
            featured_artists_data[artist_id] = artist

        if row[4] is not None and row[5] is not None:
            album = Album(name=row[4], image=row[5])
            featured_artists_data[artist_id].albums.append(album)

    # Convert the dictionary to a list of artists
    featured_artists_list = list(featured_artists_data.values())

    # Fetch data for featured artists' songs
    cursor.execute("""
        SELECT
            artist.id AS artist_id,
            song.name AS song_name,
            song.image AS song_image,
            song.category_id AS song_category
        FROM artist
        LEFT JOIN (
            SELECT song.*, ROW_NUMBER() OVER (PARTITION BY artist_id ORDER BY song.id) AS song_rank
            FROM song
        ) AS song ON artist.id = song.artist_id AND song.song_rank <= 4
        WHERE artist.featured = 1
        ORDER BY artist.id, song.song_rank;
    """)
    songs_result = cursor.fetchall()

    # Organize songs data into the existing featured_artists_data dictionary
    for row in songs_result:
        artist_id = row[0]
        if artist_id in featured_artists_data:
            song = Song(name=row[1], image=row[2])
            artist = featured_artists_data[artist_id]
            updated_songs = artist.songs + [song]  # Create a new list with the updated songs
            featured_artists_data[artist_id] = artist._replace(songs=updated_songs)

    # Convert the dictionary to a list of artists
    featured_artists_list = [artist._replace(songs=artist.songs) for artist in featured_artists_data.values()]

    # Count the number of featured artists found
    num_artists_found = len(featured_artists_list)

    cursor.execute("""
        SELECT categories.name AS category, categories.image AS image
        FROM categories
        LEFT JOIN song ON categories.id = song.category_id
        LEFT JOIN album ON categories.id = album.category_id
        WHERE song.category_id IS NOT NULL OR album.category_id IS NOT NULL
        GROUP BY category
    """)
    category_rows = cursor.fetchall()

    # Create a list of named tuples to store the data
    CategoryData = namedtuple('CategoryData', ['category', 'image'])
    category_data = [CategoryData(*row) for row in category_rows]

    connection.close()

    return render_template('discover.html', artists=featured_artists_list, num_artists=num_artists_found, category_data=category_data)

@main_bp.route('/watchlist')
@login_required
def watchlist():
    user_id = session.get('user_id')
    timestamp = session.get('selected_price_change_timeframe', 'single')

    connection = sqlite3.connect("murilex.db")
    cursor = connection.cursor()

    # Define namedtuple
    Catalog = namedtuple("Catalog", ["id","author_name", "author_image", "artist_id", "price", "shares", "price_change"])
    Album = namedtuple("Album", ["id", "name", "image", "author_name", "artist_id", "author_image", "price", "availability", "price_change"])
    Song = namedtuple("Song", ["id", "name", "image", "author_name", "artist_id", "author_image", "price", "availability", "price_change"])
    Categories = namedtuple("Categories", ["id", "name", "image"])

    # Fetch data from the watchlist table
    cursor.execute("SELECT item_id, item_type FROM watchlist WHERE user_id = ?", (user_id,))
    watchlist_rows = cursor.fetchall()

    catalogs = []
    albums = []
    songs = []
    categories = []

    # Loop through the watchlist items and retrieve details from respective tables
    for row in watchlist_rows:
        item_id = row[0]
        item_type = row[1]

        if item_type == 'song':
            cursor.execute("""SELECT song.id, song.name, song.image, artist.name AS author_name, artist_id, artist.image AS author_image, song.price, song.availability
                            FROM song
                            INNER JOIN artist ON song.artist_id = artist.id WHERE song.id = ?""", (item_id,))
            song_data = cursor.fetchone()
            price_change = calculate_price_change(item_id, item_type, timestamp)
            songs.append(Song(*song_data, price_change = price_change))

        if item_type == 'album':
            cursor.execute("""SELECT album.id, album.name, album.image, artist.name AS author_name, artist_id, artist.image AS author_image, album.price, album.availability
                            FROM album
                            INNER JOIN artist ON album.artist_id = artist.id WHERE album.id = ?""", (item_id,))
            album_data = cursor.fetchone()
            price_change = calculate_price_change(item_id, item_type, timestamp)
            albums.append(Album(*album_data, price_change = price_change))

        if item_type == 'catalogue':
            cursor.execute("""SELECT catalogue.id, artist.name AS author_name, artist.image AS author_image, artist_id, catalogue.price, catalogue.shares
                            FROM catalogue
                            INNER JOIN artist ON catalogue.artist_id = artist.id WHERE catalogue.id = ?""", (item_id,))
            catalog_data = cursor.fetchone()
            price_change = calculate_price_change(item_id, item_type, timestamp)
            catalogs.append(Catalog(*catalog_data, price_change = price_change))

        if item_type == 'categories':
            cursor.execute("""SELECT id, name, image
                            FROM categories
                            WHERE categories.id = ?""", (item_id,))
            categories_data = cursor.fetchone()
            categories.append(Categories(*categories_data))

    connection.close()

    # Create a response object
    response = make_response(render_template('watchlist.html', catalogs=catalogs, albums=albums, songs=songs, categories=categories))

    # Set cache control headers to prevent caching
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'

    return response

@main_bp.route('/<category_name>/<asset_type>')
def category(category_name, asset_type):
    connection = sqlite3.connect("murilex.db")
    cursor = connection.cursor()
    timestamp = session.get('selected_price_change_timeframe', 'single')
    category_id = []

    # Fetch the category information
    cursor.execute("SELECT id, image FROM categories WHERE name = ?", (category_name,))
    row = cursor.fetchone()

    if row is not None:
        category_id, category_image = row
        # Now you can use category_id and category_image as needed
    else:
        # Handle the case when no rows were found for the given category_name
        print("Category not found")

    # Initialize 'data' with an empty list before the if conditions
    data = []

    if asset_type == "song":
        # Fetch songs data
        Song = namedtuple('Song', ['id', 'name', 'image', 'author_name', 'author_image', 'artist_id', 'price', 'availability', 'price_change'])
        cursor.execute("""
            SELECT song.id, song.name, song.image, artist.name AS author_name, artist.image AS author_image, artist.id, song.price, song.availability
            FROM song
            INNER JOIN artist ON song.artist_id = artist.id
            WHERE song.category_id = ?
            LIMIT 50
        """, (category_id,))
        song_data = cursor.fetchall()


        for song in song_data:
            song_id = song[0]  # Extract the song ID
            price_change = calculate_price_change(song_id, 'song', timestamp)
            data.append(Song(*song, price_change=price_change))

    elif asset_type == 'album':
        # Fetch albums data
        Album = namedtuple('Album', ['id', 'name', 'image', 'author_name', 'author_image', 'artist_id', 'price', 'availability', 'price_change'])
        cursor.execute("""
            SELECT album.id, album.name, album.image, artist.name AS author_name, artist.image AS author_image, artist_id, album.price, album.availability
            FROM album
            INNER JOIN artist ON album.artist_id = artist.id
            WHERE album.category_id = ?
            LIMIT 50
        """, (category_id,))
        album_data = cursor.fetchall()

        for album in album_data:
            album_id = album[0]  # Extract the song ID
            price_change = calculate_price_change(album_id, 'album', timestamp)
            data.append(Album(*album, price_change=price_change))
        
    elif asset_type == 'catalogue':
        # Fetch catalogues data
        Catalogue = namedtuple('Catalogue', ['id', 'artist_id', 'price', 'availability', 'category_id', 'image', 'name', 'price_change'])
        cursor.execute("""
            SELECT catalogue.id, catalogue.artist_id, catalogue.price, catalogue.shares AS availability, artist.category_id AS category_id, artist.image AS image, artist.name AS name
            FROM catalogue
            INNER JOIN artist ON catalogue.artist_id = artist.id
            WHERE artist.category_id = ?
            LIMIT 50
        """, (category_id,))
        catalog_data = cursor.fetchall()

        for catalog in catalog_data:
            catalog_id = catalog[0]  # Extract the song ID
            price_change = calculate_price_change(catalog_id, 'catalogue', timestamp)
            data.append(Catalogue(*catalog, price_change=price_change))


    user_id = session.get('user_id')

    item_watchlist_count = {}  # Create a dictionary to store item_id and watchlist status

    # Loop through the data to check if each item is in the watchlist
    for item in data:
        cursor.execute('SELECT COUNT(*) FROM watchlist WHERE user_id = ? AND item_id = ? AND item_type = ?',
                       (user_id, item.id, asset_type))
        count = cursor.fetchone()[0]
        item_watchlist_count[item.id] = count

    # Handling categories
    category_watchlist_count = {}

    cursor.execute('SELECT COUNT(*) FROM watchlist WHERE user_id = ? AND item_id = ? AND item_type = ?',
                (user_id, category_id, "categories"))
    count = cursor.fetchone()[0]
    category_watchlist_count[category_id] = count

    connection.close()

    return render_template('category.html', category_name=category_name, data=data, category_image=category_image, asset_type=asset_type, item_watchlist_count=item_watchlist_count, category_watchlist_count=category_watchlist_count, category_id=category_id)

@main_bp.route('/profile/<int:user_id>')
@login_required
def profile(user_id):
    connection = sqlite3.connect("murilex.db")
    cursor = connection.cursor()
    timestamp = session.get('selected_price_change_timeframe', 'single')

    if user_id == session.get('user_id'):
        user_status = 'True'
    else:
        user_status = 'False'

    Catalog = namedtuple("Catalog", ["id", "price", "author_name", "author_image", "quantity", "price_change"])
    Album = namedtuple("Album", ["id", "price", "name", "image", "author_name", "author_image", "quantity", "price_change"])
    Song = namedtuple("Song", ["id", "price", "name", "image", "author_name", "author_image", "quantity", "price_change"])

    cursor.execute("SELECT asset_id, asset_type FROM portfolio WHERE user_id = ?", (user_id,))
    portfolio_rows = cursor.fetchall()

    catalogs = []
    albums = []
    songs = []

    for row in portfolio_rows:
        item_id = row[0]
        item_type = row[1]

        # Emit a request to calculate price change for the current asset
        #price_change=price_change_namespace.emit('calculate_price_change', {'asset_id': item_id, 'asset_type': item_type})
        #print('price change=', price_change)

        # Emit a request to price for the current asset
        #price=price_namespace.emit('get_price', {'asset_id': item_id, 'asset_type': item_type})
        #print('price=', price)

        if item_type == 'song':
            cursor.execute("""SELECT song.id, song.price, song.name, song.image, artist.name AS author_name, artist.image AS author_image, quantity
                            FROM portfolio
                            INNER JOIN song ON portfolio.asset_id = song.id AND portfolio.asset_type = 'song'
                            JOIN artist ON artist.id = song.artist_id
                           WHERE song.id = ? AND portfolio.user_id = ?""", (item_id, user_id))
            song_data = cursor.fetchone()
            price_change = calculate_price_change(item_id, item_type, timestamp)
            songs.append(Song(*song_data, price_change = price_change))

        elif item_type == 'album':
            cursor.execute("""SELECT album.id, album.price, album.name, album.image, artist.name AS author_name, artist.image AS author_image, quantity
                            FROM portfolio
                            INNER JOIN album ON portfolio.asset_id = album.id AND portfolio.asset_type = 'album'
                            JOIN artist ON album.artist_id = artist.id
                           WHERE album.id = ? AND portfolio.user_id = ?""", (item_id, user_id))
            album_data = cursor.fetchone()
            price_change = calculate_price_change(item_id, item_type, timestamp)
            albums.append(Album(*album_data, price_change = price_change))

        elif item_type == 'catalogue':
            cursor.execute("""SELECT catalogue.id, catalogue.price, artist.name AS author_name, artist.image AS author_image, portfolio.quantity
                            FROM portfolio
                            JOIN catalogue ON portfolio.asset_id = catalogue.id
                            INNER JOIN artist ON catalogue.artist_id = artist.id 
                           WHERE catalogue.id = ? AND portfolio.user_id = ?""", (item_id, user_id))
            catalog_data = cursor.fetchone()
            price_change = calculate_price_change(item_id, item_type, timestamp)
            catalogs.append(Catalog(*catalog_data, price_change = price_change))

        else:
            print("Error: route(/porfolio).")
            return

    Users = namedtuple("User", ["id", "username", "profile_image", "balance"])

    # Fetch artist information and availability (number of shares) from catalogue
    cursor.execute("""
            SELECT username, balance, email, profile_Image, available_balance
            FROM user
            WHERE id = ?
            LIMIT 1
        """, (user_id,))
    username = cursor.fetchone()

    user_username = username[0]

    cursor.execute("""
            SELECT id, username, profile_Image, balance
            FROM user
            ORDER BY balance DESC
        """)
    users = [Users(*row) for row in cursor.fetchall()]

    Transactions = namedtuple("Transaction", ["id", "asset_id", "asset_name", "image", "asset_type", "price", "quantity", "type", "balance", "timestamp"])
    transaction_data = []

    cursor.execute("""
    SELECT 
        t.id,
        t.asset_id,
        CASE 
            WHEN t.asset_type = 'song' THEN s.name
            WHEN t.asset_type = 'album' THEN a.name
            WHEN t.asset_type = 'catalogue' THEN (SELECT name FROM artist WHERE id = (SELECT artist_id FROM catalogue WHERE id = t.asset_id))
            ELSE NULL
        END as asset_name,
        CASE 
            WHEN t.asset_type = 'song' THEN s.image
            WHEN t.asset_type = 'album' THEN a.image
            WHEN t.asset_type = 'catalogue' THEN (SELECT image FROM artist WHERE id = (SELECT artist_id FROM catalogue WHERE id = t.asset_id))
            ELSE NULL
        END as asset_image,
        t.asset_type, 
        t.price, 
        t.quantity,
        t.transaction_type,
        ROUND(t.balance, 2) as rounded_balance,
        t.timestamp
    FROM transaction_history AS t
    LEFT JOIN song AS s ON t.asset_id = s.id AND t.asset_type = 'song'
    LEFT JOIN album AS a ON t.asset_id = a.id AND t.asset_type = 'album'
    LEFT JOIN catalogue AS c ON t.asset_id = c.id AND t.asset_type = 'catalogue'
    WHERE t.user_id = ?
    ORDER BY timestamp DESC
    """, (user_id,))
    transactionRaw = cursor.fetchall()
    if transactionRaw:
        transaction_data = [Transactions(*row) for row in transactionRaw]

    asset_names = [transaction.asset_name for transaction in transaction_data]
    most_common_asset_name = {}
    if asset_names:
        most_common_asset_name = Counter(asset_names).most_common(1)[0][0]

    return render_template('profile.html', user_status=user_status, user_id=user_id, username=username[0], balance=round(username[1], 2), email=username[2], profile_image=username[3], available_balance= round(username[4], 2), users=users, catalogs=catalogs, albums=albums, songs=songs, transactions=transaction_data, most_traded=most_common_asset_name)

@main_bp.route('/settings')
def settings():
    selected_graph_timeframe = session.get('selected_graph_timeframe', '1week')
    selected_price_change_timeframe = session.get('selected_price_change_timeframe', 'single')

    return render_template('settings.html', selected_graph_timeframe = selected_graph_timeframe, selected_price_change_timeframe = selected_price_change_timeframe)
