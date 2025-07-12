// JavaScript code for making bids and asks using SocketIO

// Assuming you have already connected to the SocketIO server
var socket = io();

// Function to submit a bid
function submitBid() {
    var asset_id = parseFloat(document.getElementById('asset_id').value);
    var asset_type = document.getElementById('asset_type').value;
    var price = parseFloat(document.getElementById('bid-price').value);
    var quantity = parseFloat(document.getElementById('bid-quantity').value);
    
    var bidData = {
        user_id: 1,
        asset_id: asset_id,
        asset_type: asset_type,
        type: 'buy',
        price: price,
        quantity: quantity
    };

    socket.emit('submit_order', bidData);
}

// Function to submit an ask
function submitAsk(assetID, assetType, Price,  Quantity) {    
    var askData = {
        user_id: 1,
        asset_id: assetID,
        asset_type: assetType,
        type: 'sell',
        price: Price,
        quantity: Quantity
    };

    socket.emit('submit_order', askData);
}

// Attach form submit listeners
document.getElementById('bid-form').addEventListener('submit', function(event) {
    event.preventDefault();
    submitBid();
});

document.getElementById('ask-form').addEventListener('submit', function(event) {
    event.preventDefault();

    var asset_id = parseFloat(document.getElementById('asset_id2').value);
    var asset_type = document.getElementById('asset_type2').value;
    var price = parseFloat(document.getElementById('ask-price').value);
    var quantity = parseFloat(document.getElementById('ask-quantity').value);

    submitAsk(asset_id, asset_type, price, quantity);
});
