import sqlite3, logging, traceback
from flask import session, jsonify
from datetime import datetime, timedelta

# Define a connection to the database
def connect_db():
    return sqlite3.connect('murilex.db')

# Create tables if they don't exist
def create_tables():
    conn = None

    try:
        with connect_db() as conn:
            cursor = conn.cursor()

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS bids (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    asset_id INTEGER NOT NULL,
                    asset_type TEXT NOT NULL,
                    price DECIMAL(10, 2) NOT NULL,
                    quantity DECIMAL(10, 2) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS asks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    asset_id INTEGER NOT NULL,
                    asset_type TEXT NOT NULL,
                    price DECIMAL(10, 2) NOT NULL,
                    quantity DECIMAL(10, 2) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Create more tables if needed

            conn.commit()

    except Exception as error:
        logging.error("Error in create_tables: %s", error)
        if conn:
            conn.rollback()

    finally:
        if conn:
            conn.close()

# Insert a bid into the database
def insert_bid(bid_data):
    conn = None

    try:
        with connect_db() as conn:
            cursor = conn.cursor()

            # Check for an existing bid for the same item at a similar price
            cursor.execute('SELECT * FROM bids WHERE asset_id = ? AND asset_type = ? AND price = ? AND user_id = ?',
                           (bid_data['asset_id'], bid_data['asset_type'], bid_data['price'], bid_data['user_id']))
            existing_bid = cursor.fetchone()

            if existing_bid is not None:
                # If an existing bid is found, update its quantity
                new_quantity = existing_bid[5] + bid_data['quantity']
                cursor.execute('UPDATE bids SET quantity = ? WHERE id = ?', (new_quantity, existing_bid[0]))
            else:
                cursor.execute('''
                        INSERT INTO bids (user_id, asset_id, asset_type, price, quantity, created_at)
                        VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                    ''', (bid_data['user_id'], bid_data['asset_id'], bid_data['asset_type'],
                        bid_data['price'], bid_data['quantity']))

            conn.commit()

    except Exception as error:
        logging.error("Error in insert_bid: %s", error)
        if conn:
            conn.rollback()

    finally:
        print('quantity:', bid_data['quantity'])
        if conn:
            conn.close()

# Insert an ask into the database
def insert_ask(ask_data):
    conn = None

    try:
        with connect_db() as conn:
            cursor = conn.cursor()

                    # Check for an existing bid for the same item at a similar price
            cursor.execute('SELECT * FROM asks WHERE asset_id = ? AND asset_type = ? AND price = ? AND user_id = ?',
                           (ask_data['asset_id'], ask_data['asset_type'], ask_data['price'], ask_data['user_id']))
            existing_ask = cursor.fetchone()

            if existing_ask is not None:
                # If an existing bid is found, update its quantity
                new_quantity = existing_ask[5] + ask_data['quantity']
                cursor.execute('UPDATE asks SET quantity = ? WHERE id = ?', (new_quantity, existing_ask[0]))
            else:
                # If no existing ask is found, insert the new ask
                cursor.execute('''
                    INSERT INTO asks (user_id, asset_id, asset_type, price, quantity)
                    VALUES (?, ?, ?, ?, ?)
                ''', (ask_data['user_id'], ask_data['asset_id'], ask_data['asset_type'],
                    ask_data['price'], ask_data['quantity']))

            conn.commit()

    except Exception as error:
        logging.error("Error in insert_ask: %s", error)
        if conn:
            conn.rollback()

    finally:
        if conn:
            conn.close()

def delete_bid(bid_id):
    conn = None

    try:
        with connect_db() as conn:
            cursor = conn.cursor()

            # Execute a SQL query to delete the bid with the given id
            cursor.execute('DELETE FROM bids WHERE id = ?', (bid_id,))
            
            # Commit the changes
            conn.commit()

    except Exception as error:
        logging.error("Error in delete_bid: %s", error)
        if conn:
            conn.rollback()

    finally:
        if conn:
            conn.close()

def delete_ask(ask_id):
    conn = None

    try:
        with connect_db() as conn:
            cursor = conn.cursor()

            # Execute a SQL query to delete the ask with the given id
            cursor.execute('DELETE FROM asks WHERE id = ?', (ask_id,))

            # Commit the changes
            conn.commit()

    except Exception as error:
        logging.error("Error in delete_ask: %s", error)
        if conn:
            conn.rollback()

    finally:
        if conn:
            conn.close()

# Retrieve bids from the database
def get_bids(asset_id, asset_type):
    conn = None

    try:
        with connect_db() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                            SELECT * FROM bids
                            WHERE asset_id = ? AND asset_type = ?
                            ORDER BY price ASC, created_at DESC
                        """, (asset_id, asset_type))
            bids_data = cursor.fetchall()

            bids = []
            for bid_data in bids_data:
                bid = {
                    'id': bid_data[0],
                    'user_id': bid_data[1],
                    'asset_id': bid_data[2],
                    'asset_type': bid_data[3],
                    'price': bid_data[4],
                    'quantity': bid_data[5],
                    'created_at': bid_data[6]
                }
                bids.append(bid)

            if bids is None:
                return []
            else:
                return bids

    except Exception as error:
        logging.error("Error in get_bids: %s", error)
        if conn:
            conn.rollback()

    finally:
        if conn:
            conn.close()

# Retrieve asks from the database
def get_asks(asset_id, asset_type):
    conn = None

    try:
        with connect_db() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                            SELECT * FROM asks
                            WHERE asset_id = ? AND asset_type = ?
                            ORDER BY price ASC, created_at DESC
                        """, (asset_id, asset_type))
            asks_data = cursor.fetchall()

            asks = []
            for ask_data in asks_data:
                ask = {
                    'id': ask_data[0],
                    'user_id': ask_data[1],
                    'asset_id': ask_data[2],
                    'asset_type': ask_data[3],
                    'price': ask_data[4],
                    'quantity': ask_data[5],
                    'created_at': ask_data[6]
                }
                asks.append(ask)

            if asks is None:
                return []
            else:
                return asks

    except Exception as error:
        logging.error("Error in get_asks: %s", error)
        if conn:
            conn.rollback()

    finally:
        if conn:
            conn.close()

def check_bids():
    conn = None
    
    try:
        with connect_db() as conn:
            cursor = conn.cursor()

            # Execute a SQL query to delete the ask with the given id
            cursor.execute('DELETE FROM bids WHERE quantity = ?', (0,))

    except Exception as error:
        logging.error("Error in check_bids: %s", error)
        if conn:
            conn.rollback()

    finally:
        if conn:
            conn.close()

def check_asks():
    conn = None
    
    try:
        with connect_db() as conn:
            cursor = conn.cursor()

            # Execute a SQL query to delete the ask with the given id
            cursor.execute('DELETE FROM asks WHERE quantity = ?', (0,))

    except Exception as error:
        logging.error("Error in check_asks: %s", error)
        if conn:
            conn.rollback()

    finally:
        if conn:
            conn.close()

# Insert a transaction into the transaction history
def insert_transaction(transaction_data):
    conn = None

    try:
        with connect_db() as conn:
            cursor = conn.cursor()

            cursor.execute('''
                INSERT INTO transaction_history
                (user_id, asset_id, asset_type, transaction_type, price, quantity, balance)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (transaction_data['user_id'], transaction_data['asset_id'],
                transaction_data['asset_type'], transaction_data['transaction_type'],
                transaction_data['price'], transaction_data['quantity'],
                transaction_data['balance']))

            # Update the price in the corresponding table (assuming it's a different table)
            table_name = transaction_data['asset_type'].lower()
            cursor.execute(f'''
                UPDATE {table_name}
                SET price = ?
                WHERE id = ?
            ''', (transaction_data['price'], transaction_data['asset_id']))

            conn.commit()

    except Exception as error:
        logging.error("Error in insert_transaction: %s", error)
        if conn:
            conn.rollback()

    finally:
        if conn:
            conn.close()

# Update the order book in the database
def update_order_book_in_database(bids, asks):
    conn = None

    try:
        with connect_db() as conn:
            cursor = conn.cursor()

            # Clear existing bids and asks
            cursor.execute('DELETE FROM bids')
            cursor.execute('DELETE FROM asks')

            # Insert updated bids and asks
            for bid in bids:
                cursor.execute('''
                    INSERT INTO bids
                    (user_id, asset_id, asset_type, price, quantity, created_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (bid['user_id'], bid['asset_id'], bid['asset_type'],
                    bid['price'], bid['quantity'], bid['created_at']))

            for ask in asks:
                cursor.execute('''
                    INSERT INTO asks
                    (user_id, asset_id, asset_type, price, quantity, created_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (ask['user_id'], ask['asset_id'], ask['asset_type'],
                    ask['price'], ask['quantity'], ask['created_at']))

            conn.commit()

    except Exception as error:
        logging.error("Error in update_order_book_in_database: %s", error)
        if conn:
            conn.rollback()

    finally:
        if conn:
            conn.close()

def query_ask_bid_self_limitorder(asset_id, asset_type, user_id, order_action, price):
    conn = None

    try:
        with connect_db() as conn:
            cursor = conn.cursor()
            if order_action == 'buy':
                cursor.execute("""
                            SELECT price FROM asks
                            WHERE asset_id = ? AND asset_type = ? AND user_id = ?
                            ORDER BY price ASC, created_at DESC
                        """, (asset_id, asset_type, user_id))
                asks_data = cursor.fetchall()

                if not asks_data:
                    return False
                else:
                    for ask_tuple in asks_data:
                        ask_price = ask_tuple[0]
                        if ask_price <= price:
                            return True
                return False

            elif order_action == 'sell':
                cursor.execute("""
                            SELECT price FROM bids
                            WHERE asset_id = ? AND asset_type = ? AND user_id = ?
                            ORDER BY price ASC, created_at DESC
                        """, (asset_id, asset_type, user_id))
                bids_data = cursor.fetchall()

                if not bids_data:
                    return False
                else:
                    for bid_tuple in bids_data:
                        bid_price = bid_tuple[0]
                        if bid_price >= price:
                            return True
                return False

    except Exception as error:
        logging.error("Error in query_ask_bid_self: %s", error)
        if conn:
            conn.rollback()

    finally:
        if conn:
            conn.close()

def query_ask_bid_self_bestpriceorder(asset_id, asset_type, user_id, order_action):
    conn = None

    try:
        with connect_db() as conn:
            cursor = conn.cursor()
            if order_action == 'buy':
                cursor.execute("""
                            SELECT price FROM asks
                            WHERE asset_id = ? AND asset_type = ? AND user_id = ?
                            ORDER BY price ASC, created_at DESC
                            LIMIT 1
                        """, (asset_id, asset_type, user_id))
                asks_data = cursor.fetchone()

                if not asks_data:
                    return False
                else:
                    return True

            elif order_action == 'sell':
                cursor.execute("""
                            SELECT price FROM bids
                            WHERE asset_id = ? AND asset_type = ? AND user_id = ?
                            ORDER BY price ASC, created_at DESC
                            LIMIT 1
                        """, (asset_id, asset_type, user_id))
                bids_data = cursor.fetchone()

                if not bids_data:
                    return False
                else:
                    return True

    except Exception as error:
        logging.error("Error in query_ask_bid_self: %s", error)
        if conn:
            conn.rollback()

    finally:
        if conn:
            conn.close()

def calculate_price_change(asset_id, asset_type, timeframe):
    conn = None

    try:
        with connect_db() as conn:
            cursor = conn.cursor()

            price_change = None

            
            print('timeframe =', timeframe)

            if timeframe == 'single':
                # Retrieve the most recent purchase price for the specific asset
                cursor.execute('''
                    SELECT price
                    FROM transaction_history
                    WHERE asset_id = ? AND asset_type = ? AND transaction_type = 'purchase'
                    ORDER BY timestamp DESC
                    LIMIT 1
                ''', (asset_id, asset_type))


                current_purchase_price = cursor.fetchone()
                print('current_purchase_price=', current_purchase_price)

                if current_purchase_price:
                    current_purchase_price = current_purchase_price[0]
                else:
                    # Handle the case where there's no current purchase price available
                    price_change = 0
                    return price_change

                # Retrieve the previous purchase price for the specific asset
                cursor.execute('''
                    SELECT price
                    FROM transaction_history
                    WHERE asset_id = ? AND asset_type = ? AND transaction_type = 'purchase'
                    ORDER BY timestamp DESC
                    LIMIT 1 OFFSET 1
                ''', (asset_id, asset_type))

                previous_purchase_price = cursor.fetchone()

                if previous_purchase_price:
                    previous_purchase_price = previous_purchase_price[0]
                else:
                    # Handle the case where there's no previous purchase price available
                    price_change = 0
                    return price_change

                # Calculate the price change
                price_change = ((current_purchase_price - previous_purchase_price) / previous_purchase_price) * 100

            elif timeframe == 'day' or timeframe == 'week' or timeframe == 'month' or timeframe == 'year':

                timeframe_to_days = {
                    'day': 1,
                    'week': 7,
                    'month': 30,
                    'year': 365,
                }

                # Use the dictionary to get the corresponding day value based on the timeframe
                day = timeframe_to_days.get(timeframe, 0)  # Default to 0 if the timeframe is not found

                # Calculate the start and end timestamps for the past day
                end_timestamp = datetime.now()
                start_timestamp = end_timestamp - timedelta(days=day)

                # Retrieve the most recent purchase price for the specific asset within the day
                cursor.execute('''
                    SELECT price
                    FROM transaction_history
                    WHERE asset_id = ? AND asset_type = ? AND transaction_type = 'purchase'
                    AND timestamp >= ? AND timestamp <= ?
                    ORDER BY timestamp DESC
                    LIMIT 1
                ''', (asset_id, asset_type, start_timestamp, end_timestamp))
                current_purchase_price = cursor.fetchone()

                if current_purchase_price:
                    current_purchase_price = current_purchase_price[0]
                else:
                    # Handle the case where there's no current purchase price available
                    print('No current_purchase_price.')
                    price_change = 0
                    return price_change

                cursor.execute('''
                    SELECT price
                    FROM transaction_history
                    WHERE asset_id = ? AND asset_type = ? AND transaction_type = 'purchase'
                    AND timestamp >= ? AND timestamp <= ?
                    ORDER BY timestamp ASC
                    LIMIT 1
                ''', (asset_id, asset_type, start_timestamp, end_timestamp))
                previous_purchase_price = cursor.fetchone()

                if previous_purchase_price:
                    previous_purchase_price = previous_purchase_price[0]
                else:
                    # Handle the case where there's no previous purchase price available
                    print('No previous_price_change.')
                    price_change = 0
                    return price_change

                if previous_purchase_price is not None:
                    price_change = ((current_purchase_price - previous_purchase_price) / previous_purchase_price) * 100
                else:
                    price_change = 0
                    print('No previous_purchase_price.')

            elif timeframe == 'max':

                # Retrieve the most recent purchase price for the specific asset
                cursor.execute('''
                    SELECT price
                    FROM transaction_history
                    WHERE asset_id = ? AND asset_type = ? AND transaction_type = 'purchase'
                    ORDER BY timestamp DESC
                    LIMIT 1
                ''', (asset_id, asset_type))
                current_purchase_price = cursor.fetchone()

                if current_purchase_price:
                    current_purchase_price = current_purchase_price[0]
                else:
                    # Handle the case where there's no current purchase price available
                    price_change = 0
                    return price_change

                cursor.execute('''
                    SELECT price
                    FROM transaction_history
                    WHERE asset_id = ? AND asset_type = ? AND transaction_type = 'purchase'
                    ORDER BY timestamp ASC
                    LIMIT 1
                ''', (asset_id, asset_type))
                previous_purchase_price = cursor.fetchone()

                if previous_purchase_price:
                    previous_purchase_price = previous_purchase_price[0]
                else:
                    # Handle the case where there's no previous purchase price available
                    price_change = 0

                price_change = ((current_purchase_price - previous_purchase_price) / previous_purchase_price) * 100


            else:
                print('Error, timeframe: ', timeframe)

            return round(price_change, 2)
        
    except Exception as error:
        logging.error("Error in calculate_price_change: %s", error)
        traceback.print_exc()
        if conn:
            conn.rollback()

    finally:
        if conn:
            conn.close()

def get_price(asset_id, asset_type):
    conn = None
    price = None

    try:
        with connect_db() as conn:
            cursor = conn.cursor()

            # Retrieve the most recent purchase price for the specific asset
            cursor.execute('''
                SELECT price
                FROM transaction_history
                WHERE asset_id = ? AND asset_type = ? AND transaction_type = 'purchase'
                ORDER BY timestamp DESC
                LIMIT 1
            ''', (asset_id, asset_type))

            price = cursor.fetchone()
            print('price=', price)

            if price:
                price = price[0]
            else:
                # Handle the case where there's no current purchase price available
                price = 0
                return price

            return price

    except Exception as error:
        logging.error("Error in calculate_price_change: %s", error)
        if conn:
            conn.rollback()

    finally:
        if conn:
            conn.close()

def calculate_user_initial_spend(user_id):
    conn = None

    try:
        with connect_db() as conn:
            cursor = conn.cursor()

            # Retrieve all necessary data in one query
            cursor.execute('''
                SELECT p.asset_id, p.asset_type, p.quantity, t.price, t.quantity
                FROM portfolio p
                JOIN transaction_history t ON p.user_id = t.user_id AND p.asset_id = t.asset_id AND p.asset_type = t.asset_type
                WHERE p.user_id = ? AND t.transaction_type = 'purchase'
                ORDER BY t.timestamp ASC
            ''', (user_id,))

            raw_data = cursor.fetchall()

            # Process the data in Python
            total_spend = 0

            for asset_id, asset_type, quantity, price, quantity_hist in raw_data:
                if quantity_hist <= quantity:
                    total_spend += price * quantity_hist
                    quantity -= quantity_hist
                else:
                    total_spend += price * quantity
                    break

            return round(total_spend, 2) if total_spend else 0

    except Exception as error:
        logging.error("Error in calculate_user_initial_spend: %s", error)
        if conn:
            conn.rollback()

    finally:
        if conn:
            conn.close()

def emit_portfolio_update(user_id, socketio):
    conn = None
    
    try:
        with connect_db() as conn:
            cursor = conn.cursor()

            user_id = session.get('user_id')

            # Retrieve the user's portfolio data
            cursor.execute('''
                SELECT asset_id, asset_type, quantity
                FROM portfolio
                WHERE user_id = ?
            ''', (user_id,))

            portfolio_data = cursor.fetchall()

            # Prepare the portfolio data to be sent to clients
            portfolio_update = [{'asset_id': asset_id, 'asset_type': asset_type, 'quantity': quantity}
                                for asset_id, asset_type, quantity in portfolio_data]

            # Emit the portfolio update to the client
            socketio.emit('portfolio_update', portfolio_update, room=user_id)

    except Exception as error:
        logging.error("Error in emit_portfolio_update: %s", error)
        if conn:
            conn.rollback()

    finally:
        if conn:
            conn.close()

def get_user_available_balance(user_id):
    conn = None
    
    try:
        with connect_db() as conn:
            cursor = conn.cursor()

            cursor.execute('SELECT available_balance FROM user WHERE id = ?', (user_id,))
            user_balance = cursor.fetchone()

            conn.commit()

            if user_balance:
                return round(user_balance[0], 2)  # Assuming balance is stored as the first column
            else:
                return 0  # Default to 0 if user not found or balance not available

    except Exception as error:
        logging.error("Error in get_user_available_balance: %s", error)
        if conn:
            conn.rollback()

    finally:
        if conn:
            conn.close()

def get_user_balance(user_id):
    conn = None
    
    try:
        with connect_db() as conn:
            cursor = conn.cursor()
            
            cursor.execute('SELECT balance FROM user WHERE id = ?', (user_id,))
            user_balance = cursor.fetchone()

            conn.commit()

            if user_balance:
                return round(user_balance[0], 2)  # Assuming balance is stored as the first column
            else:
                return 0  # Default to 0 if user not found or balance not available
        
    except Exception as error:
        logging.error("Error in get_user_balance: %s", error)
        if conn:
            conn.rollback()

    finally:
        if conn:
            conn.close()

def get_user_pending_balance(user_id):
    conn = None

    try:
        with connect_db() as conn:
            cursor = conn.cursor()

        cursor.execute('SELECT balance FROM user WHERE id = ?', (user_id,))
        user_full_balance = cursor.fetchone()

        cursor.execute('SELECT available_balance FROM user WHERE id = ?', (user_id,))
        user_available_balance = cursor.fetchone()


        user_pending_balance = user_full_balance[0] - user_available_balance[0]

        if user_pending_balance and user_pending_balance > 0:
            return round(user_pending_balance, 2)  # Assuming balance is stored as the first column
        else:
            return 0  # Default to 0 if user not found or balance not available

    except Exception as error:
        logging.error("Error in get_user_pending_balance: %s", error)
        if conn:
            conn.rollback()

    finally:
        if conn:
            conn.close()

def deduct_user_available_balance(user_id, amount):
    conn = None

    try:
        with connect_db() as conn:
            cursor = conn.cursor()

        # Get the current user balance
        cursor.execute('SELECT available_balance FROM user WHERE id = ?', (user_id,))
        user_balance = cursor.fetchone()

        if user_balance:
            current_balance = user_balance[0]
            new_balance = current_balance - amount

            # Update the user's balance in the database
            cursor.execute('UPDATE user SET available_balance = ? WHERE id = ?', (new_balance, user_id))
            conn.commit()

            return new_balance
        else:
            return None  # User not found

    except Exception as error:
        logging.error("Error in deduct_user_available_balance: %s", error)
        if conn:
            conn.rollback()

    finally:
        if conn:
            conn.close()

def replenish_user_available_balance(user_id, amount):
    conn = None

    try:
        with connect_db() as conn:
            cursor = conn.cursor()

        # Get the current user balance
        cursor.execute('SELECT available_balance FROM user WHERE id = ?', (user_id,))
        user_balance = cursor.fetchone()

        if user_balance:
            current_balance = user_balance[0]
            new_balance = current_balance + amount

            # Update the user's balance in the database
            cursor.execute('UPDATE user SET available_balance = ? WHERE id = ?', (new_balance, user_id))
            conn.commit()

            return new_balance
        else:
            return None  # User not found

    except Exception as error:
        logging.error("Error in replenish_user_available_balance: %s", error)
        if conn:
            conn.rollback()

    finally:
        if conn:
            conn.close()

def deduct_user_balance(user_id, amount):
    conn = None

    try:
        with connect_db() as conn:
            cursor = conn.cursor()

        # Get the current user balance
        cursor.execute('SELECT balance FROM user WHERE id = ?', (user_id,))
        user_balance = cursor.fetchone()

        if user_balance:
            current_balance = user_balance[0]
            new_balance = current_balance - amount

            # Update the user's balance in the database
            cursor.execute('UPDATE user SET balance = ? WHERE id = ?', (new_balance, user_id))
            conn.commit()
            conn.close()

            return new_balance
        else:
            conn.close()
            return None  # User not found
        
    except Exception as error:
        logging.error("Error in deduct_user_balance: %s", error)
        if conn:
            conn.rollback()

    finally:
        if conn:
            conn.close()

def replenish_user_balance(user_id, amount):
    conn = None
    
    try:
        with connect_db() as conn:
            cursor = conn.cursor()

        # Get the current user balance
        cursor.execute('SELECT balance FROM user WHERE id = ?', (user_id,))
        user_balance = cursor.fetchone()

        if user_balance:
            current_balance = user_balance[0]
            new_balance = current_balance + amount

            # Update the user's balance in the database
            cursor.execute('UPDATE user SET balance = ? WHERE id = ?', (new_balance, user_id))
            conn.commit()

            return new_balance
        else:
            conn.close()
            return None  # User not found
        
    except Exception as error:
        logging.error("Error in replenish_user_balance: %s", error)
        if conn:
            conn.rollback()

    finally:
        if conn:
            conn.close()

def get_user_assets(user_id, asset_id, asset_type):
    conn = None
    
    try:
        with connect_db() as conn:
            cursor = conn.cursor()

        cursor.execute('''
            SELECT quantity
            FROM portfolio
            WHERE user_id = ? AND asset_id = ? AND asset_type = ?
        ''', (user_id, asset_id, asset_type))

        result = cursor.fetchone()
        conn.close()

        if result:
            return result[0]  # Return the quantity of the asset
        else:
            return 0  # Return 0 if the user doesn't have the asset in their portfolio
        
    except Exception as error:
        logging.error("Error in get_user_assets: %s", error)
        if conn:
            conn.rollback()

    finally:
        if conn:
            conn.close()

# Add assets to a user's portfolio
def add_to_portfolio(user_id, asset_id, asset_type, quantity):
    conn = None
    
    try:
        with connect_db() as conn:
            cursor = conn.cursor()

        # Check if the user already has this asset in their portfolio
        cursor.execute('''
            SELECT quantity FROM portfolio
            WHERE user_id = ? AND asset_id = ? AND asset_type = ?
        ''', (user_id, asset_id, asset_type))
        existing_asset_row = cursor.fetchone()

        if existing_asset_row is not None:
            existing_asset = int(existing_asset_row[0])
            # Update the quantity if the asset is already in the portfolio
            new_quantity = existing_asset + quantity
            cursor.execute('''
                UPDATE portfolio
                SET quantity = ?
                WHERE user_id = ? AND asset_id = ? AND asset_type = ?
            ''', (new_quantity, user_id, asset_id, asset_type))
        else:
            # Insert a new record if the asset is not in the portfolio
            cursor.execute('''
                INSERT INTO portfolio (user_id, asset_id, asset_type, quantity)
                VALUES (?, ?, ?, ?)
            ''', (user_id, asset_id, asset_type, quantity))

        conn.commit()
        
    except Exception as error:
        logging.error("Error in add_to_portfolio: %s", error)
        if conn:
            conn.rollback()

    finally:
        if conn:
            conn.close()

# Deduct assets from a user's portfolio
def deduct_from_portfolio(user_id, asset_id, asset_type, quantity):
    conn = None
    
    try:
        with connect_db() as conn:
            cursor = conn.cursor()

        # Check if the user has enough assets to deduct
        cursor.execute('''
            SELECT quantity FROM portfolio
            WHERE user_id = ? AND asset_id = ? AND asset_type = ?
        ''', (user_id, asset_id, asset_type))
        existing_asset_row = cursor.fetchone()
        existing_asset = int(existing_asset_row[0])
        print('existing_asset: ', existing_asset, 'quantity:', quantity)
        if existing_asset:
            if existing_asset > quantity:
                new_quantity = existing_asset - quantity
                cursor.execute('''
                    UPDATE portfolio
                    SET quantity = ?
                    WHERE user_id = ? AND asset_id = ? AND asset_type = ?
                ''', (new_quantity, user_id, asset_id, asset_type))
            elif existing_asset == quantity:
                cursor.execute('''
                    DELETE FROM portfolio
                    WHERE user_id = ? AND asset_id = ? AND asset_type = ?
                ''', (user_id, asset_id, asset_type))
            else:
                print('Error, unexpected outcome, negative quantity of asset in portfolio of user ?', user_id)
        else:
            # Handle the case where the user doesn't have the specified asset
            print(f'Error: User {user_id} does not have the asset')

        conn.commit()

    except Exception as error:
        logging.error("Error in deduct_from_portfolio: %s", error)
        if conn:
            conn.rollback()

    finally:
        if conn:
            conn.close()

def process_bid_order(user_id, asset_id, asset_type, quantity, wk_commission_rate):
    conn = None

    try:
        with connect_db() as conn:
            cursor = conn.cursor()

            # Initialize variables to track processed quantity and total cost
            processed_quantity = 0
            total_cost = 0
            sellers = {}
            sellers_balance = []
            users_balance = []

            while processed_quantity < quantity:
                # Query the cheapest available ask order
                cursor.execute('''
                    SELECT id, price, quantity, user_id FROM asks
                    WHERE asset_id = ? AND asset_type = ?
                    ORDER BY price ASC, created_at ASC
                    LIMIT 1
                ''', (asset_id, asset_type))
                ask_order = cursor.fetchone()

                if ask_order is None:
                    break  # No more asks available to fulfill the quantity

                ask_id, ask_price, ask_quantity, seller_id = ask_order

                # Calculate the remaining quantity to be processed
                remaining_quantity = quantity - processed_quantity

                if ask_quantity <= remaining_quantity:
                    # Process the entire ask order
                    cursor.execute('DELETE FROM asks WHERE id = ?', (ask_id,))
                    processed_quantity += ask_quantity
                    total_cost += ask_price * ask_quantity
                else:
                    # Process a portion of the ask order
                    cursor.execute('UPDATE asks SET quantity = ? WHERE id = ?', (ask_quantity - remaining_quantity, ask_id))
                    processed_quantity += remaining_quantity
                    total_cost += ask_price * remaining_quantity

                # Track the total amount paid to each seller
                sellers[seller_id] = sellers.get(seller_id, 0) + (ask_price * ask_quantity)

                cursor.execute('SELECT balance FROM user WHERE id = ?', (user_id,))
                user_balance_row = cursor.fetchone()

                if user_balance_row:
                    user_balance = user_balance_row[0]  # Extract the balance from the tuple
                    users_balance = user_balance - (ask_price*processed_quantity)*(1 + wk_commission_rate)

                cursor.execute('''
                    INSERT INTO transaction_history
                    (user_id, asset_id, asset_type, transaction_type, price, quantity, balance)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (user_id, asset_id, asset_type, 'purchase', ask_price, processed_quantity, users_balance))
                conn.commit()

                cursor.execute('SELECT balance FROM user WHERE id = ?', (seller_id,))
                seller_balance_row = cursor.fetchone()

                if seller_balance_row:
                    seller_balance = seller_balance_row[0]  # Extract the balance from the tuple
                    sellers_balance = seller_balance + ask_price*processed_quantity

                cursor.execute('''
                    INSERT INTO transaction_history
                    (user_id, asset_id, asset_type, transaction_type, price, quantity, balance)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (seller_id, asset_id, asset_type, 'sale', ask_price, processed_quantity, sellers_balance))

                # Update the price in the corresponding table (assuming it's a different table)
                table_name = asset_type.lower()
                cursor.execute(f'''
                    UPDATE {table_name}
                    SET price = ?
                    WHERE id = ?
                ''', (ask_price, asset_id))

            # Deduct the user's balance and available balance for the processed quantity
            if processed_quantity > 0:
                required_balance = total_cost*(1 + wk_commission_rate)
                print('total cost=', total_cost)
                #deduct_user_balance(user_id, required_balance)

                # Get the current user balance
                cursor.execute('SELECT balance FROM user WHERE id = ?', (user_id,))
                user_balance = cursor.fetchone()

                if user_balance:
                    current_balance = user_balance[0]
                    new_balance = current_balance - required_balance

                    # Update the user's balance in the database
                    cursor.execute('UPDATE user SET balance = ? WHERE id = ?', (new_balance, user_id))

                    conn.commit()

                elif user_balance is None:
                    conn.close()
                    return None  # User not found

                #deduct_user_available_balance(user_id, required_balance)
                # Get the current user available balance
                cursor.execute('SELECT available_balance FROM user WHERE id = ?', (user_id,))
                user_available_balance = cursor.fetchone()

                if user_available_balance:
                    current_balance = user_available_balance[0]
                    new_balance = current_balance - required_balance

                    # Update the user's balance in the database
                    cursor.execute('UPDATE user SET available_balance = ? WHERE id = ?', (new_balance, user_id))

                    conn.commit()

                elif user_available_balance is None:
                    return None  # User not found

                # Add money to the balances of the sellers
                for seller_id, amount_paid in sellers.items():
                    cursor.execute('SELECT balance, available_balance FROM user WHERE id = ?', (seller_id,))
                    seller_balances = cursor.fetchone()

                    if seller_balances:
                        current_balance = seller_balances[0]
                        current_available_balance = seller_balances[1]

                        new_balance = current_balance + total_cost
                        print('amount paid=', amount_paid)
                        new_available_balance = current_available_balance + total_cost

                        # Update the seller's balance in the database
                        cursor.execute('UPDATE user SET balance = ?, available_balance = ? WHERE id = ?', (new_balance, new_available_balance, seller_id))

            # Update the user's portfolio
            if processed_quantity > 0:
                #add_to_portfolio(user_id, asset_id, asset_type, processed_quantity)
                # Check if the user already has this asset in their portfolio
                cursor.execute('''
                    SELECT quantity FROM portfolio
                    WHERE user_id = ? AND asset_id = ? AND asset_type = ?
                ''', (user_id, asset_id, asset_type))
                existing_asset_row = cursor.fetchone()

                if existing_asset_row is not None:
                    existing_asset = int(existing_asset_row[0])
                    # Update the quantity if the asset is already in the portfolio
                    new_quantity = existing_asset + quantity
                    cursor.execute('''
                        UPDATE portfolio
                        SET quantity = ?
                        WHERE user_id = ? AND asset_id = ? AND asset_type = ?
                    ''', (new_quantity, user_id, asset_id, asset_type))
                else:
                    # Insert a new record if the asset is not in the portfolio
                    cursor.execute('''
                        INSERT INTO portfolio (user_id, asset_id, asset_type, quantity)
                        VALUES (?, ?, ?, ?)
                    ''', (user_id, asset_id, asset_type, quantity))

                conn.commit()

            return {"success": "Bid order processed successfully"}

    except Exception as error:
        logging.error("Error in process_bid_order: %s", error)
        if conn:
            conn.rollback()

    finally:
        if conn:
            conn.close()

def process_ask_order(user_id, asset_id, asset_type, quantity, wk_commission_rate):
    conn = None

    try:
        with connect_db() as conn:
            cursor = conn.cursor()
            # Initialize variables to track processed quantity and total cost
            processed_quantity = 0
            total_cost = 0
            buyers = {}
            buyers_balance = []
            users_balance = []

            while processed_quantity < quantity:
                # Query the cheapest available bid order
                cursor.execute('''
                    SELECT id, price, quantity, user_id FROM bids
                    WHERE asset_id = ? AND asset_type = ?
                    ORDER BY price DESC, created_at ASC
                    LIMIT 1
                ''', (asset_id, asset_type))
                bid_order = cursor.fetchone()

                if bid_order is None:
                    break  # No more bids available to fulfill the quantity

                bid_id, bid_price, bid_quantity, buyer_id = bid_order

                # Calculate the remaining quantity to be processed
                remaining_quantity = quantity - processed_quantity

                if bid_quantity <= remaining_quantity:
                    # Process the entire bid order
                    cursor.execute('DELETE FROM bids WHERE id = ?', (bid_id,))
                    processed_quantity += bid_quantity
                    new_purchased_quantity = bid_quantity
                    total_cost += bid_price * bid_quantity
                else:
                    # Process a portion of the bid order
                    cursor.execute('UPDATE bids SET quantity = ? WHERE id = ?', (bid_quantity - remaining_quantity, bid_id))
                    processed_quantity += remaining_quantity
                    new_purchased_quantity = remaining_quantity
                    total_cost += bid_price * remaining_quantity

                # Track the processed quantity for each buyer
                buyers[buyer_id] = new_purchased_quantity

                cursor.execute('SELECT balance FROM user WHERE id = ?', (user_id,))
                user_balance_row = cursor.fetchone()

                if user_balance_row:
                    user_balance = user_balance_row[0]  # Extract the balance from the tuple
                    users_balance = user_balance + bid_price*new_purchased_quantity

                cursor.execute('''
                    INSERT INTO transaction_history
                    (user_id, asset_id, asset_type, transaction_type, price, quantity, balance)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (user_id, asset_id, asset_type, 'sale', bid_price, new_purchased_quantity, users_balance))
                conn.commit()

                cursor.execute('SELECT balance FROM user WHERE id = ?', (buyer_id,))
                buyer_balance_row = cursor.fetchone()

                if buyer_balance_row:
                    buyer_balance = buyer_balance_row[0]  # Extract the balance from the tuple
                    buyers_balance = buyer_balance - (bid_price*new_purchased_quantity)*(1 + wk_commission_rate)

                cursor.execute('''
                    INSERT INTO transaction_history
                    (user_id, asset_id, asset_type, transaction_type, price, quantity, balance)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (buyer_id, asset_id, asset_type, 'purchase', bid_price, new_purchased_quantity, buyers_balance))
                conn.commit()

                # Update the price in the corresponding table (assuming it's a different table)
                table_name = asset_type.lower()
                cursor.execute(f'''
                    UPDATE {table_name}
                    SET price = ?
                    WHERE id = ?
                ''', (bid_price, asset_id))

                if buyer_balance_row:
                    buyer_balance = buyer_balance_row[0]  # Extract the balance from the tuple
                    buyers_balance = buyer_balance - (bid_price*new_purchased_quantity)*(1 + wk_commission_rate)

                cursor.execute('''
                    UPDATE user
                    SET balance = ?
                    WHERE id = ?
                ''', (buyers_balance, buyer_id))

                # Update the buyer's portfolio
                for buyer_id, purchased_shares in buyers.items():
                    # Check if the buyer already owns the same asset
                    print('buyers:', buyers)
                    cursor.execute('''
                        SELECT quantity FROM portfolio
                        WHERE user_id = ? AND asset_id = ? AND asset_type = ?
                    ''', (buyer_id, asset_id, asset_type))
                    existing_asset_row = cursor.fetchone()

                    if existing_asset_row is not None:
                        existing_asset = int(existing_asset_row[0])
                        # Update the quantity if the asset is already in the portfolio
                        new_quantity = existing_asset + purchased_shares
                        print('buyer_id:', buyer_id, ', purchased_shares:', purchased_shares, ', existing_asset: ', existing_asset, ', new_quantity:', new_quantity)
                        cursor.execute('''
                            UPDATE portfolio
                            SET quantity = ?
                            WHERE user_id = ? AND asset_id = ? AND asset_type = ?
                        ''', (new_quantity, buyer_id, asset_id, asset_type))
                    else:
                        # Insert a new record if the asset is not in the buyer's portfolio
                        cursor.execute('''
                            INSERT INTO portfolio (user_id, asset_id, asset_type, quantity)
                            VALUES (?, ?, ?, ?)
                        ''', (buyer_id, asset_id, asset_type, purchased_shares))

                    conn.commit()

            #Update the user's portfolio
            if processed_quantity > 0:
                #deduct_from_portfolio(user_id, asset_id, asset_type, processed_quantity)
                # Check if the user has enough assets to deduct
                cursor.execute('''
                    SELECT quantity FROM portfolio
                    WHERE user_id = ? AND asset_id = ? AND asset_type = ?
                ''', (user_id, asset_id, asset_type))
                existing_asset_row = cursor.fetchone()
                existing_asset = int(existing_asset_row[0])
                print('existing_asset: ', existing_asset, 'quantity:', processed_quantity)
                if existing_asset:
                    if existing_asset > processed_quantity:
                        new_quantity = existing_asset - quantity
                        cursor.execute('''
                            UPDATE portfolio
                            SET quantity = ?
                            WHERE user_id = ? AND asset_id = ? AND asset_type = ?
                        ''', (new_quantity, user_id, asset_id, asset_type))
                    elif existing_asset == processed_quantity:
                        cursor.execute('''
                            DELETE FROM portfolio
                            WHERE user_id = ? AND asset_id = ? AND asset_type = ?
                        ''', (user_id, asset_id, asset_type))
                    else:
                        print('Error, unexpected outcome, negative quantity of asset in portfolio of user ?', user_id)
                else:
                    # Handle the case where the user doesn't have the specified asset
                    print(f'Error: User {user_id} does not have the asset')

                conn.commit()

            # Deduct the user's balance and available balance for the processed quantity
            if processed_quantity > 0:
                required_balance = total_cost
                #replenish_user_available_balance(user_id, required_balance)
                # Get the current user balance
                cursor.execute('SELECT available_balance FROM user WHERE id = ?', (user_id,))
                user_balance = cursor.fetchone()

                if user_balance:
                    current_balance = user_balance[0]
                    new_balance = current_balance + required_balance

                    # Update the user's balance in the database
                    cursor.execute('UPDATE user SET available_balance = ? WHERE id = ?', (new_balance, user_id))
                    conn.commit()
                elif user_balance is None:
                    conn.rollback()
                    return None  # User not found

                #replenish_user_balance(user_id, required_balance)
                # Get the current user balance
                cursor.execute('SELECT balance FROM user WHERE id = ?', (user_id,))
                user_balance = cursor.fetchone()

                if user_balance:
                    current_balance = user_balance[0]
                    new_balance = current_balance + required_balance

                    # Update the user's balance in the database
                    cursor.execute('UPDATE user SET balance = ? WHERE id = ?', (new_balance, user_id))
                    conn.commit()
                else:
                    conn.rollback()
                    return None  # User not found

            conn.commit()

            return {"success": "Ask order processed successfully"}

    except Exception as error:
        logging.error("Error in process_ask_order: %s", error)
        traceback.print_exc()
        if conn:
            conn.rollback()

    finally:
        if conn:
            conn.close()

def get_number_of_bids_or_asks(asset_id, asset_type, order_type):
    conn = connect_db()
    cursor = conn.cursor()

    try:
        # Determine the table name based on the order_type ('bid' or 'ask')
        table_name = 'bids' if order_type == 'bid' else 'asks'

        # Query the count of bids or asks for the specified asset
        cursor.execute(f'''
            SELECT quantity FROM {table_name}
            WHERE asset_id = ? AND asset_type = ?
        ''', (asset_id, asset_type))

        conn.commit()

        # Fetch the quantity data
        quantity_data = cursor.fetchall()

        # Sum up the quantities
        count = sum(quantity for quantity, in quantity_data)

        if count:
            return count
        else:
            return 0

    except Exception as error:
        conn.rollback()
        # Handle exceptions here, e.g., log the error
        print("get_number_of_bids_or_asks Error:", error)

    finally:
        conn.close()

def get_user_shares(user_id, asset_id, asset_type):
    conn = connect_db()
    cursor = conn.cursor()

    try:
        # Query the count of bids or asks for the specified asset
        cursor.execute('''
            SELECT quantity FROM portfolio
            WHERE user_id = ? AND asset_id = ? AND asset_type = ?
        ''', (user_id, asset_id, asset_type))

        result = cursor.fetchone()

        if result is not None:
            count = result[0]
        else:
            count = 0

        return count

    except Exception as error:
        conn.rollback()
        # Handle exceptions here, e.g., log the error
        print("get_user_shares Error:", error)

    finally:
        conn.close()

def replenish_difference_balance(id, user_id, transaction_price, transaction_quantity): #interesting
    conn = None

    try:
        with connect_db() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                        SELECT price, quantity FROM bids
                        WHERE id = ?
                        ORDER BY price ASC, created_at DESC
                        LIMIT 1
                    """, (id,))
            bids_data = cursor.fetchone()

            amount = bids_data[0] * bids_data[1]
            new_amount = transaction_price*transaction_quantity

            replenish_user_available_balance(user_id, amount)
            deduct_user_available_balance(user_id, new_amount)

    except Exception as error:
        logging.error("Error in replenish_difference_balance: %s", error)
        if conn:
            conn.rollback()

    finally:
        if conn:
            conn.close()

def get_price_history(asset_id, asset_type, timeframe):
    conn = None

    try:
        with connect_db() as conn:
            cursor = conn.cursor()

            if timeframe == '1day':
                # Fetch price history for the last day
                cursor.execute("""SELECT timestamp, price
                               FROM transaction_history 
                               WHERE transaction_type = "purchase" AND asset_id = ? AND asset_type = ? 
                               AND timestamp >= datetime('now', '-1 day')
                               ORDER BY timestamp DESC""", (asset_id, asset_type))

            elif timeframe == "1week":
                # Fetch price history for the last week
                cursor.execute("""SELECT timestamp, price
                               FROM transaction_history 
                               WHERE transaction_type = "purchase" AND asset_id = ? AND asset_type = ? 
                               AND timestamp >= datetime('now', '-7 day')
                               ORDER BY timestamp DESC""", (asset_id, asset_type))

            elif timeframe == "1month":
                # Fetch price history for the last month
                cursor.execute("""SELECT timestamp, price
                               FROM transaction_history 
                               WHERE transaction_type = "purchase" AND asset_id = ? AND asset_type = ? 
                               AND timestamp >= datetime('now', '-1 month')
                               ORDER BY timestamp DESC""", (asset_id, asset_type))

            elif timeframe == "1year":
                # Fetch price history for the last year
                cursor.execute("""SELECT timestamp, price
                               FROM transaction_history 
                               WHERE transaction_type = "purchase" AND asset_id = ? AND asset_type = ? 
                               AND timestamp >= datetime('now', '-1 year')
                               ORDER BY timestamp DESC""", (asset_id, asset_type))

            elif timeframe == "max":
                # Fetch all price history
                cursor.execute("""SELECT timestamp, price
                               FROM transaction_history 
                               WHERE transaction_type = "purchase" AND asset_id = ? AND asset_type = ? 
                               ORDER BY timestamp DESC""", (asset_id, asset_type))

            # Execute a SQL query to fetch your data (replace with your actual query)
            # cursor.execute("""SELECT timestamp, price
            #                FROM transaction_history
            #                WHERE transaction_type = "purchase" AND asset_id =? AND asset_type = ?
            #                ORDER BY timestamp DESC
            #                LIMIT 10
            #                """, (asset_id, asset_type,))

            # Fetch all the rows as a list of tuples
            data = cursor.fetchall()

            # Convert the data to a list of dictionaries for JSON serialization
            data_list = [{'timestamp': row[0], 'price': row[1]} for row in data]

            return data_list

    except Exception as error:
        logging.error("Error in get_price_history: %s", error)
        traceback.print_exc()
        if conn:
            conn.rollback()

    finally:
        if conn:
            conn.close()

def cancel_ask(ask_id):
    conn = None

    try:
        with connect_db() as conn:
            cursor = conn.cursor()

        # Fetch the bid or ask to be canceled
        cursor.execute("""SELECT * FROM asks WHERE id = ?""", (ask_id,))
        ask = cursor.fetchone()

        if ask:
            # Remove the bid or ask from the asks table
            cursor.execute("DELETE FROM asks WHERE id=?", (ask_id,))

            # Check if the asset is already in the portfolio
            cursor.execute("SELECT id, quantity FROM portfolio WHERE user_id=? AND asset_id=? AND asset_type=?",
                           (ask[1], ask[2], ask[3]))
            existing_asset = cursor.fetchone()

            if existing_asset:
                # Update the quantity in the portfolio
                new_quantity = existing_asset[1] + ask[5]
                cursor.execute("UPDATE portfolio SET quantity=? WHERE id=?", (new_quantity, existing_asset[0]))
            else:
                # Add it to the portfolio
                cursor.execute("INSERT INTO portfolio (user_id, asset_id, asset_type, quantity) VALUES (?, ?, ?, ?)",
                            (ask[1], ask[2], ask[3], ask[5]))

            # Commit the changes to the database
            conn.commit()
            return True  # Cancellation successful
        else:
            return False  # Bid/ask not found

    except Exception as error:
        logging.error("Error in cancel_ask: %s", error)
        traceback.print_exc()
        if conn:
            conn.rollback()

    finally:
        if conn:
            conn.close()

def cancel_bid(bid_id):
    conn = None

    try:
        with connect_db() as conn:
            cursor = conn.cursor()

            # Fetch the bid to be canceled
            cursor.execute("SELECT id, price, quantity FROM bids WHERE id=?", (bid_id,))
            bid = cursor.fetchone()

            if bid:
                # Remove the bid from the bids table
                cursor.execute("DELETE FROM bids WHERE id=?", (bid_id,))

                # Commit the changes to the database
                conn.commit()
                return True  # Cancellation successful
                print('returned True')
            else:
                print('returned False')
                return False  # Bid not found

    except Exception as error:
        logging.error("Error in cancel_bid: %s", error)
        if conn:
            conn.rollback()

    finally:
        if conn:
            conn.close()

def get_balance(user_id):
    conn = None

    try:
        with connect_db() as conn:
            cursor = conn.cursor()

        # Execute a SQL query to retrieve the user's balance
        cursor.execute("SELECT balance FROM user WHERE id = ?", (user_id,))
        result = cursor.fetchone()

        if result:
            # Return the balance as a float
            return float(result[0])
        else:
            # If the user doesn't exist, return None or raise an exception
            return None
    
    except Exception as error:
        logging.error("Error in get_balance: %s", error)
        if conn:
            conn.rollback()

    finally:
        if conn:
            conn.close()

def get_balance_history(user_id):
    conn = None

    try:
        with connect_db() as conn:
            cursor = conn.cursor()

            one_month_ago = datetime.now() - timedelta(days=6)

            one_month_ago_str = one_month_ago.strftime("%Y-%m-%d")

            # Fetch all price history
            cursor.execute("""SELECT timestamp, ROUND(balance, 2) as balance
                            FROM transaction_history 
                            WHERE user_id = ?
                            AND timestamp >= ?
                            ORDER BY timestamp DESC""", (user_id, one_month_ago_str))

            data = cursor.fetchall()

            # Convert the data to a list of dictionaries for JSON serialization
            data_list = [{'timestamp': row[0], 'price': row[1]} for row in data]

            return data_list

    except Exception as error:
        logging.error("Error in get_balance: %s", error)
        if conn:
            conn.rollback()

    finally:
        if conn:
            conn.close()

def get_bid_info(bid_id):
    conn = None

    try:
        with connect_db() as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT user_id, price, quantity FROM bids WHERE id = ?", (bid_id,))
            result = cursor.fetchone()
            if result:
                column_names = ["user_id", "price", "quantity"]
                return dict(zip(column_names, result))
            return None

    except Exception as error:
        logging.error("Error in get_balance: %s", error)
        if conn:
            conn.rollback()

    finally:
        if conn:
            conn.close()
