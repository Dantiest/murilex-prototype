//TRANSACTION TYPE

const transactionType = document.getElementById("transactionType");

//VISIBLE OR NOT

const orderType = document.getElementById('order-type').getAttribute('data-value');
const limitPriceRow = document.getElementById('limit-price-row');
const avgPriceRow = document.getElementById('avg-price-row');

if (transactionType.getAttribute('data-value') == 'buy') {
    var comission = parseFloat(document.getElementById('commission').getAttribute('data-value'));
}


if (orderType == 'price/share') {
    limitPriceRow.style.display = 'none';
}
else {
    avgPriceRow.style.display = 'none';
}

// UPDATE VALUES _____________________________________ UPDATE VALUES //

const sharesInput = parseFloat(document.getElementById('shares-input').textContent);
const limitInput = parseFloat(document.getElementById('limit-price').textContent);
const assetPriceInput = parseFloat(document.getElementById('asset-price').textContent);

if (orderType == 'limit-price') {
    if (transactionType.getAttribute('data-value') == 'buy') { // Fixed variable name here
        const total = sharesInput * limitInput * (1 + 0.01*comission);
        document.getElementById('total').innerHTML = total;
    }
    else if (transactionType.getAttribute('data-value') == 'sell') { // Fixed variable name here
        const total = sharesInput * limitInput;
        document.getElementById('total').innerHTML = total;
    }
}
else {
    if (transactionType.getAttribute('data-value') == 'buy') { // Fixed variable name here
        const total = sharesInput * assetPriceInput * (1 + 0.01*comission);
        document.getElementById('total').innerHTML = total;
    } 
    else if (transactionType.getAttribute('data-value') == 'sell') { // Fixed variable name here
        const total = sharesInput * assetPriceInput;
        document.getElementById('total').innerHTML = total;
    }
}

/* DETAILS ___________________________________________  DETAILS */

const screen = document.querySelector('.screen');
const information = document.querySelector('.information');
const close = document.querySelector('.close');

document.querySelector('#see-details').addEventListener('click', () => {
    screen.style.display = 'block';
    information.style.display = 'flex';
});


close.addEventListener('click', () => {
    screen.style.display = 'none';
    information.style.display = 'none';
});

screen.addEventListener('click', () => {
    screen.style.display = 'none';
    information.style.display = 'none';
});

//PROCESS PAYMENT ________________________________________ 

var socket = io();

socket.on('connect', function () {
    console.log('Connected to Socket.io');
});

const confirmOrder = document.querySelector("#confirm-order");
//const resume = document.getElementById('resume');

confirmOrder.addEventListener('click', () => {
    var userId = document.getElementById('asset_details').getAttribute('data-user-id');
    var asset_id = document.getElementById('asset_details').getAttribute('data-asset-id');
    var asset_type = document.getElementById('asset_details').getAttribute('data-asset-type'); // Corrected attribute access


    if (orderType == 'limit-price') {
        if (transactionType.getAttribute('data-value') == 'buy') { // Fixed variable name here
            //resume.innerHTML = `user_id: ${userId}, asset_id: ${asset_id}, asset_type: ${asset_type}, price: ${limitInput}, quantity: ${sharesInput}, type: 'buy'`;
            submitBid(userId, asset_id, asset_type, 'LimitOrder', limitInput, sharesInput);
        } 
        else if (transactionType.getAttribute('data-value') == 'sell') { // Fixed variable name here
            //resume.innerHTML = `user_id: ${userId}, asset_id: ${asset_id}, asset_type: ${asset_type}, price: ${limitInput}, quantity: ${sharesInput}, type: 'sell'`;
            submitAsk(userId, asset_id, asset_type, 'LimitOrder', limitInput, sharesInput);
        }
    }

    else if (orderType == 'price/share') {

        if (transactionType.getAttribute('data-value') == 'buy') { // Fixed variable name here
            //resume.innerHTML = `user_id: ${userId}, asset_id: ${asset_id}, asset_type: ${asset_type}, price: ${assetPriceInput}, quantity: ${sharesInput}, type: 'buy'`;
            submitBid(userId, asset_id, asset_type, 'BestPriceOrder', assetPriceInput, sharesInput);
        } else if (transactionType.getAttribute('data-value') == 'sell') { // Fixed variable name here
            //resume.innerHTML = `user_id: ${userId}, asset_id: ${asset_id}, asset_type: ${asset_type}, price: ${assetPriceInput}, quantity: ${sharesInput}, type: 'sell'`;
            submitAsk(userId, asset_id, asset_type, 'BestPriceOrder', assetPriceInput, sharesInput);
        }
    }
    else {
        //resume.innerHTML = 'error_whole';
    }
});



// Function to submit an bid
function submitBid(userID, assetID, assetType, order_type, Price,  Quantity) {    
    var askData = {
        user_id: parseFloat(userID),
        asset_id: parseFloat(assetID),
        asset_type: assetType,
        action: 'buy',
        type: order_type,
        price: parseFloat(Price),
        quantity: parseFloat(Quantity)
    };

    console.log('Button bid pressed');
    socket.emit('submit_order', askData);
    /*
    // Update confirmOrder.innerHTML with loading message and circulating dots
    var loadingInterval = setInterval(function () {
        var currentMessage = confirmOrder.innerHTML;
        var dots = currentMessage.match(/\./g);
        var numDots = (dots && dots.length) || 0;
        var loadingMessage = 'Checking for errors';

        if (numDots < 3) {
            confirmOrder.innerHTML = loadingMessage + '.'.repeat(numDots + 1);
        } else {
            confirmOrder.innerHTML = loadingMessage;
        }
    }, 500); // Update every 500 milliseconds
    */
    // Listen for a response from the server
    socket.on('order_processed', function (response) {
        //clearInterval(loadingInterval); // Stop the loading animation
        if (response.success) {
            // If the order was processed successfully, redirect to the portfolio page
            window.location.href = '/portfolio'; // Replace with the actual URL of your portfolio page
        } else {
            // Handle the case where an error occurred (e.g., display an error message)
            console.error('Order processing error:', response.error);
        }
    });
}

// Function to submit an ask
function submitAsk(userID, assetID, assetType, order_type, Price,  Quantity) {    
    var askData = {
        user_id: parseFloat(userID),
        asset_id: parseFloat(assetID),
        asset_type: assetType,
        action: 'sell',
        type: order_type,
        price: parseFloat(Price),
        quantity: parseFloat(Quantity)
    };

    console.log('Button ask pressed');
    socket.emit('submit_order', askData);

    // Listen for a response from the server
    socket.on('order_processed', function (response) {
        if (response.success) {
            // If the order was processed successfully, redirect to the portfolio page
            if (orderType == 'limit-price') {
                window.location.href = '/portfolio?transaction=' + encodeURIComponent('true');
            }
            else {
                window.location.href = '/portfolio?transaction=' + encodeURIComponent('false');
            }
        } else {
            // Handle the case where an error occurred (e.g., display an error message)
            console.error('Order processing error:', response.error);
        }
    });
}

// Select the HTML element with class "message"
const message = document.querySelector(".message");

// Set up a listener for the 'order_info' event
socket.on('order_info', (data) => {
    const errorMessage = data.message;
    message.innerHTML = `${errorMessage}`;
    console.log(`${errorMessage}`);

    message.classList.add('show');
    setTimeout(() => {message.classList.remove('show'); }, 5000);
});