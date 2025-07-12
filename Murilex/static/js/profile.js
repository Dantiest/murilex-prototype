const user_status = document.getElementById('edit-profile').getAttribute('data-value');

if(user_status == 'True') {
    document.querySelector('#top-profile').style.display = 'none';
}

const sections = [
    { title: 'leaderboardTable', contentId: 'leaderboard'},
    { title: 'allTable', contentId: 'table-all' },
    { title: 'graph', contentId: 'graph' },
    { title: 'transactionTable', contentId: 'transaction-table' },
];

function toggleVisibility(element, isVisible) {
    element.style.display = isVisible ? 'flex' : 'none';
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


document.querySelector('#stats-button').addEventListener('click', () => showContainerByTitle('graph'));
document.querySelector('#leaderboard-button').addEventListener('click', () => showContainerByTitle('leaderboardTable'));
document.querySelector('#portfolio-button').addEventListener('click', () => showContainerByTitle('allTable'));
document.querySelector('#transactions-button').addEventListener('click', () => showContainerByTitle('transactionTable'));



const buttons = document.querySelectorAll(".switch-button");

buttons.forEach(button => {
    button.addEventListener('click', () => {
        buttons.forEach(butt => {
            butt.style.borderBottom = 'none';
        })
        button.style.borderBottom = '3px solid #7216f4';
    });
});


/* DETAILS ___________________________________________  DETAILS */

const screen = document.querySelector('.screen');
const information = document.querySelector('.information');
const close = document.querySelector('.close');

const editInputs = document.querySelectorAll('.edit-input');
const editButtons = document.querySelectorAll('.edit-button');
const editTexts = document.querySelectorAll('.edit-text');


document.querySelector('#edit-profile').addEventListener('click', () => {
    screen.style.display = 'block';
    information.style.display = 'flex';
});


close.addEventListener('click', () => {
    screen.style.display = 'none';
    information.style.display = 'none';
    editInputs.forEach(input => {
        input.style.display = 'none';
        input.value = '';
    });
    editTexts.forEach(text => {
        text.style.display = 'block';
    });
    editButtons.forEach(button => {
        button.style.display = 'block';
    });
});

screen.addEventListener('click', () => {
    screen.style.display = 'none';
    information.style.display = 'none';
    editInputs.forEach(input => {
        input.style.display = 'none';
        input.value = '';
    });
    editTexts.forEach(text => {
        text.style.display = 'block';
    });
    editButtons.forEach(button => {
        button.style.display = 'block';
    });
});

editButtons.forEach((button, index) => {
    button.addEventListener('click', () => {
        button.style.display = 'none';
        editTexts[index].style.display = 'none';
    });
});

/* EDIT PROFILE */

function hideElement(element) {
    element.style.display = 'none';
}

// Function to show the input field for editing
function showEditInput(inputId) {
    // Hide the "Edit" button and show the input field
    document.getElementById(inputId).style.display = 'inline-block';
}

// Event listeners for "Edit" buttons
document.getElementById('editProfileImage').addEventListener('click', () => {
    showEditInput('newProfileImage', 'editProfileImage'); // Pass the edit button ID
});
document.getElementById('editUsername').addEventListener('click', () => {
    showEditInput('newUsername', 'editUsername'); // Pass the edit button ID
});

document.getElementById('editEmail').addEventListener('click', () => {
    showEditInput('newEmail', 'editEmail'); // Pass the edit button ID
});

// Event listener for pressing Enter key in an input field
document.addEventListener('keydown', function (e) {
    if (e.key === 'Enter') {
        e.preventDefault();
        const targetId = e.target.id;
        const relatedEditId = 'edit' + targetId;

        // Hide the input field and show the "Edit" button
        document.getElementById(targetId).style.display = 'none';
        document.getElementById(relatedEditId).style.display = 'inline-block';

        // Update the profile information in the DOM
        const newValue = document.getElementById(targetId).value;
        document.getElementById(targetId.replace('new', '')).textContent = newValue;

        // Show the corresponding text element
        document.getElementById(targetId.replace('new', '')).style.display = 'block';
    }
});

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
    const margin = { top: 40, right: 40, bottom: 80, left: 80 };

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
    .style('fill', 'red') // Color of the data points
    .style('opacity', 0)
    .style('stroke', '#fff')
    .style('stroke-width', '2');

    dataPoints.on('mouseover', (event, d) => {
        // Show the tooltips
        xTooltip.style.display = 'block';
        yTooltip.style.display = 'block';

        // Hide other data points (circles) and make the selected one fully visible
        dataPoints.style('opacity', 0);
        d3.select(event.currentTarget).style('opacity', 0); // Make the hovered point fully visible

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

// Function to create and render the chart
function createAndRenderChart() {
    const chartContainer = document.getElementById('chart-container');

    const userID = chartContainer.getAttribute('user-id');


    fetch(`/api/data_balance?user_id=${userID}`)
        .then(response => response.json())
        .then(data => {
            // Use the fetched data to create your D3.js chart
            createChart(data);
        })
        .catch(error => {
            console.error('Error fetching data:', error);
        });
}

window.addEventListener('load', createAndRenderChart);

/* SOCKETS ______________________________________________ SOCKETS */

const saveButton = document.getElementById('save'); // Assuming you have a button with the id 'save-button'

saveButton.addEventListener('click', () => {
    let emailNew = document.getElementById('newEmail').value;
    let usernameNew = document.getElementById('newUsername').value;
    let imageNew = document.getElementById('newProfileImage').value;
    
    const updatedData = {
        // Conditionally include email property if emailNew has a value
        email: emailNew ? emailNew : null,
        // Always include username property
        username: usernameNew ? usernameNew : null,
        // Conditionally include profile_image property if imageNew has a value
        profile_image: imageNew ? imageNew : null
    };

    if (!emailNew && !usernameNew && !imageNew) {
        // Assuming you have a list of input elements with the class 'edit-input'
        const editInputs = document.querySelectorAll('.edit-input');
        editInputs.forEach(input => {
            input.style.borderColor = 'red'; // Change borderColor to style.borderColor
        });

        return;
    }

    // Send a POST request to the backend
    fetch('/updateProfile', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(updatedData)
    })
    .then(response => response.json())
    .then(data => {
        console.log(data.message); // Log the response message from the backend
        location.reload(); // Reload the page on success
    })
    .catch(error => {
        console.error('Error:', error);
    });
});

const userBalance = parseFloat(document.getElementById('balance').textContent);

document.getElementById('return').textContent = `${((userBalance-1000)/1000 * 100).toFixed(2)}%`;

const profits = document.querySelectorAll('.available.profit');
const balances = document.querySelectorAll('.price-value.balance'); // Use the correct selector

profits.forEach((profit, index) => {
    const balance = parseFloat(balances[index].textContent); // Convert text content to a number
    profit.textContent = `${(balance - 1000) / 10}%`;
});

