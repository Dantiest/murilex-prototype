from routes.database import (emit_portfolio_update, insert_bid, insert_ask, deduct_from_portfolio,
                      get_bids, get_asks, update_order_book_in_database, insert_transaction, deduct_user_balance,
                      get_user_available_balance, deduct_user_available_balance, get_user_assets, add_to_portfolio,
                      calculate_price_change, process_bid_order, process_ask_order, get_number_of_bids_or_asks,
                      delete_bid, delete_ask, check_bids, check_asks, replenish_user_balance, get_price,
                      query_ask_bid_self_limitorder, query_ask_bid_self_bestpriceorder, replenish_user_available_balance,
                      replenish_difference_balance, get_balance)
from flask_socketio import SocketIO, emit
from flask import jsonify, request

socketio = SocketIO()

timestamp = 'single'
commission_rate = 2
wk_commission_rate = 0.02

@socketio.on('connect')
def handle_connect():
    client_sid = request.sid
    print(f"Client connected with SID: {client_sid}")

def match_orders(asset_id, asset_type):
    try:
        bids = get_bids(asset_id, asset_type)
        if not bids:
            return

        asks = get_asks(asset_id, asset_type)
        if not asks:
            return

        # Create copies of the bids and asks lists
        bids_copy = bids.copy()
        asks_copy = asks.copy()

        for bid in bids_copy:
            for ask in asks_copy:
                if bid['price'] >= ask['price']:
                    # Match found: bid price is greater than or equal to ask price

                    # Calculate transaction price and quantity
                    transaction_price = ask['price']  # Using the ask price
                    transaction_quantity = min(bid['quantity'], ask['quantity'])
                    
                    old_commission = wk_commission_rate*bid['price']
                    new_commission = wk_commission_rate*transaction_price
                    commission_diff = old_commission - new_commission


                    final_transaction_price  = (1 + wk_commission_rate)*transaction_price*transaction_quantity

                    replenish_difference_balance(bid['id'], bid['user_id'], transaction_price, transaction_quantity)
                    deduct_user_balance(bid['user_id'], round(final_transaction_price, 2))

                    #when user submits bid commission rate of that bid price is taken, but
                    #when bid is matched it should take only commission for ask price, which is lower
                    #probably will need to refund difference between commission for bid and ask

                    replenish_user_available_balance(ask['user_id'], transaction_quantity*transaction_price)
                    replenish_user_balance(ask['user_id'], transaction_quantity*transaction_price)
                    print("commission_diff=", commission_diff)
                    replenish_user_available_balance(bid['user_id'], commission_diff*transaction_quantity)

                    bid_balance = get_balance(bid['user_id'])
                    print('bid balance=', bid_balance)
                    ask_balance = get_balance(ask['user_id'])
                    print('ask balance=', ask_balance)

                    # Insert the transaction into the transaction history
                    insert_transaction({
                        'user_id': bid['user_id'],
                        'asset_id': bid['asset_id'],
                        'asset_type': bid['asset_type'],
                        'transaction_type': 'purchase',
                        'price': transaction_price,
                        'quantity': transaction_quantity,
                        'balance' : bid_balance
                    })

                    insert_transaction({
                        'user_id': ask['user_id'],
                        'asset_id': ask['asset_id'],
                        'asset_type': ask['asset_type'],
                        'transaction_type': 'sale',
                        'price': transaction_price,
                        'quantity': transaction_quantity,
                        'balance' : ask_balance
                    })

                    # After a transaction sending most recent prices
                    data = {
                        'asset_id': ask['asset_id'],
                        'asset_type': ask['asset_type'],
                        'price': transaction_price
                    }
                    socketio.emit('asset_price_update', data)

                    price_change = calculate_price_change(ask['asset_id'], ask['asset_type'], timestamp)

                    change_data = {
                        'asset_id': ask['asset_id'],
                        'asset_type': ask['asset_type'],
                        'price_change': price_change
                    }
                    socketio.emit('asset_price_change', change_data)

                    # Update bid and ask quantities
                    bid['quantity'] -= transaction_quantity
                    ask['quantity'] -= transaction_quantity

                    # Remove fully matched orders
                    if bid['quantity'] <= 0:
                        # Remove the bid from the bids list
                        if bid in bids:
                            bids.remove(bid)
                            delete_bid(bid['id'])
                    if ask['quantity'] <= 0:
                        # Remove the ask from the asks list
                        if ask in asks:
                            asks.remove(ask)
                            delete_ask(ask['id'])



                    # Add matched assets to the buyer's portfolio
                    buyer_id = bid['user_id']
                    asset_id = bid['asset_id']
                    asset_type = bid['asset_type']
                    add_to_portfolio(buyer_id, asset_id, asset_type, transaction_quantity)

        # Update the order book in the database
        update_order_book_in_database(bids, asks)

        socketio.emit('order_processed', {'success': True})
    except Exception as error:
        # Handle exceptions here, e.g., log the error
        print("Error in match_orders:", error)
        socketio.emit('order_processed', {'success': False, 'error': 'Error message here'})

@socketio.on('submit_order')
def handle_submit_order(order):
    try:
        user_id = order['user_id']
        quantity = order['quantity']
        asset_id = order['asset_id']
        asset_type = order['asset_type']
        price = order['price']

        if order['type'] == 'BestPriceOrder':

            #user_trading_with_himself = query_ask_bid_self_bestpriceorder(asset_id, asset_type, user_id, order['action'])
            #if user_trading_with_himself:
            #    emit('order_info', {'message': 'User Trading With Himself'}, room=request.sid)
            #    return

            if order['action'] == 'buy':
                if quantity < 0:
                    emit('order_info', {'message': 'Cannot choose negative quantity'}, room=request.sid)
                    return

                ask_count = get_number_of_bids_or_asks(asset_id, asset_type, 'ask')
                if quantity > ask_count:
                    emit('order_info', {'message': 'Cannot buy more shares than available'}, room=request.sid)
                    return

                # Check user's balance

                required_balance = (price * quantity)*(1 + wk_commission_rate)
                user_balance = get_user_available_balance(user_id)

                if user_balance < required_balance:
                    emit('order_info', {'message': 'Insufficient balance'}, room=request.sid)
                    return

                # Call the process_best_price_order function to process the buy order
                process_bid_order(user_id, asset_id, asset_type, quantity, wk_commission_rate)

                # You can emit a response back to the client if needed
                socketio.emit('order_processed', {'success': True})

            elif order['action'] == 'sell':

                if quantity < 0:
                    emit('order_info', {'message': 'Cannot choose negative quantity'}, room=request.sid)
                    return
                user_assets = get_user_assets(user_id, order['asset_id'], order['asset_type'])
                print(user_assets)
                if user_assets < quantity:
                    socketio.emit('order_info', {'message': 'Insufficient assets'}, room=request.sid)
                    return

                bid_count = get_number_of_bids_or_asks(asset_id, asset_type, 'bid')
                if quantity > bid_count:
                    emit('order_info', {'message': 'Cannot buy more shares than available'}, room=request.sid)
                    return
                
                process_ask_order(user_id, asset_id, asset_type, quantity, wk_commission_rate)

                # You can emit a response back to the client if needed
                socketio.emit('order_processed', {'success': True})

            latest_price = get_price(asset_id, asset_type)

            print('price is ', latest_price)

            # After a transaction sending most recent prices
            data = {
                'asset_id': asset_id,
                'asset_type': asset_type,
                'price': latest_price
            }
            socketio.emit('asset_price_update', data)

            price_change = calculate_price_change(asset_id, asset_type, timestamp)

            change_data = {
                'asset_id': asset_id,
                'asset_type': asset_type,
                'price_change': price_change
            }
            socketio.emit('asset_price_change', change_data)

        elif order['type'] == 'LimitOrder':

            #user_trading_with_himself = query_ask_bid_self_limitorder(asset_id, asset_type, user_id, order['action'], price)
            #if user_trading_with_himself:
            #    emit('order_info', {'message': 'User Trading With Himself'}, room=request.sid)
            #    return

            if order['action'] == 'buy':

                print('submit_order, order==buy:', order)

                if quantity < 0:
                    emit('order_info', {'message': 'Cannot choose negative quantity'}, room=request.sid)
                    return

                if price < 0:
                    emit('order_info', {'message': 'Cannot choose negative price'}, room=request.sid)
                    return
                # Check user's balance
                required_balance = (price * quantity)*(1 + wk_commission_rate)
                user_balance = get_user_available_balance(user_id)

                if user_balance < required_balance:
                    emit('order_info', {'message': 'Insufficient balance'}, room=request.sid)
                    return

                # Deduct user's balance
                deduct_user_available_balance(user_id, required_balance)

                insert_bid(order)

                # After inserting a new bid or ask into the database
                data = {
                    'price': price,
                    'quantity': quantity,
                    'type': 'bid'
                }
                socketio.emit('new_bid_or_ask', data)

                # After inserting the buy order, call match_orders to check for matches

                match_orders(asset_id, asset_type)  # Call match_orders to match orders

                # You can emit a response back to the client if needed
                socketio.emit('order_processed', {'success': True})
            elif order['action'] == 'sell':

                # Check if user has enough assets to sell
                if quantity < 0:
                    emit('order_info', {'message': 'Cannot choose negative quantity'}, room=request.sid)
                    return

                user_assets = get_user_assets(user_id, order['asset_id'], order['asset_type'])

                if user_assets < quantity:
                    socketio.emit('order_info', {'message': 'Insufficient assets'}, room=request.sid)
                    return

                deduct_from_portfolio(user_id, asset_id, asset_type, quantity)

                insert_ask(order)

                data = {
                    'price': price,
                    'quantity': quantity,
                    'type': 'ask'
                }
                socketio.emit('new_bid_or_ask', data)

                # After inserting the buy order, call match_orders to check for matches
                match_orders(asset_id, asset_type)  # Call match_orders to match orders

                # You can emit a response back to the client if needed
                socketio.emit('order_processed', {'success': True})

        check_bids()
        check_asks()
        # After updating the order book, emit portfolio update to the user
        emit_portfolio_update(order['user_id'], socketio)
    except Exception as error:
        # Handle exceptions here, e.g., log the error
        print("handle_submit_order Error:", error)
        socketio.emit('order_processed', {'success': False, 'error': 'Error message here'})

@socketio.on('new_bid_or_ask')
def handle_new_bid_or_ask(data):
    # Emit the new bid/ask data to all connected clients
    socketio.emit('update_bids_asks', data)