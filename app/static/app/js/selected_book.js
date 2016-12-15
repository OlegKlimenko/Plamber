// ---------------------------------------------------------------------------------------------------------------------
/**
 * Fetches image from canvas and set it to image.
 */
function fetchData() {
    var canvas = document.getElementById("book-image");
    var dataURL = canvas.toDataURL();

    $("#the-book-image").attr("src", dataURL);
}

// ---------------------------------------------------------------------------------------------------------------------
/**
 * Renders the page of the PDF document.
 *
 * @param {Object} pdf        The instance of the pdf document.
 * @param {number} pageNumber The number of a page which we need to render.
 */
function renderPage(pdf, pageNumber) {
    pdf.getPage(pageNumber).then(function (page) {
        var scale = 1.5;
        var viewPort = page.getViewport(scale);

        var canvas = document.getElementById("book-image");
        var context = canvas.getContext("2d");

        canvas.height = viewPort.height;
        canvas.width = viewPort.width;

        var renderContext = {
            canvasContext: context,
            viewport: viewPort
        };

        var task = page.render(renderContext);
        task.promise.then(function() {
            fetchData();
        });
    });
}

// ---------------------------------------------------------------------------------------------------------------------
/**
 * Loads the image of a book.
 */
function loadImage() {
    var url = $("#book-url").text();
    PDFJS.workerSrc = "/static/app/js/third_party/pdf_js/pdf.worker.js";

    PDFJS.getDocument(url).then(function (pdf) {
        renderPage(pdf, 1)
    });
}

// ---------------------------------------------------------------------------------------------------------------------
/**
 * Checks if image of the book is setted on the page. If no, it loads from book, and stores in database with book.
 */
$(document).ready(function() {
    var src = $("#the-book-image").attr("src");
    if (src) {}
    else {
        loadImage();
    }
});

// ---------------------------------------------------------------------------------------------------------------------
/**
 * Sends ajax request for adding book to user's own library; Generates additional HTML code.
 */
function addBookHome() {
    $.ajax({
        url: "home-add-book",
        type: "POST",
        data: {book: $("#book-id").val(),
               csrfmiddlewaretoken: getCookie("csrftoken")},

        success: function result(json) {
            $("#add-book-div").remove();
            $("#left-side").append("<div id='remove-book-div'><button class='add-book' id='remove-book'>" +
                                   "Удалить книгу</button>" +
                                   "<div class='word-wrap add-book-text'>" +
                                   "Сейчас книга в списке читаемых вами.</div></div>");
            $("#remove-book").attr("onClick", "removeBookHome()");
        }
    });
}

// ---------------------------------------------------------------------------------------------------------------------
/**
 * Sends ajax request for removing book from user's own library; Generates additional HTML code.
 */
function removeBookHome(csrfToken) {
    $.ajax({
        url: "home-remove-book",
        type: "POST",
        data: {book: $("#book-id").val(),
               csrfmiddlewaretoken: getCookie("csrftoken")},

        success: function result(json) {
            $("#remove-book-div").remove();
            $("#left-side").append("<div id='add-book-div'><button class='add-book' " +
                                   "id='add-book'>Добавить книгу</button></div>");
            $("#add-book").attr("onClick", "addBookHome()");
        }
    });
}

// ---------------------------------------------------------------------------------------------------------------------
/**
 * Changes estimation of a book.
 *
 * @param {number} idBook The id of a book.
 * @param {number} newRating The rating which we reset.
 */
function changeEstimation(idBook, newRating) {
    $.ajax({
        url: "change-rating",
        type: "POST",
        data: {book: idBook,
               rating: newRating,
               csrfmiddlewaretoken: getCookie("csrftoken")},

        success: function result(json) {
            $("#rating").text(json);
        }
    });
}

// ---------------------------------------------------------------------------------------------------------------------
/**
 * Adds a comment to a book; Generates additional HTML code.
 *
 * @param {number} idBook The id of a book.
 */
function addComment(idBook) {
    $.ajax({
        url: "comment-add",
        type: "POST",
        data: {book: idBook,
               comment: $("#add-comment-text").val(),
               csrfmiddlewaretoken: getCookie("csrftoken")},

        success: function result(response) {
            $("#comments-header").after("<hr class='hr'>" +
                                        "<div class='comment' align='left'>" +
                                        "<div class='user-photo'>" +
                                        "<img class='comment-photo' src='" + response['user_photo'] + "' " +
                                        "width='120' height='120'>" +
                                        "<div class='word-wrap user-name'><b>" + response['username'] +
                                        "</b></div></div>" +
                                        "<div class='comment-text word-wrap'>" + response['text'] + "</div></div>");

            $("#add-comment-text").val("");
            $("html, body").animate({scrollBottom: $(document).height()});
        }
    });
}
