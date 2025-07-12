// Connect to the Socket.IO server
var socket = io();

socket.on('connect', function () {
    console.log('Connected to Socket.io');
});

/* socket.on('new_bid_or_ask', function(data) {
    // Handle the received bid/ask update data
    console.log('Received new bid/ask update:', data);

    // Update the UI with the new bid/ask data
    // Extract relevant data
    var price = data.price;
    var quantity = data.quantity;
    var type = data.type; // 'bid' or 'ask'

    // Create a new list item to represent the bid/ask entry
    var listItem = document.createElement('div');
    listItem.setAttribute('class', 'order-book');
    if (type == 'bid') {
        listItem.innerHTML = `
        <div class="title-division">
            <txt>Size</txt>
            <txt>Bid</txt>
        </div>
        <div class="division">
            <txt id="${type}_quantity_{{ loop.index }}" class="${type}_quantity" data-value="${quantity}">${quantity}</txt>
            <txt id="${type}_price_{{ loop.index }}" class="${type}_price" data-value="${price}">${price}$</txt>
        </div>`;
    }
    else {
        listItem.innerHTML = `
        <div class="title-division">
            <txt>Ask</txt>
            <txt>Size</txt>
        </div>
        <div class="division">
            <txt id="${type}_price_{{ loop.index }}" class="${type}_price" data-value="${price}">${price}$</txt>
            <txt id="${type}_quantity_{{ loop.index }}" class="${type}_quantity" data-value="${quantity}">${quantity}</txt>
        </div>`;
    }


    // Determine the container based on bid or ask type
    var containerId = type === 'bid' ? 'bid-table' : 'ask-table';
    var container = document.getElementById(containerId);

    // Append the new bid/ask entry to the container
    container.appendChild(listItem);

    // Call these functions
    bidQuantities = Array.from(document.querySelectorAll('.bid_quantity')).map(element => parseFloat(element.getAttribute('data-value')));
    askQuantities = Array.from(document.querySelectorAll('.ask_quantity')).map(element => parseFloat(element.getAttribute('data-value')));
    bidPrices = Array.from(document.querySelectorAll('.bid_price')).map(element => parseFloat(element.getAttribute('data-value')));
    askPrices = Array.from(document.querySelectorAll('.ask_price')).map(element => parseFloat(element.getAttribute('data-value')));

    updatePrice();
    updateTotal();
}); */

const existingOrders = {
    bids: [],  // List of existing buy orders (bid orders)
    asks: []   // List of existing sell orders (ask orders)
};

function fetchExistingOrdersFromServer(assetId, assetType) {
    // Make an AJAX request to your server to fetch the existing orders
    // Include asset_id and asset_type as query parameters
    const url = `/fetch-existing-orders?asset_id=${assetId}&asset_type=${assetType}`;

    fetch(url)
        .then(response => response.json())
        .then(data => {
            // Update existingOrders with the received data
            existingOrders.bids = data.bids; // Update bids
            existingOrders.asks = data.asks; // Update asks
        })
        .catch(error => {
            console.error('Error fetching existing orders:', error);
        });
}

// Call the function to fetch existing orders when the page loads
//fetchExistingOrdersFromServer();

console.log('existing order', existingOrders)

socket.on('new_bid_or_ask', function (data) {
    // Handle the received bid/ask update data
    console.log('Received new bid/ask update:', data);

    // Extract relevant data
    var price = data.price;
    var quantity = data.quantity;
    var type = data.type; // 'bid' or 'ask'

    // Determine the container based on bid or ask type
    var containerId = type === 'bid' ? 'bid-table' : 'ask-table';
    var container = document.getElementById(containerId);

    // Find all matching orders and their quantities
    var matchingOrders = findAllMatchingOrders(price, type);

    if (matchingOrders.length > 0) {
        var totalMatchingQuantity = matchingOrders.reduce(function (total, order) {
            return total + order.quantity;
        }, 0);

        // Calculate the remaining quantities
        var newQuantity;
        console.log('newQuantity 0', newQuantity)
        if (type === 'bid') {
            // For a new bid, we subtract the matching ask quantities
            newQuantity = quantity - totalMatchingQuantity;
            type = 'ask';
        } else if (type === 'ask') {
            // For a new ask, we subtract the matching bid quantities
            newQuantity = quantity - totalMatchingQuantity;
            type = 'bid';
        }
        console.log('newQuantity 1', newQuantity);

        // Remove all matching orders from the UI
        for (var i = 0; i < matchingOrders.length; i++) {
            removeOrderFromUI(matchingOrders[i]);
        }

        if (newQuantity > 0) {
            // Add the remaining order to the UI
            var oppositeType = (type === 'bid') ? 'ask' : 'bid';
            console.log('type:', type)
            console.log('container:', container)
            addOrderToUI(container, oppositeType, price, newQuantity);
        } else if (newQuantity < 0) {
            newQuantity = Math.abs(newQuantity);
            console.log('newQuantity 2', newQuantity);
            console.log('type:', type)
            var oppositeContainerId = (type === 'bid') ? 'bid-table' : 'ask-table';
            var oppositeContainer = document.getElementById(oppositeContainerId);
            console.log('container:', container)
            addOrderToUI(oppositeContainer, type, price, newQuantity);
        }
        console.log('newQuantity 3', newQuantity)
    } else {
        // No matching orders found, simply add the new order to the UI
        addOrderToUI(container, type, price, quantity);

        // Add the new order to the existingOrders object
        var newOrder = {
            price: price,
            quantity: quantity,
            type: type,
        };

        existingOrders[type + 's'].push(newOrder);
    }
});

function findAllMatchingOrders(price, type) {
    // Find all existing orders with the same price and type
    var matchingOrders = [];
    var orders = type === 'bid' ? existingOrders.asks : existingOrders.bids;

    for (var i = 0; i < orders.length; i++) {
        var order = orders[i];
        if (order.price === price) {
            matchingOrders.push(order);
        }
    }

    return matchingOrders;
}

function addOrderToUI(container, type, price, quantity) {
    // Create a new list item
    var listItem = document.createElement('div');
    listItem.setAttribute('class', 'order-book');
    
    // Update the list item based on type (bid or ask)
    if (type === 'bid') {
        listItem.innerHTML = `
        <div class="title-division">
            <txt>Size</txt>
            <txt>Bid</txt>
        </div>
        <div class="division">
            <txt class="${type}_quantity" data-value="${quantity}">${quantity}</txt>
            <txt class="${type}_price" data-value="${price}">${price}$</txt>
        </div>`;
    } else {
        listItem.innerHTML = `
        <div class="title-division">
            <txt>Ask</txt>
            <txt>Size</txt>
        </div>
        <div class="division">
            <txt class="${type}_price" data-value="${price}">${price}$</txt>
            <txt class="${type}_quantity" data-value="${quantity}">${quantity}</txt>
        </div>`;
    }

    // Append the new list item to the container
    container.appendChild(listItem);
}

function updateOrderInUI(order, quantity) {
    // Find the existing order based on its price and type
    var elements = document.querySelectorAll(`.${order.type}_price`);
    for (var i = 0; i < elements.length; i++) {
        var element = elements[i];
        var price = parseFloat(element.getAttribute('data-value'));
        if (price === order.price) {
            // Update the quantity and data-value attribute
            element = element.nextElementSibling; // Move to the quantity element
            if (element) { // Check if the element exists
                // Update the quantity and data-value attribute
                element.innerText = quantity;
                element.setAttribute('data-value', quantity);

                // Check if quantity is zero and remove it
                if (quantity === 0) {
                    removeOrderFromUI(order);
                }
            } else {
                // Handle the case where the element is not found
                console.error("Element not found for price: " + price);
            }
            return; // Stop after updating the first matching order
        }
    }
}

function removeOrderFromUI(order, newQuantity) {
    // Find the existing order based on its price and type
    var elements = document.querySelectorAll(`.${order.type}_price`);
    for (var i = 0; i < elements.length; i++) {
        var element = elements[i];
        var price = parseFloat(element.getAttribute('data-value'));
        if (price === order.price) {
            // Remove the parent list item
            var listItem = element.closest('.order-book');
            listItem.remove();

            // If newQuantity is defined and zero, you can remove it from the existingOrders
            if (typeof newQuantity !== 'undefined' && newQuantity === 0) {
                // Remove it from the existingOrders
                var index = existingOrders[order.type + 's'].indexOf(order);
                if (index !== -1) {
                    existingOrders[order.type + 's'].splice(index, 1);
                }
            }
            return; // Stop after removing the first matching order
        }
    }
}