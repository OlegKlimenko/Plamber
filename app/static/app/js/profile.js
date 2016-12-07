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