// ---------------------------------------------------------------------------------------------------------------------
/**
 * Sends ajax request for sorting depending on selected category.
 *
 * @param string 'criterion' The criterion by which we want to do sorting.
 * @param number 'category'  The number of a category.
 */
function sort(category, criterion) {
    $.ajax({
        url: 'sort',
        type: 'GET',
        data: {category: category,
               criterion, criterion},

        success: function(books) {
            $('.booksArea').empty();

            for (var book = 0; book < books.length; book++) {
                id = books[book]['id'];
                book_name = books[book]['name'];
                author = books[book]['author'];

                $('.booksArea').append('<a href="book/' + id + '/"><div class="book workBackground">' +
                                      '<img class="bookImage" src="" width="100" height="150">' +
                                      '<div class="bookName">' + book_name + '</div>' +
                                      '<div class="bookAuthor">' + author + '</div>' +
                                      '</div></a>');
            }
        }
    });
}

// ---------------------------------------------------------------------------------------------------------------------
/*
 * Changes classes on buttons for change their colors.
 */
function changeBtnColor(element) {
    if ($('.button').hasClass('selectedButtonColor')) {
        $('.button').removeClass('selectedButtonColor');
        $('.button').addClass('buttonColor');
    }

    $(element).removeClass('buttonColor');
    $(element).addClass('selectedButtonColor');
}