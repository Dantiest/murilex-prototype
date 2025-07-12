/* CHANGE COLOR */
var transactionType = 'buy';
var visible = 'price/share';
const orderType = document.querySelectorAll(".buy-sell");
const chartContainer = document.getElementById('chart-container');

var sharesInput = document.getElementById('limit-shares-amount');
var priceInput = document.getElementById('limit-price-amount');
var sharesOwned = parseFloat(document.getElementById('shares-owned').getAttribute('data-value'));

let maxShares = parseFloat(sharesInput.getAttribute('data-ask-count'));
let totalShares = 4000;

orderType.forEach(type => {
    type.addEventListener('click', () => {
        orderType.forEach(order => {
            order.style.backgroundColor = 'black';
        });
        type.style.backgroundColor = '#7216f4';
        buySell = type.getAttribute('data-value');

        transactionType = buySell;

        if (transactionType == 'buy') {
            if (visible == 'price/share') {
                maxShares = parseFloat(sharesInput.getAttribute('data-ask-count'));
                sharesInput.setAttribute('max', maxShares);
                sharesInput.setAttribute('placeholder', `Max. ${maxShares}`);
            }
            else {
                sharesInput.setAttribute('max', totalShares);
                sharesInput.setAttribute('placeholder', '');
                maxShares = totalShares;
            }
            document.getElementById('shares-owned').style.display = 'none';

        } 
        else {
            if (visible == 'price/share'){
                if (sharesOwned > parseFloat(sharesInput.getAttribute('data-bid-count'))){
                    sharesInput.setAttribute('max', parseFloat(sharesInput.getAttribute('data-bid-count')));
                    sharesInput.setAttribute('placeholder', `Max. ${parseFloat(sharesInput.getAttribute('data-bid-count'))}`);
                    maxShares = parseFloat(sharesInput.getAttribute('data-bid-count'));
                }
                else {
                    sharesInput.setAttribute('max', sharesOwned);
                    sharesInput.setAttribute('placeholder', `Max. ${sharesOwned}`);
                    maxShares = sharesOwned;
                }
            }
            else {
                sharesInput.setAttribute('max', totalShares);
                sharesInput.setAttribute('placeholder', '');
            }
            document.getElementById('shares-owned').style.display = 'flex';
        }
    });
});


/*   ORDER TYPE    */

const bestPrice = document.querySelector("#best-price");
const limitOrder = document.querySelector("#limit-order");
const dropBtn = document.querySelector(".dropbtn");
const limitPrice = document.querySelector("#limit-price");
const avgPrice = document.querySelector("#avg-price");
const dropDownContent = document.querySelector(".dropdown-content");

bestPrice.addEventListener('click', (event) => {
    const selectedValue = event.target.getAttribute('data-value');
    dropBtn.innerHTML = `${selectedValue}`;

    visible = 'price/share';

    limitPrice.style.display = 'none';
    avgPrice.style.display = 'flex';
    
    if (transactionType == 'buy') {
        maxShares = parseFloat(sharesInput.getAttribute('data-ask-count'));
        sharesInput.setAttribute('max', maxShares);
        sharesInput.setAttribute('placeholder', `Max. ${maxShares}`);
    }
    else {
        if (sharesOwned > parseFloat(sharesInput.getAttribute('data-bid-count'))){
            sharesInput.setAttribute('max', parseFloat(sharesInput.getAttribute('data-bid-count')));
            sharesInput.setAttribute('placeholder', `Max. ${parseFloat(sharesInput.getAttribute('data-bid-count'))}`);
            maxShares = parseFloat(sharesInput.getAttribute('data-bid-count'));
        }
        else {
            sharesInput.setAttribute('max', sharesOwned);
            sharesInput.setAttribute('placeholder', `Max. ${sharesOwned}`);
            maxShares = sharesOwned;
        }
    }



    //dropDownContent.style.display = 'none';
    updatePrice();
    updateTotal();
});

limitOrder.addEventListener('click', (event) => {
    const selectedValue = event.target.getAttribute('data-value');
    dropBtn.innerHTML = `${selectedValue}`;

    visible = 'limit-price';

    limitPrice.style.display = 'flex';
    avgPrice.style.display = 'none';


    sharesInput.setAttribute('max', totalShares);
    sharesInput.setAttribute('placeholder', '0');
    maxShares = -1;


    //dropDownContent.style.display = 'none';
    updateTotal();
});

/* ORDER BOOK VS. TRADE HISTORY */

const orderBtn = document.querySelector(".order-button");
const tradeBtn = document.querySelector(".trade-button");
const orderBookContainers = document.querySelectorAll(".order-book");
const tradeHistoryContainers = document.querySelectorAll(".trade-history");

orderBtn.addEventListener('click', () => {
    orderBtn.style.borderBottom = '2px solid #7216f4';
    tradeBtn.style.borderBottom = 'none';
    orderBookContainers.forEach(container => {
        container.style.display = 'flex';
    });
    tradeHistoryContainers.forEach(container => {
        container.style.display = 'none';
    });
});

tradeBtn.addEventListener('click', () => {
    tradeBtn.style.borderBottom = '2px solid #7216f4';
    orderBtn.style.borderBottom = 'none';
    orderBookContainers.forEach(container => {
        container.style.display = 'none';
    });
    tradeHistoryContainers.forEach(container => {
        container.style.display = 'flex';
    });
});

/* ADD/RMV TO/FROM WATCHLIST BUTTONS */

const all_add = document.querySelectorAll(".add");
const all_rmv = document.querySelectorAll(".rmv");

const all_add_secondary = document.querySelectorAll(".add_secondary");
const all_rmv_secondary = document.querySelectorAll(".rmv_secondary");

let total = 0;

all_add.forEach((add, index) => {
    add.addEventListener('click', function(event) {
        event.preventDefault();
        add.style.display = "none";
        all_rmv_secondary[index].style.display = "block";
        total++;
        updatePulseAnimation();
    });
});

all_rmv_secondary.forEach((rmv, index) => {
    rmv.addEventListener('click', function(event) {
        event.preventDefault();
        rmv.style.display = "none";
        all_add[index].style.display = "block";
        total--;
        updatePulseAnimation();
    });
});

all_rmv.forEach((link, index) => {
    link.addEventListener('click', function(event) {
        event.preventDefault();
        link.style.display = "none";
        all_add_secondary[index].style.display = "block";
        total--;
        updatePulseAnimation();
    });
});

all_add_secondary.forEach((link, index) => {
    link.addEventListener('click', function(event) {
        event.preventDefault();
        link.style.display = "none";
        all_rmv[index].style.display = "block";
        total++;
        updatePulseAnimation();
    });
});


//PULSE ANIMATION

function updatePulseAnimation() {
    if (total > 0) {
        pulseAnimation();
    } else {
        pulseAnimationOff();
    }
}

function pulseAnimation() {
    const pulseObject = document.querySelector(".pulse-object");
    pulseObject.classList.add("pulse-animation");
}

function pulseAnimationOff() {
    const pulseObject = document.querySelector(".pulse-object");
    pulseObject.classList.remove("pulse-animation");
}

//ADDING AND REMOVING FROM WATCHLIST

document.addEventListener("DOMContentLoaded", function() {
    // Add button click event
    document.querySelectorAll(".add, .add_secondary").forEach(function(button) {
        button.addEventListener("click", function(event) {
            event.preventDefault();

            var itemId = this.getAttribute("data-item-id");
            var assetType = this.getAttribute("data-asset-type");
            var action = this.getAttribute("data-action");

            performWatchlistAction(itemId, assetType, action);
        });
    });

    // Remove button click event
    document.querySelectorAll(".rmv, .rmv_secondary").forEach(function(button) {
        button.addEventListener("click", function(event) {
            event.preventDefault();

            var itemId = this.getAttribute("data-item-id");
            var assetType = this.getAttribute("data-asset-type");
            var action = this.getAttribute("data-action");

            performWatchlistAction(itemId, assetType, action);
        });
    });

    // Function to send data to the server
    function performWatchlistAction(itemIdentifier, assetType, action) {
        fetch("/manage_assets", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                item_id: itemIdentifier,
                item_type: assetType,
                action: action
            })
        })
        .then(response => response.json())
        .then(data => {
            console.log(data.message);
            // Handle success or error messages here
        })
        .catch(error => {
            console.error("Error:", error);
            // Handle error cases here
        });
    }
});


//DISPLAY _______________________________________ DISPLAY
/*
const Display = document.querySelector(".display");
const orderReview = document.querySelector(".order-review");
const close = document.querySelector(".close");


Display.addEventListener('click', () => {
    Display.style.display = 'none';
    orderReview.style.display = 'none';
});

close.addEventListener('click', () => {
    Display.style.display = 'none';
    orderReview.style.display = 'none';
});

*/

//UPDATE VALUES

const assetType = document.getElementById('asset_details').getAttribute('data-asset-type');
const assetId = document.getElementById('asset_details').getAttribute('data-value');
const assetAvgPrice = document.getElementById('asset_price');

var bidQuantities = Array.from(document.querySelectorAll('.bid_quantity')).map(element => parseFloat(element.getAttribute('data-value')));
var askQuantities = Array.from(document.querySelectorAll('.ask_quantity')).map(element => parseFloat(element.getAttribute('data-value')));
var bidPrices = Array.from(document.querySelectorAll('.bid_price')).map(element => parseFloat(element.getAttribute('data-value')));
var askPrices = Array.from(document.querySelectorAll('.ask_price')).map(element => parseFloat(element.getAttribute('data-value')));

var sharesTotal = parseFloat(sharesInput.value);
var limitTotal = parseFloat(priceInput.value);

sharesInput.addEventListener('input', () => {
    updatePrice();
    updateTotal();
});
priceInput.addEventListener('input', updateTotal);

const totalAmountElement = document.getElementById('total');

function updatePrice() {
    let sharesTtl = parseFloat(sharesInput.value);
    let sharesQuantity = parseFloat(sharesInput.value);
    let totalCost = 0;

    if (!sharesTtl) {
        console.log("No Shares Input.");
        assetAvgPrice.innerHTML = '';
        totalAmountElement.textContent = '';
        return;
    }

    if (transactionType == 'buy') {

        if (sharesTtl > sumArray(askQuantities)) {
            console.log("Invalid Shares Total.");
            assetAvgPrice.innerHTML = '<txt>Not enough asks</txt>';
            return;
        }

        let i = 0;
        while (sharesQuantity > 0) {
            if (sharesTtl > askQuantities[i]) {
                totalCost += askQuantities[i] * askPrices[i];
                sharesQuantity -= askQuantities[i];
            }
            else {
                totalCost += sharesQuantity * askPrices[i];
                sharesQuantity = 0;
            }
            i++;
        }
        let avgPrice = totalCost / sharesTtl;
        assetAvgPrice.innerHTML = `${avgPrice.toFixed(2)}`;
    } 
    else {
        if (sharesTtl > sumArray(bidQuantities)) {
            console.log("Invalid Shares Total.");
            assetAvgPrice.innerHTML = '<txt>Not enough bids</txt>';
            return;
        }

        let i = 0;
        while (sharesQuantity > 0) {
            if (sharesTtl > bidQuantities[i]) {
                totalCost += bidQuantities[i] * bidPrices[i];
                sharesQuantity -= bidQuantities[i];
            }
            else {
                totalCost += sharesQuantity * bidPrices[i];
                sharesQuantity = 0;
            }
            i++;
        }
        let avgPrice = totalCost / sharesTtl;
        assetAvgPrice.innerHTML = `${avgPrice.toFixed(2)}`;
    }
}

orderType.forEach(type => {
     type.addEventListener('click', () => {
        updatePrice();
        updateTotal();
     });
});

function updateTotal() {
    // Get the numeric values from the input fields
    sharesTotal = parseFloat(sharesInput.value);
    limitTotal = parseFloat(priceInput.value);

    // Validate if the values are positive before proceeding
    if (sharesTotal < 0) {
        // You can display an error message to the user, clear the values, or take other actions
        assetAvgPrice.innerHTML = '';
        totalAmountElement.textContent = '';
        return;
    }
    else if(!sharesTotal) {
        assetAvgPrice.innerHTML = '';
        totalAmountElement.textContent = '';
        return;
    }

    if (visible == 'limit-price'){
        if (limitTotal < 0) {
            // You can display an error message to the user, clear the values, or take other actions
            return;
        }
        if (!limitTotal) {
            totalAmountElement.textContent = '';
            return;
        }
        
        const amount = limitTotal * sharesTotal;

        // Update the displayed total amount
        totalAmountElement.textContent = amount.toFixed(2);
    }
    else {
        let assetPrice = parseFloat(assetAvgPrice.textContent);


        const amount = assetPrice * sharesTotal;

        // Update the displayed total amount
        totalAmountElement.textContent = amount.toFixed(2);
    }
}

function deleteAssets() {
    for (let i=0; i < sumArray(bidQuantities); i++) {
        for(let k=0; k < sumArray(askQuantities); k++){
            if (bidPrices[i] >= askPrices[y]) {
                if(askQuantities[y] > bidQuantities[i]) {
                    //bid.delete and ask.delete
                }
                else if (askQuantities[y] < bidQuantities[i]){
                    //ask.delete and bid -= ...
                }
                else {
                    //ask.delete and bid.delete
                }
            }
        }
    }
}

function sumArray(arr) {
    return arr.reduce((acc, val) => acc + val, 0);
}

function redirectToNextPage() {
    if (sharesTotal) {
        if (sharesTotal < 0) {
            console.log('Negative Total Shares.');
            sharesInput.style.border = '1px solid red';
            return;
        }
        if (visible == 'limit-price') {
            if (limitTotal) {
                if (limitTotal < 0) {
                    console.log('Limit price is negative.');
                    priceInput.style.border = '1px solid red';
                    return;
                }
                else {
                    var url = '/review_order?asset-id=' + encodeURIComponent(assetId) + '&asset-type=' + encodeURIComponent(assetType) + '&quantity=' + encodeURIComponent(sharesTotal) + '&limit-price=' + encodeURIComponent(limitTotal) + '&transaction-type=' + encodeURIComponent(transactionType) + '&order-type=' + encodeURIComponent(visible);
                    window.location.href = url;
                }
            }
            else {
                console.log('No limit Total');
                priceInput.style.border = '1px solid red';
                return;
            }
        }
        else {
            if (sharesTotal > maxShares) {
                console.log('Shares Past Max.');
                sharesInput.style.border = '1px solid red';
                return;
            }
            else {
                var url = '/review_order?asset-id=' + encodeURIComponent(assetId) + '&asset-type=' + encodeURIComponent(assetType) + '&quantity=' + encodeURIComponent(sharesTotal) + '&transaction-type=' + encodeURIComponent(transactionType) + '&order-type=' + encodeURIComponent(visible) + '&limit-price=none';
                window.location.href = url;
            }
        }
    }
    else {
        console.log('No shares');
        sharesInput.style.border = '1px solid red';
        return;
    }
}

document.getElementById('review-order').addEventListener('click', () => redirectToNextPage());

// Connect to the Socket.IO server
var socket = io();

socket.on('connect', function () {
    console.log('Connected to Socket.io');
});

socket.on('new_bid_or_ask', function(data) {
    // Handle the received bid/ask update data
    console.log('Received new bid/ask update:', data);

    var message = document.getElementById('message');

    message.innerHTML = 'Please refresh page. Information may be outdated.'

    message.classList.add('show');
    setTimeout(() => {message.classList.remove('show'); }, 5000);

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
});

/*const existingOrders = {
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
} */

// Tooltip elements
const xTooltip = document.querySelector('#Xtooltip');
const yTooltip = document.querySelector('#Ytooltip');
const xValue = document.querySelector('#Xvalue');
const yValue = document.querySelector('#Yvalue');

// D3 GRAPHS

function createChart(data) {
    // Set up SVG dimensions
    const width = 800;
    const height = 500;
    const margin = { top: 20, right: 20, bottom: 30, left: 40 };

    const svg = d3.select('#chart-container')
    .append('svg')
    .attr('width', '110%') // Set the width to 100% of the container
    .attr('height', '110%') // Set the height to 100% of the container
    .attr('preserveAspectRatio', 'xMinYMin meet')
    .attr('viewBox', `0 0 ${width} ${height}`);

    // Sort the data by timestamp in ascending order
    data.sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp));

    // Extract timestamp and price data
    const dates = data.map(d => new Date(d.timestamp)); // Parse timestamps into Date objects
    const prices = data.map(d => d.price);

    // Create scales for x and y axes
    const x = d3.scaleTime()
        .domain([d3.min(dates), d3.max(dates)]) // Assuming 'dates' is an array of Date objects
        .range([margin.left, width - margin.right]);

    const yMax = d3.max(prices);
    const yBuffer = 0.1 * yMax; // 10% buffer beyond the highest point
    
    const y = d3.scaleLinear()
        .domain([0, yMax + yBuffer]) // Extend the domain
        .nice()
        .range([height - margin.bottom, margin.top]);

    
    // Add an event listener to track mouse movement
    svg.on('mousemove', handleMousemove);

    function handleMousemove(event) {
        const mouseX = d3.pointer(event)[0]; // Get the x-coordinate of the mouse cursor
        const mouseY = d3.pointer(event)[1]; // Get the y-coordinate of the mouse cursor
        const closestDataPoint = findClosestDataPoint(mouseX, mouseY); // Find the closest data point in both dimensions
    
        // Remove any existing vertical lines
        //svg.selectAll('.vertical-line').remove();
    
        // Update the tooltip or highlight the closest data point
        if (closestDataPoint) {
            // Customize your code to display the tooltip or highlight the closest data point
            const date = closestDataPoint.timestamp;
            const price = closestDataPoint.price;
    
            // Update the tooltip content
            xValue.textContent = date;
            yValue.textContent = price;
    
            // Set the position of the tooltips next to the mouse cursor
            xTooltip.style.left = (event.pageX + 10) + 'px'; // Adjust the offset as needed
            xTooltip.style.top = (event.pageY + 10) + 'px'; // Adjust the offset as needed
            yTooltip.style.left = (event.pageX + 10) + 'px'; // Adjust the offset as needed
            yTooltip.style.top = (event.pageY + 30) + 'px'; // Adjust the offset as needed
    
            // Show the tooltips
            xTooltip.style.display = 'block';
            yTooltip.style.display = 'block';
    
            // Update the highlight circle
            highlightCircle
                .attr('cx', x(new Date(date))) // Set x position based on the date of the closest point
                .attr('cy', y(price)) // Set y position based on the price of the closest point
                .style('opacity', 1); // Show the circle
    
            // Define the length of the vertical line
            //const lineLength = height - y(price); // Adjust as needed
    
            // Create and append a vertical line
            svg.append('line')
                //.attr('class', 'vertical-line')
                .attr('x1', x(new Date(date)))
                .attr('y1', y(price))
                .attr('x2', x(new Date(date)))
                .attr('y2', y(price) + lineLength)
                .style('stroke', 'blue') // Set the line color
                .style('stroke-width', '2'); // Set the line width
        } else {
            // If there is no closest data point, hide the highlight circle
            highlightCircle.style('opacity', 0);
    
        }
    }
    

    // Function to find the closest data point horizontally
    function findClosestDataPoint(mouseX, mouseY) {
        let closestPoint = null;
        let closestDistance = Infinity;

        data.forEach(dataPoint => {
            const dataX = x(new Date(dataPoint.timestamp)); // Use your x scale to get the x-coordinate of the data point
            const dataY = y(dataPoint.price);
            const distance = Math.sqrt((dataX - mouseX) ** 2 + (dataY - mouseY) ** 2);

            if (distance < closestDistance) {
                closestDistance = distance;
                closestPoint = dataPoint;
            }
        });

        return closestPoint;
    }
    
    // Create a line generator
    const line = d3.line()
        .x(d => x(new Date(d.timestamp))) // Use x scale with Date objects
        .y(d => y(d.price))
        .curve(d3.curveLinear); // Apply the curve interpolation


    // Append a path element for the line
    svg.append('path')
        .datum(data)
        .attr('class', 'line')
        .attr('d', line);

    // Add x and y axes
    svg.append('g')
        .attr('class', 'x-axis')
        .attr('transform', `translate(0,${height - margin.bottom})`)
        //.call(d3.axisBottom(x).tickValues(getTickValues(dates, 3))); // Specify the number of tick values
        .call(d3.axisBottom(x).tickValues([]))

    svg.append('g')
        .attr('class', 'y-axis')
        .attr('transform', `translate(${margin.left},0)`)
        .call(d3.axisLeft(y));
        
    svg.selectAll('text').style('font-size', '20px'); // Adjust the font-size value

    svg.selectAll('.bar')
    .data(data)
    .enter().append('rect')
    .attr('class', 'bar')


    // Create a circle for highlighting the point on hover
    const highlightCircle = svg.append('circle')
        .attr('class', 'highlight-circle')
        .attr('r', 5) // Set the radius of the circle
        .style('fill', 'red') // Set the fill color
        .style('opacity', 0); // Initially hide the circle
    
    // Add an event listener to the SVG for mouseout RED CIRCLES NOT USED
    svg.on('mouseout', () => {
        console.log(event.target);
        // Hide the highlight circle
        highlightCircle.style('opacity', 0);
        // Hide the tooltips on mouseout
        xTooltip.style.display = 'none';
        yTooltip.style.display = 'none';

        //svg.selectAll('.vertical-line').remove();
    });

    // Create a group for data points (circles or points)
    const dataPoints = svg.selectAll('.data-point')
    .data(data)
    .enter()
    .append('circle')
    .attr('class', 'data-point')
    .attr('cx', (d, i) => x(new Date(d.timestamp)))
    .attr('cy', d => y(d.price))
    .attr('r', 5) // Radius of the data points
    .style('fill', 'white') // Color of the data points
    .style('opacity', 0)
    .style('stroke', '#fff')
    .style('stroke-width', '2');

    dataPoints.on('mouseover', (event, d) => {
        // Show the tooltips
        xTooltip.style.display = 'block';
        yTooltip.style.display = 'block';

        // Hide other data points (circles) and make the selected one fully visible
        dataPoints.style('opacity', 0);
        d3.select(event.currentTarget).style('opacity', 1); // Make the hovered point fully visible

    })
    .on('mouseout', () => {
        // Hide tooltips on mouseout
        if (xTooltip) {
            xTooltip.style.display = 'none';
        }
        if (yTooltip) {
            yTooltip.style.display = 'none';
        }
        dataPoints.style('opacity', 0); // Reset opacity for all points //aici
        d3.select(event.currentTarget).style('opacity', 0); 

    });

}

/* TIMESCALES */

const type = document.querySelector(".row .type");
const timeScales = document.querySelectorAll(".scale");

// Function to create and render the chart
function createAndRenderChart(selectedTimeframe) {
    const chartContainer = document.getElementById('chart-container');

    // Clear the previous chart by removing its content
    chartContainer.innerHTML = '';

    fetch(`/api/data_asset?asset_id=${assetId}&asset_type=${assetType}&timeframe=${selectedTimeframe}`)
        .then(response => response.json())
        .then(data => {
            // Use the fetched data to create your D3.js chart
            createChart(data);
        })
        .catch(error => {
            console.error('Error fetching data:', error);
        });
}

// Set the default timeframe to "max"
const defaultTimeframe = "1week";

// Call the createAndRenderChart function with the default "max" timeframe when the page loads
createAndRenderChart(defaultTimeframe);

timeScales.forEach(scale => {
    scale.addEventListener('click', () => {
        const selectedTimeframe = scale.getAttribute('data-timeframe');
        
        console.log(selectedTimeframe)

        // Clear the previous chart by removing its content
        chartContainer.innerHTML = '';

        fetch(`/api/data_asset?asset_id=${assetId}&asset_type=${assetType}&timeframe=${selectedTimeframe}`)
        .then(response => response.json())
        .then(data => {
            if (data.length === 0) {
                chartContainer.innerHTML = 'No data yet';
            } else {
                createChart(data);
                console.log(data)
            }
        })
        .catch(error => {
            console.error('Error fetching data:', error);
        });

        timeScales.forEach(time => {
            time.style.backgroundColor = 'black';
        });
        const selectedType = scale.getAttribute('data-value');
        type.innerHTML = `${selectedType}`;
        scale.style.backgroundColor = '#7216f4';
    });
});

// Function to get a subset of tick values
//function getTickValues(arr, count) {
//    const step = Math.ceil(arr.length / (count - 1));
//    return arr.filter((value, index) => index % step === 0);
//}
