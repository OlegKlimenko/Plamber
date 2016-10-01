// ---------------------------------------------------------------------------------------------------------------------
//function storeBookImage() {
//    $.ajax({
//        url: "store-book-image",
//        type: "POST",
//        data: {book: $("book_name").val(),
//              image: $("#book_file"),
//               csrfmiddlewaretoken: getCookie("csrftoken")},
//
//        contentType: false,        cache: false,
//       processData:false,
//
//
//        success: function(json) {
//            console.log("YEAH!!!");
//        }
//    });
//}

// ---------------------------------------------------------------------------------------------------------------------
/**
 * Fetches image from canvas and set it to image.
 */
function fetchData() {
    var canvas = document.getElementById("book_image");
    var dataURL = canvas.toDataURL();

    $("#theBookImage").attr("src", dataURL);
//    $("#book_file").attr("src", "http://files.porsche.com/filestore/image/multimedia/none/991-2nd-c2s-modelimage-sideshot/model/e4c9e332-5539-11e5-8c32-0019999cd470;s3/porsche-model.png");
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

        var canvas = document.getElementById("book_image");
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
//            storeBookImage();
        });
    });
}

// ---------------------------------------------------------------------------------------------------------------------
/**
 * Loads the image of a book.
 */
function loadImage() {
    var url = $("#book_url").text();
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
    var src = $("#theBookImage").attr("src");
    if (src) {}
    else {
        loadImage();
    }
});

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
            $("#addBookDiv").remove();
            $("#leftSide").append("<div id='removeBookDiv'><button class='addBook' id='removeBook'>" +
                                  "Удалить книгу</button>" +
                                  "<div class='wordWrap addBookText'>Сейчас книга в списке читаемых вами.</div></div>");
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
            $("#removeBookDiv").remove();
            $("#leftSide").append("<div id='addBookDiv'><button class='addBook' " +
                                  "id='addBook'>Добавить книгу</button></div>");
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
            $("#commentsHeader").after("<hr class='hr'>" +
                                   "<div class='comment' align='left'>" +
                                   "<div class='userPhoto'>" +
                                   "<img src='' width='120' height='120'>" +
                                   "<div class='wordWrap userName'><b>" + username + "</b></div></div>" +
                                   "<div class='commentText wordWrap'>" + $("#addCommentText").val() + "</div></div>");

            $("#addCommentText").val("");
            $("html, body").animate({scrollBottom: $(document).height()});
        }
    });
}