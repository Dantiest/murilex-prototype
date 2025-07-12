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

// D3 GRAPHS

function createChart(data, chartContainer) {
    // Set up SVG dimensions
    const width = 800;
    const height = 500;
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
                chartContainer.innerHTML = 'No data yet';
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
