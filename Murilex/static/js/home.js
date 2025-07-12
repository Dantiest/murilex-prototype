//TICKER

var ticker = document.querySelector('.ticker');
var list = document.querySelector('.ticker__list');
var clone1 = list.cloneNode(true);
var clone2 = list.cloneNode(true);

ticker.append(clone1, clone2);
let totalArticles = 0;

//NEWS

const apikey = 'b40984074c7b4ef82340579c1e8ea746';
const gnewsUrl = 'https://gnews.io/api/v4/search?q=music releases&apikey=' + apikey;

const container = document.querySelector(".container");
const seeMoreButton = document.getElementById("seeMoreButton");
let articles = []; // Store the fetched articles
let visibleArticles = 4; // Number of articles to show initially
let step = 3; // Number of articles to load on "See More"

function handleImageError(imageElement) {
  // Replace the broken image with a placeholder or an error message
  imageElement.src = "static/image/murexe_out.jpg";
}

// Create cards from data
const generateUI = (articles, startIndex, endIndex) => {
  for (let i = startIndex; i < endIndex; i++) {
    const item = articles[i];
    let card = document.createElement("a");
    card.classList.add("news-card");
    card.setAttribute("href", item.url);
    console.log("URL to Image:", item.urlToImage);
    card.innerHTML = `<div class="news-image-container">
    <div class="news-division">
      <svg style="fill: #7216f4" xmlns="http://www.w3.org/2000/svg" height="1.5rem" viewBox="0 0 512 512"><path d="M96 96c0-35.3 28.7-64 64-64H448c35.3 0 64 28.7 64 64V416c0 35.3-28.7 64-64 64H80c-44.2 0-80-35.8-80-80V128c0-17.7 14.3-32 32-32s32 14.3 32 32V400c0 8.8 7.2 16 16 16s16-7.2 16-16V96zm64 24v80c0 13.3 10.7 24 24 24H296c13.3 0 24-10.7 24-24V120c0-13.3-10.7-24-24-24H184c-13.3 0-24 10.7-24 24zm208-8c0 8.8 7.2 16 16 16h48c8.8 0 16-7.2 16-16s-7.2-16-16-16H384c-8.8 0-16 7.2-16 16zm0 96c0 8.8 7.2 16 16 16h48c8.8 0 16-7.2 16-16s-7.2-16-16-16H384c-8.8 0-16 7.2-16 16zM160 304c0 8.8 7.2 16 16 16H432c8.8 0 16-7.2 16-16s-7.2-16-16-16H176c-8.8 0-16 7.2-16 16zm0 96c0 8.8 7.2 16 16 16H432c8.8 0 16-7.2 16-16s-7.2-16-16-16H176c-8.8 0-16 7.2-16 16z"/></svg>
      <txt>News</txt>
    </div>
    <img class="news-image" src="${item.urlToImage}" alt="${item.title}" onerror="handleImageError(this); console.log('Image loading error:', this);">
    </div>
    <div class="news-content">
      <div class="news-title">
        ${item.title}
      </div>
      <div class="news-description">
        ${item.description || item.content || ""}
      </div>
    </div>`;
    container.appendChild(card);
  }
};

// Fetch news data and generate UI
fetch(gnewsUrl)
  .then(response => response.json())
  .then(data => {
    articles = data.articles;
    generateUI(articles, 0, visibleArticles); // Display initial articles
  })
  .catch(error => console.error('Error fetching news data:', error));

// Show more articles when the button is clicked
let timesClicked = 0;
seeMoreButton.addEventListener("click", () => {
  visibleArticles += step;
  generateUI(articles, visibleArticles - step, visibleArticles);
  timesClicked++;
  console.log(`timesClicked: ${timesClicked}`);
  updateSeeMoreButtonVisibility();
});

// Function to update the visibility of the "See More" button
function updateSeeMoreButtonVisibility() {
  const remainingArticles = articles.length - visibleArticles;
  if (remainingArticles <= 0) {
    seeMoreButton.style.display = 'none';
  } else {
    seeMoreButton.style.display = 'block';
  }
}

// if (totalArticles < (timesClicked * step + visibleArticles)) {
//   seeMoreButton.style.display = 'none';
// }

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

// D3 GRAPHS

function createChart(data, chartContainer) {
  // Set up SVG dimensions
  const width = 90;
  const height = 20;
  const margin = { top: 0, right: 0, bottom: 0, left: 0 };

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


function search_artists(){
  //get search input and reuslts list
  var user_search = document.getElementById("search_input");
  var results_list = document.getElementById("...");

  // when something is put in, search data base for similar letter, and pass into display function
  user_search.addEventListener("input", function() {
    var searchTerm = user_search.ariaValueMax.toLowerCase();
    filteredResults = sql;
    displayResults(filteredResults);
});
}



function displayResults(results) {
  searchResults.innerHTML = " ";
  results.forEach(result => {
    listItem = document.createElement("li");
    listItem.textContent = result;
    listItem.addEventListener("click", function(){
      search_input = result;
      resultsList.style.display = "none";
    });
    resultsList.appendChild(listItem)
  });

  if (results.length > 0){
    searchResults.style.display = "block";
  }
  else{
    searchResults.style.display = "none"
  }
}

window.addEventListener("click", function(event){
  if (!search_input.contains(event.target) && !searchResults.contains(event.target)){
    searchResults.style.display = "none";
  }
});
