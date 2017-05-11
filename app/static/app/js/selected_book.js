var BOOK_IMAGE;

// ---------------------------------------------------------------------------------------------------------------------
/**
 * Fetches image from canvas and set it to image.
 */
function fetchData() {
    var canvas = document.getElementById("book-image");
    var dataURL = canvas.toDataURL();

    $("#the-book-image").attr("src", dataURL);
    BOOK_IMAGE = dataURL;
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
            storeImage();
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
 * Stores the image of a book to database.
 */
function storeImage() {
    $.ajax({
        url: "store-book-image",
        type: "POST",
        data: {
            id: $("#book-id").val(),
            image: BOOK_IMAGE,
            csrfmiddlewaretoken: getCookie("csrftoken")
        },

        success: function result(json) {}
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
            window.location.replace('/read-book/' + json['book_id'] + '/');
        }
    });
}

// ---------------------------------------------------------------------------------------------------------------------
/**
 * Sends ajax request for removing book from user's own library; Generates additional HTML code.
 */
function removeBookHome() {
    $.ajax({
        url: "home-remove-book",
        type: "POST",
        data: {book: $("#book-id").val(),
               csrfmiddlewaretoken: getCookie("csrftoken")},

        success: function result(json) {
            $("#remove-book-div").remove();
            $("#btn-area").append("<div id='add-book-div'><button class='btn' " +
                                  "id='add-book'>Начать читать</button></div>");
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
            $("#rating").text(json['avg_rating']);
            $("#rating-count").text(json['rating_count']);
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
            var imageSrc = response['user_photo'] ? response['user_photo'] : "/static/app/images/user.png";

            $("#no-comments").remove();
            $("#comments").after(
                "<hr class='hr'><div class='row'><div class='col-sm-12 col-md-12 col-lg-12 col-xs-12'>" +
                "<div class='col-sm-2 col-md-2 col-lg-2 col-xs-5'>" +
                "<img class='img-responsive' src='" + imageSrc + "'>" +
                "</div><div class='col-sm-10 col-md-10 col-lg-10 col-xs-7 word-wrap'>" +
                "<div class='word-wrap user-name margin'>" +
                "<b>" + response['username'] + "</b>" +
                "<b> - <i class='comment-posted-date'>" + response['posted_date'] + "</i></b></div>" +
                "<span class='text-font'>" + response['text'] + "</span>" +
                "</div></div></div>"
            );

            $("#add-comment-text").val("");
            $("html, body").animate({scrollBottom: $(document).height()});
        }
    });
}
