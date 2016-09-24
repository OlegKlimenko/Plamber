// ---------------------------------------------------------------------------------------------------------------------
/**
 * Inserts books after ajax request.
 *
 * @param {Object<Object>} books The list of books.
 */
function insertBooks(books) {
    $(".booksArea").empty();

    for (var book = 0; book < books.length; book++) {
        var id = books[book]["id"];
        var bookName = books[book]["name"];
        var author = books[book]["author"];

        $(".booksArea").append("<a href='book/" + id + "/'><div class='book wordWrap' align='left'>" +
                               "<div><b>" + bookName + "</b></div>" +
                               "<div>" + author + "</div>" +
                               "</div></a>");
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
    $.ajax({
        url: "sort",
        type: "GET",
        data: {category: sortCategory,
               criterion: sortCriterion},

        success: function result(books) {
            insertBooks(books);
        }
    });
}

// ---------------------------------------------------------------------------------------------------------------------
/**
 * Changes classes on buttons for change their colors.
 */
function changeBtnColor(element) {
    if ($(".button").hasClass("selectedButtonColor")) {
        $(".button").removeClass("selectedButtonColor");
        $(".button").addClass("buttonColor");
    }

    $(element).removeClass("buttonColor");
    $(element).addClass("selectedButtonColor");
}

// ---------------------------------------------------------------------------------------------------------------------
/**
 * Sends ajax request for search books depending in entered data in the input.
 *
 * @param {number} searchCategory The number of a category.
 */
function searchBooks(searchCategory) {
    var searchData = $("#searchInput").val();

    if (searchData) {
            $.ajax({
            url: "search-book",
            type: "GET",
            data: {data: searchData,
                   category: searchCategory},

            success: function result(books) {
                insertBooks(books);
            }
        });
    }
    else {
        sort(searchCategory, "book_name");
    }
}
