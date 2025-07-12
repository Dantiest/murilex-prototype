//DIVISIONS IN THE BOTTOM BAR

const numDivisions = document.querySelectorAll('.division').length;
const divisionElements = document.querySelectorAll('.division');

const divisionWidthPercentage = 100 / numDivisions;

divisionElements.forEach((division) => {
    division.style.width = divisionWidthPercentage + '%';
});

//FILTER

const sections = [
    { title: 'pendingTable', contentId: 'pending'},
    { title: 'allTable', contentId: 'table-all' },
    { title: 'cataloguesTable', contentId: 'catalogues-table' },
    { title: 'albumsTable', contentId: 'albums-table' },
    { title: 'songsTable', contentId: 'songs-table' },
];

function toggleVisibility(element, isVisible) {
    if (element) {
        element.style.display = isVisible ? 'flex' : 'none';
    }
}

function hideAllSections() {
    sections.forEach(section => {
        const content = document.querySelector(`#${section.contentId}`);
        toggleVisibility(content, false);
    });
}

function showSection(section) {
    const content = document.querySelector(`#${section.contentId}`);
    toggleVisibility(content, true);
}

function showContainerByTitle(title) {
    hideAllSections();
    const section = sections.find(section => section.title === title);
    if (section) {
        showSection(section);
    }
}

document.querySelector('.category-button-all').addEventListener('click', () => showContainerByTitle('allTable'));
document.querySelector('.category-button-catalogues').addEventListener('click', () => showContainerByTitle('cataloguesTable'));
document.querySelector('.category-button-songs').addEventListener('click', () => showContainerByTitle('songsTable'));
document.querySelector('.category-button-albums').addEventListener('click', () => showContainerByTitle('albumsTable'));
document.querySelector('.category-button-pending').addEventListener('click', () => showContainerByTitle('pendingTable'));

const buttons = document.querySelectorAll(".category-button");

buttons.forEach(button => {
    button.addEventListener('click', () => {
        buttons.forEach(butt => {
            butt.style.backgroundColor = '#7216f4';
        })
        button.style.backgroundColor = 'rgb(45, 45, 45)';
    });
});


if (document.querySelector('.all').getAttribute('data-value') == 'true') {
    showContainerByTitle('pendingTable');
    document.querySelector('.category-button-pending').style.backgroundColor = 'black';
}
else {
    showContainerByTitle('allTable');
    document.querySelector('.category-button-all').style.backgroundColor = 'black';
}


//SOCKET.IO

var socket = io();

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
    var price = parseFloat(data.price_change).toFixed(2);

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

const cancelBids = document.querySelectorAll('.rmv.bid');
const cancelAsks = document.querySelectorAll('.rmv.ask');

cancelBids.forEach(bid => {
    bid.addEventListener('click', () => {
        let bid_id = bid.getAttribute('data-bid-id');
        cancelbid(bid_id);
        bid.parentNode.style.display = 'none';
    });
});

cancelAsks.forEach(ask => {
    ask.addEventListener('click', () => {
        let ask_id = ask.getAttribute('data-ask-id');
        cancelask(ask_id);
        ask.parentNode.style.display = 'none';
    });
});

function cancelbid(bid_id) {
    fetch("/cancel_the_bid", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            item_id: bid_id, // Pass the bidId as item_id
        }),
    })
    .then(response => {
        if (response.ok) {
            return response.json();
        } else {
            throw new Error("Failed to cancel bid");
        }
    })
    .then(data => {
        console.log(data.message); // Handle the response message
        // You can perform additional actions based on the response here
    })
    .catch(error => {
        console.error("Error canceling bid:", error);
        // Handle the error appropriately
    });
}

function cancelask(ask_id) {
    fetch("/cancel_the_ask", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            item_id: ask_id, // Pass the askId as item_id
        }),
    })
    .then(response => {
        if (response.ok) {
            return response.json();
        } else {
            throw new Error("Failed to cancel ask");
        }
    })
    .then(data => {
        console.log(data.message); // Handle the response message
        // You can perform additional actions based on the response here
    })
    .catch(error => {
        console.error("Error canceling ask:", error);
        // Handle the error appropriately
    });
}

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

    // Add x and y axes
    svg.append('g')
        .attr('class', 'x-axis')
        .attr('transform', `translate(0,${height - margin.bottom})`)

    svg.append('g')
        .attr('class', 'y-axis')
        .attr('transform', `translate(${margin.left},0)`)
        .call(d3.axisLeft(y));
        
    svg.selectAll('text').style('font-size', '20px'); // Adjust the font-size value

    svg.selectAll('.bar')
    .data(data)
    .enter().append('rect')
    .attr('class', 'bar')

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
        

        //const assetId = 1;
        //const assetType = 'catalogue';
        const timeframe = 'max';

        console.log(`Container ${index}:`, chartContainer);
        console.log('Asset ID:', assetId);
        console.log('Asset Type:', assetType);

        fetch(`/api/data_rest?asset_id=${assetId}&asset_type=${assetType}&timeframe=${timeframe}`)
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
