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

        $(".books-area").append("<a href='book/" + id + "/'><div class='col-sm-3 col-md-3 col-lg-2 col-xs-6'>" +
                                "<div class='thumbnail'><div class='img-wrapper'>" +
                                "<img src='" + url + "' alt='" + bookName + "'><div class='book-info word-wrap'>" +
                                "<strong>" + bookName + "</strong><br><i>" + author + "</i></div></div></div></div></a>");
    }
}

// ---------------------------------------------------------------------------------------------------------------------
/**
 * Sends ajax request for sorting depending on selected category.
 *
 * @param {string} sortCriterion The criterion by which we want to do sorting.
 * @param {number} sortCategory  The number of a category.
 * @param {number} pageNum       The number of the page to output.
 */
function sort(sortCategory, sortCriterion, pageNum) {
    loadDisplay();
    $.ajax({
        url: "sort",
        type: "GET",
        data: {
            category: sortCategory,
            criterion: sortCriterion,
            page: pageNum
        },

        success: function result(response) {
            removeNextBookBtn();
            insertBooks(response['books']);

            if (response['has_next']) {
                addNextBookSortBtn(response['category'], response['criterion'], response['next_page']);
            }
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
 * @param {number} pageNum        The current page number.
 */
function searchBooks(searchCategory, pageNum) {
    var searchData = $("#search-input").val();

    if (searchData) {
        loadDisplay();
        $.ajax({
            url: "search-book",
            type: "GET",
            data: {
                data: searchData,
                category: searchCategory,
                page: pageNum
            },

            success: function result(response) {
                removeNextBookBtn();
                insertBooks(response['books']);

                if (response['has_next']) {
                    addNextBookSearchBtn(searchCategory, response['next_page']);
                }
                loadHide();
            }
        });
    }
    else {
        clearBooksArea();
        sortAreaDisplay();
        sort(searchCategory, "book_name",1);
    }
}

// ---------------------------------------------------------------------------------------------------------------------
function clearBooksArea() {
    $(".books-area").empty();
}

// ---------------------------------------------------------------------------------------------------------------------
function removeNextBookBtn() {
    $('#load-books-area').remove();
}

// ---------------------------------------------------------------------------------------------------------------------
function addNextBookBtn(categoryId, page) {
    $('.books-area').append(
        '<div id="load-books-area" class="align-center col-sm-12 col-md-12 col-lg-12">' +
        '<button class="btn load-books" ' +
        'onclick="loadNextBooks(' + categoryId + ',' + page + ')">Загрузить еще</button></div>'
    )
}

// ---------------------------------------------------------------------------------------------------------------------
function addNextBookSearchBtn(categoryId, page) {
    $('.books-area').append(
        '<div id="load-books-area" class="align-center col-sm-12 col-md-12 col-lg-12">' +
        '<button class="btn load-books" ' +
        'onclick="searchBooks(' + categoryId + ',' + page + ')">Загрузить еще</button></div>'
    )
}

// ---------------------------------------------------------------------------------------------------------------------
function addNextBookSortBtn(categoryId, criterion, page) {
    $('.books-area').append(
        "<div id='load-books-area' class='align-center col-sm-12 col-md-12 col-lg-12'>" +
        "<button class='btn load-books' " +
        "onclick='sort(" + categoryId + "," + '"' + criterion + '",' + page + ")'>Загрузить еще</button></div>"
    )
}

// ---------------------------------------------------------------------------------------------------------------------
/**
 * Loads the book paging output without filters.
 *
 * @param {number} categoryId  The category identifier.
 * @param {number} currentPage The current page to output identifier.
 */
function loadNextBooks(categoryId, currentPage) {
    $.ajax({
        url: "/category/" + categoryId + "/load-books/",
        type: "GET",
        data: {'page': currentPage},

        success: function result(response) {
            removeNextBookBtn();
            insertBooks(response['books']);

            if (response['has_next']) {
                addNextBookBtn(response['category_id'], response['next_page']);
            }
        }
    });
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
function sortAreaDisplay() {
    $(".sort-area").css('display', 'block');
}

// ---------------------------------------------------------------------------------------------------------------------
function sortAreaHide() {
    $(".sort-area").css('display', 'none');
}

// ---------------------------------------------------------------------------------------------------------------------
/**
 * Returns the state back to output elements instead of found books.
 */
function returnState(searchCategory) {
    var searchData = $('#search-input').val();

    if (!searchData) {
        clearBooksArea();
        sortAreaDisplay();
        changeBtnColor($("#default-sort-btn"));
        sort(searchCategory, "book_name", 1);
    }
}
