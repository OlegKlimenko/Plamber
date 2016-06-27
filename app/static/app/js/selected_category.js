// ---------------------------------------------------------------------------------------------------------------------
/**
 * Sends ajax request for sorting depending on selected category.
 *
 * @param {string} criterion The criterion by which we want to do sorting.
 * @param {number} category  The number of a category.
 */
function sort(category, criterion) {
    $.ajax({
        url: "sort",
        type: "GET",
        data: {category: category,
               criterion: criterion},

        success: function(books) {
            insertBooks(books);
        }
    });
}

// ---------------------------------------------------------------------------------------------------------------------
/*
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
 * Inserts books after ajax request.
 *
 * @param {Object<Object>} books The list of books.
 */
function insertBooks(books) {
    $('.booksArea').empty();

    for (var book = 0; book < books.length; book++) {
        var id = books[book]["id"];
        var book_name = books[book]["name"];
        var author = books[book]["author"];

        $(".booksArea").append('<a href="book/' + id + '/"><div class="book workBackground">' +
                              '<img class="bookImage" src="" width="100" height="150" alt="Изображение книги">' +
                              '<div class="bookName">' + book_name + '</div>' +
                              '<div class="bookAuthor">' + author + '</div>' +
                              '</div></a>');
    }
}

// ---------------------------------------------------------------------------------------------------------------------
/*
 * Sends ajax request for search books depending in entered data in the input.
 *
 * @param {number} category The number of a category.
 */
function searchBooks(category) {
    var search_data = $("#searchInput").val();

    if (search_data) {
            $.ajax({
            url: "search-book",
            type: "GET",
            data: {search_data: search_data,
                   category: category},

            success: function(books) {
                insertBooks(books);
            }
        });
    }
    else {
        sort(category, "book_name");
    }
}
