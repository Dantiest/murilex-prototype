document.addEventListener('DOMContentLoaded', function() {
    const sections = [
        { title: 'categories', titleId: 'categories-title', contentId: 'categories' },
        { title: 'catalogues', titleId: 'catalogues-title', contentId: 'catalogues-all' },
        { title: 'albums', titleId: 'albums-title', contentId: 'albums-all' },
        { title: 'songs', titleId: 'songs-title', contentId: 'songs-all' },

        { title: 'cataloguesTable', titleId: 'catalogues-title', contentId: 'catalogues-table' },
        { title: 'albumsTable', titleId: 'albums-title', contentId: 'albums-table' },
        { title: 'songsTable', titleId: 'songs-title', contentId: 'songs-table' },
    ];

    function toggleVisibility(element, isVisible) {
        element.style.display = isVisible ? 'flex' : 'none';
    }

    function hideAllSections() {
        sections.forEach(section => {
            const titles = document.querySelectorAll(`#${section.titleId}`);
            const contents = document.querySelectorAll(`#${section.contentId}`);
            titles.forEach(title => {
                toggleVisibility(title, false);
            });
            contents.forEach(content => {
                toggleVisibility(content, false);
            });
        });
    }

    function showSection(section) {
        const title = document.querySelector(`#${section.titleId}`);
        const content = document.querySelector(`#${section.contentId}`);
        toggleVisibility(title, true);
        toggleVisibility(content, true);
    }

    function showContainerByTitle(title) {
        hideAllSections();
        const section = sections.find(section => section.title === title);
        if (section) {
            showSection(section);
        }
    }

    function showAll() {
        hideAllSections();
        sections.slice(0, 4).forEach(section => {
            const titles = document.querySelectorAll(`#${section.titleId}`);
            const contents = document.querySelectorAll(`#${section.contentId}`);
            titles.forEach(title => {
                toggleVisibility(title, true);
            });
            contents.forEach(content => {
                toggleVisibility(content, true);
            });
        });
    }

    /*document.querySelector('.category-button-all').addEventListener('click', () => {
        hideAllSections();
        // Show covers for all sections
        sections.forEach(section => {
            if (section.title !== 'cataloguesTable' || section.title !== 'songsTable' || section.title !== 'albumsTable') {
                toggleVisibility(document.querySelector(`#${section.contentId}`), true);
                toggleVisibility(document.querySelector(`#${section.titleId}`), true);
            }
        });
    });*/
    document.querySelector('.category-button-all').addEventListener('click', () => showAll());
    document.querySelector('.category-button-categories').addEventListener('click', () => showContainerByTitle('categories'));
    document.querySelector('.category-button-catalogues').addEventListener('click', () => showContainerByTitle('cataloguesTable'));
    document.querySelector('.category-button-songs').addEventListener('click', () => showContainerByTitle('songsTable'));
    document.querySelector('.category-button-albums').addEventListener('click', () => showContainerByTitle('albumsTable'));


    const buttons = document.querySelectorAll(".category-button");

    buttons.forEach(btn => {
        btn.addEventListener('click', () => {
            buttons.forEach(otherBtn => {
                otherBtn.style.backgroundColor = '#7216f4';
            });
            btn.style.backgroundColor = 'rgb(45, 45, 45)';
        });
    });

});

//REMOVE


const all_remove = document.querySelectorAll(".remove");
const all_rmv = document.querySelectorAll(".rmv");

all_remove.forEach((button, index) => {
    button.addEventListener('click', () => {
        event.preventDefault();

        const parentElement = button.parentElement;
        parentElement.classList.add('hidden');

        all_rmv[index].parentElement.classList.add('hidden');

        var itemId = button.getAttribute("data-item-id");
        var assetType = button.getAttribute("data-asset-type");

        performWatchlistAction(itemId, assetType, "remove");
    });
});

all_rmv.forEach((button, index) => {
    button.addEventListener('click', () => {
        event.preventDefault();

        const parentElement = button.parentElement;
        
        parentElement.classList.add('hidden');

        all_remove[index].parentElement.classList.add('hidden');

        var itemId = button.getAttribute("data-item-id");
        var assetType = button.getAttribute("data-asset-type");

        performWatchlistAction(itemId, assetType, "remove");

        // Check if all_rmv buttons are all hidden
        const allHidden = Array.from(all_rmv).every(button => button.parentElement.classList.contains('hidden'));

        if (allHidden) {
            // Do something when all elements are hidden
        }
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
    const height = 500;
    const margin = { top: 160, right: 80, bottom: 120, left: 200 };

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
