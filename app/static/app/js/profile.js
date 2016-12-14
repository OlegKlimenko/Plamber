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
