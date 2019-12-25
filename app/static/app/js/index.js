// ---------------------------------------------------------------------------------------------------------------------
/**
 * Displays sub page for log in.
 */
function logInPageShow() {
    $("#log-in-sub-page").css("display", "block");
    $("#main").css("display", "none");
}

// ---------------------------------------------------------------------------------------------------------------------
/**
 * Hides sub page for log in.
 */
function logInPageHide() {
    $("#log-in-sub-page").css("display", "none");
    $("#main").css("display", "block");
}

// ---------------------------------------------------------------------------------------------------------------------
/**
 * Displays sub page for registration new user.
 */
function registerPageShow() {
    $("#register-sub-page").css("display", "block");
    $("#main").css("display", "none");
}

// ---------------------------------------------------------------------------------------------------------------------
/**
 * Hides sub page for registration new user.
 */
function registerPageHide() {
    $("#register-sub-page").css("display", "none");
    $("#main").css("display", "block");
}

// ---------------------------------------------------------------------------------------------------------------------
/**
 * Displays sub page for forgotten password.
 */
function forgotPageShow() {
    $("#forgot-status").text("");
    $("#forgot-sub-page").css("display", "block");
    $("#log-in-sub-page").css("display", "none");
}

// ---------------------------------------------------------------------------------------------------------------------
/**
 * Hides sub page for forgotten password.
 */
function forgotPageHide() {
    $("#forgot-sub-page").css("display", "none");
    $("#log-in-sub-page").css("display", "block");
}

// ---------------------------------------------------------------------------------------------------------------------
/**
 * Changes standard message in username 'Input' field.
 *
 * @param {Object} input
 */
function usernameSignInMessage(input) {
    if (input.validity.patternMismatch) {
        input.setCustomValidity("Имя пользователя должно содержать только\n" +
                                "латинские буквы, цифры, знаки подчеркивания\n" +
                                "и быть длиной не менее 2 и не более 30 символов.\n" +
                                "Если вы логинетесь используя Email, то формат стандартный для Email");
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
    var usernameInput = $("#username-input");

    // Send request only if 'Input' is not empty.
    if (usernameInput.val()) {
        $.ajax({
            url: "is-user-exists",
            type: "GET",
            data: {username: usernameInput.val()},

            success: function result(json) {
                if (json) {
                    document.getElementById("user-exists").style.display = "block";
                }
                else {
                    document.getElementById("user-exists").style.display = "none";
                }
            },

            error: function result(response) {
                 document.getElementById("user-exists").style.display = "block";
            }
        });
    }
}

// ---------------------------------------------------------------------------------------------------------------------
/**
 * Sends ajax request to check if the requested email is already exists.
 */
function checkMailNotExists() {
    // Send request only if 'Input' is not empty.
    if ($("#mail-input").val()) {
        $.ajax({
            url: "is-mail-exists",
            type: "GET",
            data: {email: $("#mail-input").val()},

            success: function result(json) {
                if (json) {
                    document.getElementById("mail-exists").style.display = "block";
                }
                else {
                    document.getElementById("mail-exists").style.display = "none";
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
    var isMailExists = document.getElementById("mail-exists").style.display;
    var isLinesEqual = document.getElementById("pass-wrong-message").style.display;
    var captcha = $('#g-recaptcha-response').val();

    if (!captcha) {
        $('#no-captcha').css('display', 'block');
    }

    if (isUserExists === "none" && isLinesEqual === "none" && isMailExists === "none" && captcha) {
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
            if (response.status === 404) {
                $("#forgot-status").text("Такого Email не обнаружено. Перепроверьте данные.");
            } else if (response.status === 400) {
                $("#forgot-status").text("Формат Email неправильный. Введите правильный еще раз, пожалуйста.");
            }
            else {
                $("#forgot-status").text("Произошла ошибка. Попробуйте снова или обратитесь к администрации.");
            }
        }
    });
}
