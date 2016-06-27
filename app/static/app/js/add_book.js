// ---------------------------------------------------------------------------------------------------------------------
/**
 * Inserts authors in HTML document, depending on count of authors.
 *
 * @param {Object} authors The list of authors.
 */
function insertAuthors(authors) {
    if (authors.length > 0) {
        $("#divAuthorsList").css("display", "block");
        $("#divAuthorsListHeader").css("display", "block");
        $("#divAuthorsList").empty();

        for (var author = 0; author < authors.length; author++) {
            $("#divAuthorsList").append("<div align='left'>" +
                                        "<a class='reference' onclick='selectedAuthor(this)'>" +
                                        authors[author] + "</a></div>");
        }
    }
    else {
        $("#divAuthorsListHeader").css("display", "none");
        $("#divAuthorsList").empty();
    }
}

// ---------------------------------------------------------------------------------------------------------------------
/**
 * Creates Ajax request for generating author list.
 */
function generateAuthors() {
    if ($("#authorInput").val() !== "") {
        $.ajax({
            url: "generate-authors",
            type: "GET",
            data: {authorPart: $("#authorInput").val()},

            success: function(authors) {
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
    $("#authorInput").val(name.text);
}

// ---------------------------------------------------------------------------------------------------------------------
/**
 * Checks if book is chosen. Generates HTML elements depending this check.
 *
 * @param {Object} event
 */
function isBookChosen(event) {
    if ($("#uploadBook").val()) {
        $("#missingBookWarn").css("display", "none");
        $("#fileUploading").css("display", "block");
        event.submit();
    }
    else {
        $("#missingBookWarn").css("display", "block");
    }
}