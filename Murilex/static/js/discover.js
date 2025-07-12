
const slider = document.querySelector('.slider');
const arrowLeft = document.querySelector('.left');
const arrowRight = document.querySelector('.right');
const indicatorParents = document.querySelector('.controls ul');
const sliderProfiles = document.querySelectorAll('.slider .profile');

var sectionIndex = 0;

sliderProfiles[sectionIndex].style.opacity = 1; // Set the initial opacity to fully visible
indicatorParents.children[sectionIndex].classList.add('selected');

// Calculate the width of each slide based on the number of profiles
const slideWidth = 100 / sliderProfiles.length;

// Function to move to the next slide
function moveToNextSlide() {
    sliderProfiles[sectionIndex].style.opacity = 0; // Fade out the current profile
    sectionIndex = (sectionIndex < sliderProfiles.length - 1) ? sectionIndex + 1 : 0;
    sliderProfiles[sectionIndex].style.opacity = 1; // Fade in the new profile
    document.querySelector('.controls .selected').classList.remove('selected');
    indicatorParents.children[sectionIndex].classList.add('selected');
    slider.style.transform = `translate(${sectionIndex * -slideWidth}%)`;
}

document.querySelectorAll('.controls li').forEach(function(indicator, ind) {
    indicator.addEventListener('click', function() {
        sliderProfiles[sectionIndex].style.opacity = 0; // Fade out the current profile
        sectionIndex = ind;
        sliderProfiles[sectionIndex].style.opacity = 1; // Fade in the new profile
        document.querySelector('.controls .selected').classList.remove('selected');
        indicator.classList.add('selected');
        slider.style.transform = `translate(${sectionIndex * -slideWidth}%)`;
    });
});

arrowRight.addEventListener('click', function() {
    moveToNextSlide();
});

arrowLeft.addEventListener('click', function() {
    sliderProfiles[sectionIndex].style.opacity = 0; // Fade out the current profile
    sectionIndex = (sectionIndex > 0) ? sectionIndex - 1 : sliderProfiles.length - 1; // If at the first slide, move to the last one
    sliderProfiles[sectionIndex].style.opacity = 1; // Fade in the new profile
    document.querySelector('.controls .selected').classList.remove('selected');
    indicatorParents.children[sectionIndex].classList.add('selected');
    slider.style.transform = `translate(${sectionIndex * -slideWidth}%)`;
  });
  
// Call the moveToNextSlide function every 5 seconds (adjust the time as needed)
setInterval(moveToNextSlide, 15000);


//FILTER

const dropdownLinks = document.querySelectorAll('.dropdown-content a');
const selectedBox = document.querySelector('.selected-box');

dropdownLinks.forEach(link => {
  link.addEventListener('click', function(event) {
    event.preventDefault();
    const selectedValue = this.getAttribute('data-value');
    const svgIcon = '<svg class="clearBtn" xmlns="http://www.w3.org/2000/svg" style="height: 15px; fill: black; margin-right: 4px; margin-left: 4px" viewBox="0 0 384 512"><!--! Font Awesome Free 6.4.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license (Commercial License) Copyright 2023 Fonticons, Inc. --><path d="M342.6 150.6c12.5-12.5 12.5-32.8 0-45.3s-32.8-12.5-45.3 0L192 210.7 86.6 105.4c-12.5-12.5-32.8-12.5-45.3 0s-12.5 32.8 0 45.3L146.7 256 41.4 361.4c-12.5 12.5-12.5 32.8 0 45.3s32.8 12.5 45.3 0L192 301.3 297.4 406.6c12.5 12.5 32.8 12.5 45.3 0s12.5-32.8 0-45.3L237.3 256 342.6 150.6z"/></svg>';
    const input = '<input class="filterBy" style="padding: 3px; width: 5rem; margin-left: 3px" placeholder="...">';
    
    const newBox = document.createElement('div');
    newBox.innerHTML = `${selectedValue}: ${input} ${svgIcon}`;
    newBox.style = "border: 3px solid #7216f4; border-radius: 20px; height: 100%; padding: 5px; margin-right: 7px; font-family: 'Lato', sans-serif";
    selectedBox.appendChild(newBox);
    link.style.display = "none";
    
    // Select the .clearBtn inside newBox
    const clearBtn = newBox.querySelector('.clearBtn');
    clearBtn.addEventListener('click', function() {
      selectedBox.removeChild(newBox);
      link.style.display = "block";
    });
  });
});
