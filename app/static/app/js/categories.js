/**
 * Displays the loading spinner
 */
function loadDisplay() {
    $("#loading").css('display', 'block');
}

// ---------------------------------------------------------------------------------------------------------------------
/**
 * Hides the loading spinner
 */
function loadHide() {
    $("#loading").css('display', 'none');
}

// ---------------------------------------------------------------------------------------------------------------------
/**
 * Inserts books after ajax request.
 *
 * @param {Object<Object>} books The list of books.
 */
function insertBooks(books) {

    if (!books.length) {
        $(".books-area").append("<h4>По вашему запросу книг не найдено :(</h4>")
    }

    for (var book = 0; book < books.length; book++) {
        var id = books[book]["id"];
        var bookName = books[book]["name"];
        var author = books[book]["author"];
        var url = books[book]["url"];

        $(".books-area").append("<a href='book/" + id + "/'><div class='col-sm-3 col-md-3 col-lg-2 col-xs-6'" +
                                " align='left'><div class='thumbnail'><div class='img-wrapper'>" +
                                "<img src='" + url + "' alt='" + bookName + "'><div class='book-info word-wrap'>" +
                                "<strong>" + bookName + "</strong><br><i>" + author + "</i></div></div></div></div></a>");
    }
}

// ---------------------------------------------------------------------------------------------------------------------
/**
 * Sends ajax request for search books depending in entered data in the input.
 *
 * @param {number} pageNum        The current page number.
 */
function searchBooks(pageNum) {
    var searchData = $("#search-input").val();

    if (searchData) {
        loadDisplay();
        $.ajax({
            url: "search-book",
            type: "GET",
            data: {
                data: searchData,
                page: pageNum
            },

            success: function result(response) {
                if ($("#search-input").val()) {
                    removeNextBookBtn();
                    insertBooks(response['books']);

                    if (response['has_next']) {
                        addNextBookBtn(response['next_page']);
                    }
                }
                loadHide();
            }
        });
    }
    else {
        showCategories();
        clearBooksArea();
    }
}

// ---------------------------------------------------------------------------------------------------------------------
function clearBooksArea() {
    $(".books-area").empty();
}

// ---------------------------------------------------------------------------------------------------------------------
function addNextBookBtn(page) {
    $('.books-area').append(
        '<div id="load-books-area" class="align-center col-sm-12 col-md-12 col-lg-12">' +
        '<button class="btn load-books" ' +
        'onclick="searchBooks(' + page + ')">Загрузить еще</button></div>'
    )
}

// ---------------------------------------------------------------------------------------------------------------------
function removeNextBookBtn() {
    $('#load-books-area').remove();
}

// ---------------------------------------------------------------------------------------------------------------------
function showCategories() {
    $('#categories').css('display', 'block');
}

// ---------------------------------------------------------------------------------------------------------------------
function hideCategories() {
    $('#categories').css('display', 'none');
}

// ---------------------------------------------------------------------------------------------------------------------
/**
 * Returns the state back to output elements instead of found books.
 */
function returnState() {
    var searchData = $('#search-input').val();

    if (!searchData) {
        showCategories();
        clearBooksArea();
    }
}
