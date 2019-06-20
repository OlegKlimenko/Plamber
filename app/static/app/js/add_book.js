// ---------------------------------------------------------------------------------------------------------------------
/**
 * Inserts authors in HTML document, depending on count of authors.
 *
 * @param {Object} authors The list of authors.
 */
function insertAuthors(authors) {
    if (authors.length > 0) {
        $("#div-authors-list").css("display", "block");
        $("#div-authors-list-header").css("display", "block");
        $("#div-authors-list").empty();

        for (var author = 0; author < authors.length; author++) {
            $("#div-authors-list").append("<div align='left'>" +
                                          "<a class='reference' onclick='selectedAuthor(this)'>" +
                                          authors[author] + "</a></div>");
        }
    }
}

// ---------------------------------------------------------------------------------------------------------------------
/**
 * Creates Ajax request for generating author list.
 */
function generateAuthors() {
    if ($("#author-input").val() !== "") {
        $.ajax({
            url: "generate-authors",
            type: "GET",
            data: {part: $("#author-input").val()},

            success: function result(authors) {
                insertAuthors(authors);
            }
        });
    }
    else {
        $("#div-authors-list-header").css("display", "none");
        $("#div-authors-list").empty();
    }
}

// ---------------------------------------------------------------------------------------------------------------------
/**
 * Inserts books in HTML document, depending on count of books.
 *
 * @param {Object} books The list of books.
 */
function insertBooks(books) {
    if (books.length > 0) {
        $("#div-books-list").css("display", "block");
        $("#div-books-list-header").css("display", "block");
        $("#div-books-list").empty();

        for (var book = 0; book < books.length; book++) {
            $("#div-books-list").append("<div align='left'>" +
                                          "<a class='reference' href='" + books[book]['url'] + "'>" +
                                          books[book]['name'] + "</a></div>");
        }
    }
}

// ---------------------------------------------------------------------------------------------------------------------
/**
 * Creates Ajax request for generating book list.
 */
function generateBooks() {
    if ($("#book-input").val() !== "") {
        $.ajax({
            url: "generate-books",
            type: "GET",
            data: {part: $("#book-input").val()},

            success: function result(books) {
                insertBooks(books)
            }
        });
    }
    else {
        $("#div-books-list-header").css("display", "none");
        $("#div-books-list").empty();
    }
}

// ---------------------------------------------------------------------------------------------------------------------
/**
 * Sets the name of selected author to HTML 'Input' field.
 *
 * @param {Object} name The name of selected author.
 */
function selectedAuthor(name) {
    $("#author-input").val(name.text);
}

// ---------------------------------------------------------------------------------------------------------------------
/**
 * Specifies the input button, when file is selected.
 */
$(document).ready(function() {
    $('#upload-book').on('change', function(event) {
        var txt = $(this).val().split('\\').pop();

        if (txt.length > 30) {
            txt = txt.substring(0, 30) + '...'
        }
        if (!txt) txt = 'Загрузить книгу';

        $('#upload-caption').text(txt);
    });

    $('form').on('submit', function(event) {
        event.preventDefault();

        var upload_book = $("#upload-book");

        $("#invalid-book").hide();

        if (upload_book.val()) {
            $("#missing-book-warn").css("display", "none");
            $("#file-uploading").css("display", "block");

            var formData = new FormData($(this)[0]);
            var file = upload_book[0].files[0];

            formData.set('bookfile', file, Date.now() + '.' + file.name.split('.').pop());

            $.ajax({
                url: $('form').attr('action'),
                type: 'POST',
                data: formData,
                async: true,
                cache: false,
                contentType: false,
                processData: false,

                success: function(response) {
                    window.location.href = response;
                },

                error: function(jqXHR, errorThrown) {
                    alert(
                        'Вы попытались загрузить не PDF/FB2 файл\n' +
                        'или он поврежден. Попробуйте другой файл.'
                    );
                    $("#file-uploading").css("display", "none");
                }
            });
        }

        else {
            $("#missing-book-warn").css("display", "block");
        }
    });
});

