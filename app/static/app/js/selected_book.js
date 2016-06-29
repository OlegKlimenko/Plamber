// ---------------------------------------------------------------------------------------------------------------------
/**
 * Sends ajax request for adding book to user's own library; Generates additional HTML code.
 *
 * @param {string} csrfToken The special django token for avoid csrf attacks.
 */
function addBookHome(csrfToken) {
    $.ajax({
        url: "home-add-book",
        type: "POST",
        data: {book: $("#book_id").val(),
               csrfmiddlewaretoken: csrfToken},

        success: function result(json) {
            $("#addBook").css("display", "none");
            $("#avgMach").after("<div id='removeBookDiv'>" + "<button class='addBook buttonColor' id='removeBook'>" +
                                "Удалить книгу</button>Сейчас книга в списке читаемых вами.</div>");
            $("#removeBook").attr("onClick", "removeBookHome(" + "'" + csrfToken + "')");
        }
    });
}

// ---------------------------------------------------------------------------------------------------------------------
/**
 * Sends ajax request for removing book from user's own library; Generates additional HTML code.
 *
 * @param {string} csrfToken The special django token for avoid csrf attacks.
 */
function removeBookHome(csrfToken) {
    $.ajax({
        url: "home-remove-book",
        type: "POST",
        data: {book: $("#book_id").val(),
               csrfmiddlewaretoken: csrfToken},

        success: function result(json) {
            $("#removeBookDiv").css("display", "none");
            $("#avgMach").after("<button class='addBook buttonColor' id='addBook'>Добавить книгу</button>");
            $("#addBook").attr("onClick", "addBookHome(" + "'" + csrfToken + "')");
        }
    });
}

// ---------------------------------------------------------------------------------------------------------------------
/**
 * Changes estimation of a book.
 *
 * @param {string} csrfToken The special django token for avoid csrf attacks.
 * @param {number} idBook The id of a book.
 * @param {number} newRating The rating which we reset.
 */
function changeEstimation(csrfToken, idBook, newRating) {
    $.ajax({
        url: "change-rating",
        type: "POST",
        data: {book: idBook,
               rating: newRating,
               csrfmiddlewaretoken: csrfToken},

        success: function result(json) {
            $("#rating").text(json);
        }
    });
}

// ---------------------------------------------------------------------------------------------------------------------
/**
 * Adds a comment to a book; Generates additional HTML code.
 *
 * @param {string} csrfToken The special django token for avoid csrf attacks.
 * @param {number} idBook The id of a book.
 */
function addComment(csrfToken, idBook) {
    $.ajax({
        url: "comment-add",
        type: "POST",
        data: {book: idBook,
               comment: $("#addCommentText").val(),
               csrfmiddlewaretoken: csrfToken},

        success: function result(username) {
            $(".newComment").after("<div class='comment workBackground margins padding spaceWidth' align='right'>" +
                                   "<img class='userPhoto' src='' width='120' height='120' alt='Фото пользователя'>" +
                                   "<b>" + username + "</b><textarea class='commentText commentTextGeneral'>" +
                                   $("#addCommentText").val() + "</textarea></div>");
            $("#addCommentText").val("");
            $("html, body").animate({scrollBottom: $(document).height()});
        }
    });
}