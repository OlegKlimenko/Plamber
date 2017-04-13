// ---------------------------------------------------------------------------------------------------------------------
/**
 * Initiates and shows loading spinner.
 */
function showSpinner() {

}

// ---------------------------------------------------------------------------------------------------------------------
/**
 * Hides loading spinner.
 */
function hideSpinner() {
    
}

// ---------------------------------------------------------------------------------------------------------------------
/**
 * Returns the cookie with special name.
 *
 * @param {string} name The name.
 */
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== "") {
        var cookies = document.cookie.split(";");
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            if (cookie.substring(0, name.length + 1) === (name + "=")) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// ---------------------------------------------------------------------------------------------------------------------
/**
 * Submits the selected form
 */
function logout() {
    $("#logout").submit();
}
