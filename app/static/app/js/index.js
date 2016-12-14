// ---------------------------------------------------------------------------------------------------------------------
/**
 * Displays sub page for log in.
 */
function logInPageShow() {
    $("#log-in-sub-page").css("display", "block");
}

// ---------------------------------------------------------------------------------------------------------------------
/**
 * Hides sub page for log in.
 */
function logInPageHide() {
    $("#log-in-sub-page").css("display", "none");
}

// ---------------------------------------------------------------------------------------------------------------------
/**
 * Displays sub page for registration new user.
 */
function registerPageShow() {
    $("#register-sub-page").css("display", "block");
}

// ---------------------------------------------------------------------------------------------------------------------
/**
 * Hides sub page for registration new user.
 */
function registerPageHide() {
    $("#register-sub-page").css("display", "none");
}

// ---------------------------------------------------------------------------------------------------------------------
/**
 * Changes standard message in username 'Input' field for signing new user.
 *
 * @param {Object} input
 */
function usernameSignInMessage(input) {
    if (input.validity.patternMismatch) {
        input.setCustomValidity("Имя пользователя должно содержать только\n" +
                                "латинские буквы, цифры, знаки подчеркивания\n" +
                                "и быть длиной не менее 6 и не более 30 символов");
    } else {
        input.setCustomValidity("");
    }
}

// ---------------------------------------------------------------------------------------------------------------------
/**
 * Changes standard message in password 'Input' field for signing new user.
 *
 * @param {Object} input
 */
function passwordSignInMessage(input) {
    if (input.validity.patternMismatch) {
        input.setCustomValidity("Пароль должен содержать только\n" +
                                "латинские буквы, цифры, знаки подчеркивания\n" +
                                "и быть длиной не менее 6 и не более 16 символов");
    } else {
        input.setCustomValidity("");
    }
}

// ---------------------------------------------------------------------------------------------------------------------
/**
 * Checks if both of 'Input' password lines are equal.
 */
function checkEqualPassLines() {
    var firstInputValue = document.getElementById("first-pass").value;
    var secondInputValue = document.getElementById("second-pass").value;

    if (firstInputValue !== secondInputValue) {
        document.getElementById("pass-wrong-message").style.display = "block";
    }
    else {
        document.getElementById("pass-wrong-message").style.display = "none";
    }
}

// ---------------------------------------------------------------------------------------------------------------------
/**
 * Sends ajax request to check if the user is already exists.
 */
function checkUserNotExists() {
    // Send request only if 'Input' is not empty.
    if ($("#username-input").val()) {
        $.ajax({
            url: "is-user-exists",
            type: "GET",
            data: {username: $("#username-input").val()},

            success: function result(json) {
                if (json) {
                    document.getElementById("user-exists").style.display = "block";
                }
                else {
                    document.getElementById("user-exists").style.display = "none";
                }
            }
        });
    }
}

// ---------------------------------------------------------------------------------------------------------------------
/**
 * Sends form only if both of password 'Input' lines are equals and filled.
 *
 * @param {Object} event
 */
function isSignInAvailable(event) {
    var isUserExists = document.getElementById("user-exists").style.display;
    var isLinesEqual = document.getElementById("pass-wrong-message").style.display;

    if (isUserExists === "none" && isLinesEqual === "none") {
        event.submit();
    }
}

// ---------------------------------------------------------------------------------------------------------------------
/**
 * Shows the inputs passwords when mouse down.
 */
function showPasswords(src) {
    $('.eye-img').attr('src', src);
    $('input[name="passw"]').attr('type', 'text');
    $('input[name="passw1"]').attr('type', 'text');
    $('input[name="passw2"]').attr('type', 'text');
}

// ---------------------------------------------------------------------------------------------------------------------
/**
 * Hides the inputs passwords when mouse up.
 */
function hidePasswords(src) {
    $('.eye-img').attr('src', src);
    $('input[name="passw"]').attr('type', 'password');
    $('input[name="passw1"]').attr('type', 'password');
    $('input[name="passw2"]').attr('type', 'password');
}
