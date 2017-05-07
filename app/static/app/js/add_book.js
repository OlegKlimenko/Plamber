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
    else {
        $("#div-authors-list-header").css("display", "none");
        $("#div-authors-list").empty();
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
 * Checks if book is chosen. Generates HTML elements depending this check.
 *
 * @param {Object} event
 */
function isBookChosen(event) {
    $("#invalid-book").hide();
    if ($("#upload-book").val()) {
        $("#missing-book-warn").css("display", "none");
        $("#file-uploading").css("display", "block");
        event.submit();
    }
    else {
        $("#missing-book-warn").css("display", "block");
    }
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
        $('#upload-caption').text(txt);
    });
});

