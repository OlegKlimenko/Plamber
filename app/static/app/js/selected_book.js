// ---------------------------------------------------------------------------------------------------------------------
/**
 * Sends ajax request for adding book to user's own library; Generates additional HTML code.
 *
 * @param {string} csrf_token The special django token for avoid csrf attacks.
 */
function addBookHome(csrf_token) {
    $.ajax({
        url: "home-add-book",
        type: "POST",
        data: {book_id: $("#book_id").val(),
               csrfmiddlewaretoken: csrf_token},

        success: function(json) {
            $("#addBook").css("display", "none");
            $("#avgMach").after('<div id="removeBookDiv">' + '<button class="addBook buttonColor" id="removeBook">' +
                                "Удалить книгу</button>Сейчас книга в списке читаемых вами.</div>");
            $("#removeBook").attr("onClick", 'removeBookHome(' + '"' + csrf_token + '")');
        }
    });
}

// ---------------------------------------------------------------------------------------------------------------------
/**
 * Sends ajax request for removing book from user's own library; Generates additional HTML code.
 *
 * @param {string} csrf_token The special django token for avoid csrf attacks.
 */
function removeBookHome(csrf_token) {
    $.ajax({
        url: "home-remove-book",
        type: "POST",
        data: {book_id: $("#book_id").val(),
               csrfmiddlewaretoken: csrf_token},

        success: function(json) {
            $("#removeBookDiv").css("display", "none");
            $("#avgMach").after('<button class="addBook buttonColor" id="addBook">Добавить книгу</button>');
            $("#addBook").attr("onClick", 'addBookHome(' + '"' + csrf_token + '")');
        }
    });
}

// ---------------------------------------------------------------------------------------------------------------------
/**
 * Changes estimation of a book.
 *
 * @param {string} csrf_token The special django token for avoid csrf attacks.
 * @param {number} book_id The id of a book.
 * @param {number} rating The rating which we reset.
 */
function changeEstimation(csrf_token, book_id, rating) {
    $.ajax({
        url: "change-rating",
        type: "POST",
        data: {book_id: book_id,
               rating: rating,
               csrfmiddlewaretoken: csrf_token},

        success: function(json) {
            $("#rating").text(json);
        }
    });
}

// ---------------------------------------------------------------------------------------------------------------------
/**
 * Adds a comment to a book; Generates additional HTML code.
 *
 * @param {string} csrf_token The special django token for avoid csrf attacks.
 * @param {number} book_id The id of a book.
 */
function addComment(csrf_token, book_id) {
    $.ajax({
        url: "comment-add",
        type: "POST",
        data: {book_id: book_id,
               comment: $("#addCommentText").val(),
               csrfmiddlewaretoken: csrf_token},

        success: function(username) {
            $(".newComment").after('<div class="comment workBackground margins padding spaceWidth" align="right">' +
                                   '<img class="userPhoto" src="" width="120" height="120" alt="Фото пользователя">' +
                                   '<b>' + username + '</b><textarea class="commentText commentTextGeneral">' +
                                   $('#addCommentText').val() + '</textarea></div>');
            $('#addCommentText').val('');
            $('html, body').animate({scrollBottom: $(document).height()});
        }
    });
}