// ROWS 

const all_add = document.querySelectorAll(".row .add, .addcategory");
const all_rmv = document.querySelectorAll(".row .rmv, .rmvcategory");
const all_add_secondary = document.querySelectorAll(".add_secondary, .addcategory_secondary");
const all_rmv_secondary = document.querySelectorAll(".rmv_secondary, .rmvcategory_secondary");

const watchlist = document.getElementById("watchlist");
let total = 0;

all_add.forEach((link, index) => {
    link.addEventListener('click', function(event) {
        event.preventDefault();
        link.style.display = "none";
        all_rmv_secondary[index].style.display = "block";
        total++;
        updatePulseAnimation();
        if(displayVisible) {
            Display.classList.remove('show');
            setTimeout(function() {
                showAdded(index);
            }, 500);
        }
        else {
            showAdded(index);
        }
    });
});

all_rmv_secondary.forEach((link, index) => {
    link.addEventListener('click', function(event) {
        event.preventDefault();
        link.style.display = "none";
        all_add[index].style.display = "block";
        total--;
        updatePulseAnimation();
        if(displayVisible) {
            Display.classList.remove('show');
            setTimeout(function() {
                showRemoved(index);
            }, 500);
        }
        else {
            showRemoved(index);
        }
    });
});

all_rmv.forEach((link, index) => {
    link.addEventListener('click', function(event) {
        event.preventDefault();
        link.style.display = "none";
        all_add_secondary[index].style.display = "block";
        total--;
        updatePulseAnimation();
        if(displayVisible) {
            Display.classList.remove('show');
            setTimeout(function() {
                showRemoved(index);
            }, 500);
        }
        else {
            showRemoved(index);
        }
    });
});

all_add_secondary.forEach((link, index) => {
    link.addEventListener('click', function(event) {
        event.preventDefault();
        link.style.display = "none";
        all_rmv[index].style.display = "block";
        total++;
        updatePulseAnimation();
        if(displayVisible) {
            Display.classList.remove('show');
            setTimeout(function() {
                showAdded(index);
            }, 500);
        }
        else {
            showAdded(index);
        }
    });
});

//DISPLAY ANIMATION

const names = document.querySelectorAll(".row .song-name");
const images = document.querySelectorAll(".row .image-song");
const selectedImage = document.querySelector(".selected-image");
const selectedName = document.querySelector(".selected-name");
const selectedMsg = document.querySelector(".add_or_rmv");
const Display = document.querySelector(".display");


let displayVisible = false;

function showAdded(index) {
    const image = images[index].getAttribute('data-value');
    selectedImage.src = image;
    const name = names[index].getAttribute('data-value');
    selectedName.textContent = name;
    selectedMsg.textContent = "Added  to";

    displayVisible = true;
    Display.classList.add('show'); // Apply the 'show' class to trigger the transition

    setTimeout(() => {
        displayVisible = false;
        Display.classList.remove('show'); // Remove the 'show' class after 5 seconds
    }, 7000); // Hide after 5000 milliseconds (5 seconds)
}

function showRemoved(index) {
    const image = images[index].getAttribute('data-value');
    selectedImage.src = image;
    const name = names[index].getAttribute('data-value');
    selectedName.textContent = name;
    selectedMsg.textContent = "Removed  from";

    displayVisible = true;
    Display.classList.add('show'); // Apply the 'show' class to trigger the transition

    setTimeout(() => {
        displayVisible = false;
        Display.classList.remove('show'); // Remove the 'show' class after 5 seconds
    }, 7000); // Hide after 5000 milliseconds (5 seconds)
}


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

            var userId = this.getAttribute("data-user-id");
            var itemId = this.getAttribute("data-item-id");
            var assetType = this.getAttribute("data-asset-type");
            var action = this.getAttribute("data-action");

            performWatchlistAction(userId, itemId, assetType, action);
        });
    });

    // Remove button click event
    document.querySelectorAll(".rmv, .rmv_secondary").forEach(function(button) {
        button.addEventListener("click", function(event) {
            event.preventDefault();

            var userId = this.getAttribute("data-user-id");
            var itemId = this.getAttribute("data-item-id");
            var assetType = this.getAttribute("data-asset-type");
            var action = this.getAttribute("data-action");

            performWatchlistAction(userId, itemId, assetType, action);
        });
    });

    // Function to send data to the server
    function performWatchlistAction(userIdentifier, itemIdentifier, assetType, action) {
        fetch("/manage_assets", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                user_id: userIdentifier,
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

//  CATEGORIES

const addButton = document.querySelector(".addcategory, .addcategory_secondary");
const removeButton = document.querySelector(".rmvcategory, .rmvcategory_secondary");

console.log("addButton:", addButton);
console.log("removeButton:", removeButton);

addButton.addEventListener("click", function () {
    const categoryId = addButton.getAttribute("data-item-id");
    manageCategory(categoryId, "add");
});

removeButton.addEventListener("click", function () {
    const categoryId = removeButton.getAttribute("data-item-id");
    manageCategory(categoryId, "remove");
});

async function manageCategory(categoryId, action) {
    try {
        const response = await fetch('/manage_categories', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                category_id: categoryId,
                action: action
            })
        });

        const data = await response.json();
        console.log(data.message);  // Log the response message from the server

        // You can update the UI or display a message to the user based on the response
    } catch (error) {
        console.error('Error:', error);
        // Handle error cases, such as failed fetch or invalid JSON response
    }
}

all_add_secondary.forEach(add => {
    add.style.display='none';
})
all_rmv_secondary.forEach(rmv => {
    rmv.style.display='none';
})

// Connect to the Socket.IO server
const socket = io();

socket.on('connect', function () {
    console.log('Connected to Socket.io');
});

socket.on('asset_price_update', function(data) {
    // Handle the received bid/ask update data
    console.log('Received new assset price update:', data);

    var asset_id = data.asset_id;
    var asset_type = data.asset_type;
    var price = data.price;

    // Find the HTML element corresponding to the asset ID and type
    var assetElement = document.querySelector(`.price[data-asset-id="${asset_id}"][data-asset-type="${asset_type}"]`);

    if (assetElement) {
        // Update the price display for the specific asset
        var priceElement = assetElement.querySelector('.price-value');
        if (priceElement) {
            priceElement.textContent = price + '$'; // You can format it as needed
        }
    }
});

socket.on('asset_price_change', function(data) {
    // Handle the received bid/ask update data
    console.log('Received new assset price change update:', data);

    var asset_id = data.asset_id;
    var asset_type = data.asset_type;
    var price = parseFloat(data.price_change).toFixed(2);;

    // Find the HTML element corresponding to the asset ID and type
    var assetElement = document.querySelector(`.price[data-asset-id="${asset_id}"][data-asset-type="${asset_type}"]`);

    if (assetElement) {
        // Update the price display for the specific asset
        var priceElement = assetElement.querySelector('.price-change');
        if (priceElement) {
            priceElement.textContent = price + '%'; // You can format it as needed
        }
    }
});

// D3 GRAPHS

function createChart(data, chartContainer) {
    // Set up SVG dimensions
    const width = 800;
    const height = 250;
    const margin = { top: 20, right: 20, bottom: 30, left: 40 };

    const svg = d3.select(chartContainer)
    .append('svg')
    .attr('width', '110%') // Set the width to 100% of the container
    .attr('height', '110%') // Set the height to 100% of the container
    .attr('preserveAspectRatio', 'xMinYMin meet')
    .attr('viewBox', `0 0 ${width} ${height}`);

    // Sort the data by timestamp in ascending order
    data.sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp));

    // Extract timestamp and price data
    const dates = data.map(d => d.timestamp);
    const prices = data.map(d => d.price);

    // Create scales for x and y axes
    const x = d3.scaleBand()
        .domain(dates)
        .range([margin.left, width - margin.right])
        .padding(0);

    const y = d3.scaleLinear()
        .domain([0, d3.max(prices)])
        .nice()
        .range([height - margin.bottom, margin.top]);

    // Create a line generator
    const line = d3.line()
        .x((d, i) => x(dates[i]) + x.bandwidth() / 2)
        .y(d => y(d.price));

    // Append a path element for the line
    svg.append('path')
        .datum(data)
        .attr('class', 'line')
        .attr('d', line);

}

// Set the default timeframe to "max"
const defaultTimeframe = "max";

// Create and render a chart for each chart-container
function createAndRenderCharts() {
    // Find all elements with id="chart-container"
    const chartContainers = document.querySelectorAll('#chart-container');

    // Loop through each chart container
    chartContainers.forEach((chartContainer, index) => {
        // You can generate unique assetId and assetType for each container based on your data
        const assetId = chartContainer.getAttribute('data-item-id');
        const assetType = chartContainer.getAttribute('data-asset-type');
        

        console.log(`Container ${index}:`, chartContainer);
        console.log('Asset ID:', assetId);
        console.log('Asset Type:', assetType);

        fetch(`/api/data_rest?asset_id=${assetId}&asset_type=${assetType}`)
        .then(response => response.json())
        .then(data => {
            console.log('Data received:', data);
            if (data.length === 0) {
                console.log('No data available.');
                chartContainer.innerHTML = '';
            } else {
                console.log('Rendering chart with data:', data);
                // Create and render the chart in the current chartContainer
                createChart(data, chartContainer);
            }
        })
        .catch(error => {
            console.error('Error fetching data:', error);
        });
    });
}

// Call the function to create and render charts when the page loads
window.addEventListener('load', createAndRenderCharts);
