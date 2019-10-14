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
        var extension = books[book]["extension"]

        element = "<a href='book/" + id + "/'><div class='col-sm-3 col-md-3 col-lg-2 col-xs-6'" +
                  " align='left'><div class='thumbnail'><div class='img-wrapper'>"

        if (extension == "PDF") element += '<div class="ribbon ribbon-pdf">' + extension + '</div>'
        else if (extension == "FB2") element += '<div class="ribbon ribbon-fb2">' + extension + '</div>'

        element += "<img src='" + url + "' alt='" + bookName + "'><div class='book-info word-wrap'>" +
                   "<strong>" + bookName + "</strong><br><i>" + author + "</i></div></div></div></div></a>"

        $(".books-area").append(element);
    }
}

// ---------------------------------------------------------------------------------------------------------------------
/**
 * Sends ajax request for sorting depending on selected category.
 *
 * @param {string} sortCriterion The criterion by which we want to do sorting.
 * @param {number} sortCategory  The number of a category.
 */
function sort(sortCategory, sortCriterion) {
    loadDisplay();
    $.ajax({
        url: "sort",
        type: "GET",
        data: {category: sortCategory,
               criterion: sortCriterion},

        success: function result(books) {
            insertBooks(books);
            loadHide();
        }
    });
}

// ---------------------------------------------------------------------------------------------------------------------
/**
 * Changes classes on buttons for change their colors.
 */
function changeBtnColor(element) {
    if ($(".btn").hasClass("selected-button-color")) {
        $(".btn").removeClass("selected-button-color");
        $(".btn").addClass("button-color");
    }

    $(element).removeClass("button-color");
    $(element).addClass("selected-button-color");
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
                insertBooks(books);
                loadHide();
            }
        });
    }
    else {
        sort(searchCategory, "book_name");
    }
}

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
 * Returns the state back to output elements instead of found books.
 */
function returnState(searchCategory) {
    var searchData = $('#search-input').val();

    if (!searchData) {
        sort(searchCategory, "book_name");
    }
}
