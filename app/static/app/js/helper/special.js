// Options for loading spinner
var spinner_opts = {
    lines: 9,
    length: 28,
    width: 14,
    radius: 42,
    scale: 0.3,
    corners: 1,
    color: '#fff',
    opacity: 0.15,
    rotate: 0,
    direction: 1,
    speed: 1,
    trail: 60,
    fps: 20,
    zIndex: 2e9,
    className: 'spinner',
    top: '50%',
    left: '50%',
    shadow: false,
    hwaccel: false,
    position: 'absolute'
};

// ---------------------------------------------------------------------------------------------------------------------
/**
 * Initiates the spinner.
 */
function initSpinner() {
    var target = document.getElementById('spinner');
    new Spinner(spinner_opts).spin(target);
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
