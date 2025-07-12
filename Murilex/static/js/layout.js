$(document).ready(function () {
    $("#logout").click(function (e) {
        e.preventDefault(); // Prevent the default click behavior (i.e., navigating to a URL)
        
        // Send an AJAX request to the logout endpoint
        $.get("/logout", function (data) {
            // Assuming the logout route returns some response (e.g., "Logged out successfully")
            //alert(data);  Display a message (you can customize this)
            
            // Reload the page or perform any other desired action
            location.reload();
        });
    });
});

document.getElementById('searchInput').onsubmit = function() {
  window.location = 'http://www.google.com/search?q= ' + document.getElementById('txtSearch').value;
  return false;
}