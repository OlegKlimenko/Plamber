var remove_book_id;

// ---------------------------------------------------------------------------------------------------------------------
/**
 * Shows sub window to comfirm remove selected book.
 *
 * @param {number} id   The unique identifier of the book.
 * @param {string} name The book name.
 */
function showRemoveSub(id, name) {
    remove_book_id = id;

    $('#book-name').text(name);
    $('#remove-book-sub').css('display', 'block');
}

// ---------------------------------------------------------------------------------------------------------------------
/**
 * Hides sub window for confirming remove selected book.
 */
function hideRemoveSub() {
    $('#remove-book-sub').css('display', 'none');
}

// ---------------------------------------------------------------------------------------------------------------------
/**
 * Send Ajax request for removing selected book.
 */
function removeBook() {
    $.ajax({
        url: 'home-remove-book',
        type: 'POST',
        data: {
            book: remove_book_id,
            csrfmiddlewaretoken: getCookie("csrftoken")
        },

        success: function(response) {
            $('#book_' + remove_book_id).remove();
            hideRemoveSub();
        }
    });
}

// ---------------------------------------------------------------------------------------------------------------------
/**
 * Shows sub area for changing user's avatar.
 */
function showChangeAvatarArea() {
    $('#change-avatar').css('display', 'block');
}

// ---------------------------------------------------------------------------------------------------------------------
/**
 * Hides sub area for changing user's avatar.
 */
function hideChangeAvatarArea() {
    $('#change-avatar').css('display', 'none');
}

// ---------------------------------------------------------------------------------------------------------------------
/**
 * Sends ajax request for changing avatar.
 */
function changeAvatar() {
    var avatar = $('input[name="user_avatar"]');
    var form_data = new FormData();

    if (!avatar.val()) {
        $('#status-message').text('Bыберите фото!');
    }
    else {
        form_data.append('avatar', avatar.prop('files')[0]);
        form_data.append('csrfmiddlewaretoken', getCookie("csrftoken"));

        $.ajax({
            url: '/upload-avatar/',
            type: 'POST',
            cache: false,
            contentType: false,
            processData: false,
            data: form_data,

            success: function(response) {
                $('#status-message').text(response['message']);
                $('#profile-image').attr('src', response['avatar_url']);
            },

            error: function(response) {
                $('#status-message').text('Не удалось загрузить фото. Попробуйте еще раз.');
            }
        });

        hideChangeAvatarArea();
    }
}

// ---------------------------------------------------------------------------------------------------------------------
/**
 * Shows the area for changing password.
 */
function showChangePasswordArea() {
    $('#change-password').css('display', 'block');
}

// ---------------------------------------------------------------------------------------------------------------------
/**
 * Hides the area for changing password.
 */
function hideChangePasswordArea() {
    $('#change-avatar').css('display', 'block');
}

// ---------------------------------------------------------------------------------------------------------------------
/**
 * Validates the password inputs before sending.
 */
function validatePasswordInputs() {
    var re = new RegExp('^[a-zA-Z0-9_]{6,16}$');

    var prev_password = $('#prev-password');
    var new_password_one = $('#new-password-one');
    var new_password_two = $('#new-password-two');

    if (!prev_password.val() || !new_password_one.val() || !new_password_two.val()) {
        $('#status-message').text('Заполните пожалуйста все поля для ввода.');
        return false;
    }
    else if (!re.test(prev_password.val()) || !re.test(new_password_one.val()) || !re.test(new_password_two.val())) {
        $('#status-message').text(
            'Формат пароля(лей) не верный. Пароль должен содержать только ' +
            'латинские буквы, цифры, знаки подчеркивания ' +
            'и быть длиной не менее 6 и не более 16 символов.'
        );
        return false;
    }
    else if (new_password_one.val() != new_password_two.val()) {
        $('#status-message').text('Последние два поля должны совпадать.')
    }
    else {
        return true;
    }
}

// ---------------------------------------------------------------------------------------------------------------------
/**
 * Sends ajax request for changing user's password.
 */
function changePassword() {
    if (validatePasswordInputs()) {
        $.ajax({
            url: 'change-password',
            type: 'POST',
            data: {
                'prev_password': $('#prev-password').val(),
                'new_password': $('#new-password-one').val(),
                'csrfmiddlewaretoken': getCookie("csrftoken")
            },

            success: function(response) {
                $('#status-message').text(response);
            },

            error: function(response) {
                $('#status-message').text('Не удалось поменять пароль. Попробуйте снова.')
            }
        });
    }
}

// ---------------------------------------------------------------------------------------------------------------------
/**
 * Shows the inputs passwords when mouse down.
 */
function showPasswords(src) {
    $('.eye-img').attr('src', src);
    $('#prev-password').attr('type', 'text');
    $('#new-password-one').attr('type', 'text');
    $('#new-password-two').attr('type', 'text');
}

// ---------------------------------------------------------------------------------------------------------------------
/**
 * Hides the inputs passwords when mouse up.
 */
function hidePasswords(src) {
    $('.eye-img').attr('src', src);
    $('#prev-password').attr('type', 'password');
    $('#new-password-one').attr('type', 'password');
    $('#new-password-two').attr('type', 'password');
}
