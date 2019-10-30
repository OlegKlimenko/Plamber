var BOOK_IMAGE;

// ---------------------------------------------------------------------------------------------------------------------
/**
 * Fetches image from canvas and set it to image.
 */
function fetchData() {
    var canvas = document.getElementById("book-image");
    BOOK_IMAGE = canvas.toDataURL();
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

        success: function result(json) {
            $("#loading").css("display", "none");
            $("#the-book-image").attr("src", BOOK_IMAGE);
        }
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
        $("#loading").css("display", "block");
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

            $("#estimate-" + prev_estimate).attr('class', 'estimate');
            $("#estimate-" + newRating).attr('class', 'estimate-selected');

            prev_estimate = newRating;
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
                "<img class='img-responsive' src='" + imageSrc + "' alt='Фото пользователя'>" +
                "</div><div class='col-sm-10 col-md-10 col-lg-10 col-xs-7 word-wrap'>" +
                "<div class='word-wrap user-name margin'>" +
                "<strong>" + response['username'] + "</strong>" +
                "<strong> - <i class='comment-posted-date'>" + response['posted_date'] + "</i></strong></div>" +
                "<span class='text-font'>" + response['text'] + "</span>" +
                "</div></div></div>"
            );

            $("#add-comment-text").val("");
            $("html, body").animate({scrollBottom: $(document).height()});
        }
    });
}

// ---------------------------------------------------------------------------------------------------------------------
/**
 * Sends comment py pressing enter key.
 *
 * @param {object} event Standard event.
 * @param {number} id    Book identifier which is used to add comment.
 */
function addMessage(event, id) {
    if (event.keyCode == 13) {
        addComment(id);
    }
}

// ---------------------------------------------------------------------------------------------------------------------
/**
 * Fetches next page if next page is present.
 *
 * @param {number} currentPage The number of current page.
 * @param {number} bookId      ID of current book.
 */
function getNextPage(currentPage, bookId) {
    $("#load-comments-area").remove();

    $.ajax({
        url: "load-comments",
        type: "POST",
        data: {page: currentPage,
               book_id: bookId,
               csrfmiddlewaretoken: getCookie("csrftoken")},

        success: function result(response) {
            generateNextPageHTML(response);
        }
    });
}

// ---------------------------------------------------------------------------------------------------------------------
/**
 * Generates HTML output for loading new comments.
 *
 * @param {object} response The AJAX response in JSON.
 */
function generateNextPageHTML(response) {
    for (var elem in response["comments"]) {
        if (response["comments"].hasOwnProperty(elem)) {
            var user_photo = response["comments"][elem]['user_photo'];

            var imageSrc = user_photo ? user_photo : "/static/app/images/user.png";
            var username = response["comments"][elem]['username'];
            var postedDate = response["comments"][elem]['posted_date'];
            var text = response["comments"][elem]['text'];

            $("#all-comments").append(
                "<hr class='hr'><div class='row'><div class='col-sm-12 col-md-12 col-lg-12 col-xs-12'>" +
                "<div class='col-sm-2 col-md-2 col-lg-2 col-xs-5'>" +
                "<img class='img-responsive' src='" + imageSrc + "' alt='фото пользователя'>" +
                "</div><div class='col-sm-10 col-md-10 col-lg-10 col-xs-7 word-wrap'>" +
                "<div class='word-wrap user-name margin'>" +
                "<strong>" + username + "</strong>" +
                "<strong> - <i class='comment-posted-date'>" + postedDate + "</i></strong></div>" +
                "<span class='text-font'>" + text + "</span>" +
                "</div></div></div>");
        }
    }

    if (response['has_next_page']) {
        $("#all-comments").append(
            '<div id="load-comments-area" align="center">' +
            '<button id="load-comments" class="btn" ' +
            'onclick="getNextPage(' + response['current_page'] + ', ' + response['book_id'] + ')' +
            '">Еще комментарии</button>' +
            '</div>')
    }
}

// ---------------------------------------------------------------------------------------------------------------------
function reportBookShow() {
    $('#report-book-sub').css('display', 'block');
    $('#popup-background').css('display', 'block');
}

// ---------------------------------------------------------------------------------------------------------------------
function reportBookHide() {
    $('#report-book-sub').css('display', 'none');
    $('#popup-background').css('display', 'none');
}

// ---------------------------------------------------------------------------------------------------------------------
$(document).ready(function() {
    $('#report-book-submit').submit(function(e) {
        e.preventDefault();

        var formData = new FormData($(this)[0]);
        var extendedText = 'Book id:' + BOOK_ID + '\n' + formData.get('text');

        formData.append('text', extendedText);

        $.ajax({
            url: REPORT_URL,
            type: 'POST',
            data: formData,
            contentType: false,
            processData: false,

            success: function(response) {
                alert('Успешно отправлено!');
                $('#report-text').val('');
                reportBookHide();
            },

            error: function(response) {
                alert('Произошла ошибка...');
            }
        });

        return false;
    })
});
