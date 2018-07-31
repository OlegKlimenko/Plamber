// ---------------------------------------------------------------------------------------------------------------------
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
    $(".books-area").empty();

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
 * @param {number} searchCategory The number of a category.
 */
function searchBooks(searchCategory) {
    var searchData = $("#search-input").val();

    if (searchData) {
        loadDisplay();
        $.ajax({
            url: "search-book",
            type: "GET",
            data: {data: searchData,
                   category: searchCategory},

            success: function result(books) {
                if ($("#search-input").val()) {
                    insertBooks(books);
                    $('#categories').css('display', 'none');
                }
                loadHide();
            }
        });
    }
    else {
        $('#categories').css('display', 'block');
        $('.books-area').empty();
    }
}

// ---------------------------------------------------------------------------------------------------------------------
/**
 * Returns the state back to output elements instead of found books.
 */
function returnState() {
    var searchData = $('#search-input').val();

    if (!searchData) {
        $('#categories').css('display', 'block');
        $('.books-area').empty();
    }
}
