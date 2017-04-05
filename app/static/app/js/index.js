// ---------------------------------------------------------------------------------------------------------------------
/**
 * Displays sub page for log in.
 */
function logInPageShow() {
    fitLogin();
    $("#log-in-sub-page").css("display", "block");
    $("#main").css("display", "none");
}

// ---------------------------------------------------------------------------------------------------------------------
/**
 * Hides sub page for log in.
 */
function logInPageHide() {
    fitMain();
    $("#log-in-sub-page").css("display", "none");
    $("#main").css("display", "block");
}

// ---------------------------------------------------------------------------------------------------------------------
/**
 * Displays sub page for registration new user.
 */
function registerPageShow() {
    fitRegister();
    $("#register-sub-page").css("display", "block");
    $("#main").css("display", "none");
}

// ---------------------------------------------------------------------------------------------------------------------
/**
 * Hides sub page for registration new user.
 */
function registerPageHide() {
    fitMain();
    $("#register-sub-page").css("display", "none");
    $("#main").css("display", "block");
}

// ---------------------------------------------------------------------------------------------------------------------
/**
 * Displays sub page for forgotten password.
 */
function forgotPageShow() {
    $("#forgot-status").text("");
    fitForgot();
    $("#forgot-sub-page").css("display", "block");
    $("#log-in-sub-page").css("display", "none");
}

// ---------------------------------------------------------------------------------------------------------------------
/**
 * Hides sub page for forgotten password.
 */
function forgotPageHide() {
    fitForgot();
    $("#forgot-sub-page").css("display", "none");
    $("#log-in-sub-page").css("display", "block");
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
 * Sends mail to restore user data.
 */
function sendMail() {
    $("#forgot-status").text("");
    $.ajax({
        url: "send-mail",
        type: "POST",
        data: {
            email: $("#forgot-input").val(),
            csrfmiddlewaretoken: getCookie("csrftoken")
        },

        success: function result(json) {
            $("#forgot-status").text("Письмо успешно отправлено вам на почту!");
        },

        error: function(response) {
            if (response.status == 404) {
                $("#forgot-status").text("Такого Email не обнаружено. Перепроверьте данные.");
            }
            else {
                $("#forgot-status").text("Произошла ошибка. Попробуйте снова или обратитесь к администрации.");
            }
        }
    });
}

// ---------------------------------------------------------------------------------------------------------------------
/**
 * Creates artificial margin for fitting up the background image at main sub page.
 */
function fitMain() {
    $("#main").css("margin-bottom", $(window).height() - $("#main").height() + 6);
}

// ---------------------------------------------------------------------------------------------------------------------
/**
 * Creates artificial margin for fitting up the background image at login sub page.
 */
function fitLogin() {
    $("#log-in-sub-page").css("margin-bottom", $(window).height() - $("#log-in-sub-page").height() + 6);
}

// ---------------------------------------------------------------------------------------------------------------------
/**
 * Creates artificial margin for fitting up the background image at register sub page.
 */
function fitRegister() {
    $("#register-sub-page").css("margin-bottom", $(window).height() - $("#register-sub-page").height() + 6);
}

// ---------------------------------------------------------------------------------------------------------------------
/**
 * Creates artificial margin for fitting up the background image at forgot sub page.
 */
function fitForgot() {
    $("#forgot-sub-page").css("margin-bottom", $(window).height() - $("#register-sub-page").height() + 6);
}

// ---------------------------------------------------------------------------------------------------------------------
/**
 * Fits up the background image which depends on resize event.
 */
window.addEventListener("resize", function() {
    if ($("#main").css("display") == "block") fitMain();
    else if ($("#log-in-sub-page").css("display") == "block") fitLogin();
    else fitRegister();
});
