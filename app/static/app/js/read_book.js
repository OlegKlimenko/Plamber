// Constants.
var PDF_DOCUMENT;
var SCALE = 1;

// Page outputting.
var DESIRED_WIDTH;
var DESIRED_HEIGHT;
var HEADER_MARGIN = 100;
var PAGES_TO_RENDER = [];

// Page navigating.
var TOTAL_HEIGHT = 0;
var CURRENT_PAGE = 1;
var PREVIOUS_OFFSET = 0;
var CURRENT_OFFSET = 0;
var NEXT_OFFSET = 0;

// Reload data.
var RELOAD = false;
var SIZE_LINE = 720;

// ---------------------------------------------------------------------------------------------------------------------
/**
 * Renders the page of the PDF document.
 *
 * @param {Object} pdf        The instance of the pdf document.
 * @param {number} pageNumber The number of a page which we need to render.
 */
function renderPage(pdf, pageNumber) {
    pdf.getPage(pageNumber).then(function (page) {
        var viewPort = page.getViewport(SCALE);
        var scale = DESIRED_WIDTH / viewPort.width;
        var scaledViewport = page.getViewport(scale);

        var canvas = document.getElementById("page" + pageNumber);
        var context = canvas.getContext("2d");

        var devicePixelRatio = window.devicePixelRatio || 1;
        var backingStoreRatio = context.webkitBackingStorePixelRatio ||
                                context.mozBackingStorePixelRatio ||
                                context.msBackingStorePixelRatio ||
                                context.oBackingStorePixelRatio ||
                                context.backingStorePixelRatio || 1;

        var ratio = devicePixelRatio / backingStoreRatio;

        if (devicePixelRatio !== backingStoreRatio) {
            var oldWidth = scaledViewport.width;
            var oldHeight = scaledViewport.height;

            canvas.width = oldWidth * ratio;
            canvas.height = oldHeight * ratio;

            canvas.style.width = oldWidth + 'px';
            canvas.style.height = oldHeight + 'px';

            context.scale(ratio, ratio);
        }

        var renderContext = {
            canvasContext: context,
            viewport: scaledViewport
        };

        page.render(renderContext).then(function() {
            renderPage(PDF_DOCUMENT, PAGES_TO_RENDER.pop());
            loadHide();
        })
    });
}

// ---------------------------------------------------------------------------------------------------------------------
/**
 * Renders the pages.
 *
 * @param {number} pageNum The number of a page.
 */
function renderPages(pageNum) {
    PAGES_TO_RENDER.push(CURRENT_PAGE + 1);
    renderPage(PDF_DOCUMENT, pageNum);
}

// ---------------------------------------------------------------------------------------------------------------------
/**
 * Sends ajax request for changing information about current readed page of each page of each user.
 *
 * @param {number} pageNum The number of a page.
 */
function setCurrentPage(pageNum) {
    $('.page-number').val(pageNum);
    $('#current-page').text(pageNum);

    $.ajax({
        url: "set-current-page",
        type: "POST",
        data: {page: pageNum,
               book: $("#book-id").text(),
               csrfmiddlewaretoken: getCookie("csrftoken")},

        success: function result(json) {}
    });
}

// ---------------------------------------------------------------------------------------------------------------------
/**
 * Sets the page offset depending on pixels of selected page.
 *
 * @param {number} pageNum The number of a page.
 */
function setOffset(pageNum) {
    PREVIOUS_OFFSET = $('#page' + (parseInt(pageNum) - 1)).offset().top;
    CURRENT_OFFSET = $('#page' + pageNum).offset().top;
    NEXT_OFFSET = $('#page' + (parseInt(pageNum) + 1)).offset().top;

    CURRENT_PAGE = parseInt(pageNum);
    renderPages(CURRENT_PAGE);
    $(document).scrollTop(CURRENT_OFFSET - HEADER_MARGIN);
}

// ---------------------------------------------------------------------------------------------------------------------
/**
 * Set values and renders page after loading the page.
 *
 * @param {number} pageNum The number of a page.
 */
function loadPage(pageNum) {
    $('.page-number').val(pageNum);

    if (pageNum != 1) {
        setOffset(pageNum);
    }
    else {
        renderPages(parseInt(pageNum));
    }
}

// ---------------------------------------------------------------------------------------------------------------------
/**
 * Renders pages when page was scrolled.
 */
$(document).scroll(function() {
    if (RELOAD) {
        RELOAD = false;
    }
    else {
        var document_scroll = $(document).scrollTop();

        if (document_scroll + HEADER_MARGIN > NEXT_OFFSET) {
            CURRENT_PAGE += 1;
            updateOffsets();
        }

        else if (document_scroll + HEADER_MARGIN < PREVIOUS_OFFSET + DESIRED_HEIGHT) {
            CURRENT_PAGE -= 1;
            updateOffsets();
        }
    }
});

// ---------------------------------------------------------------------------------------------------------------------
/**
 * Updates offsets info for further calculations.
 */
function updateOffsets() {
    NEXT_OFFSET = $('#page' + (parseInt(CURRENT_PAGE) + 1)).offset().top;
    PREVIOUS_OFFSET = $('#page' + (parseInt(CURRENT_PAGE) - 1)).offset().top;

    setCurrentPage(CURRENT_PAGE);
    renderPages(CURRENT_PAGE);
}

// ---------------------------------------------------------------------------------------------------------------------
/**
 * Sets settings for open PDF document; opens document and generates starting point elements.
 */
function loadPages() {
    var url = $("#book-url").text();

    PDFJS.workerSrc = "/static/app/js/third_party/pdf_js/pdf.worker.js";

    PDFJS.getDocument(url).then(function (pdf) {
        PDF_DOCUMENT = pdf;

        DESIRED_WIDTH = $('#container-width').width();

        $('#main').empty();
        TOTAL_HEIGHT = 0;

        calculateHeight(PDF_DOCUMENT, 1);
    });
}

// ---------------------------------------------------------------------------------------------------------------------
/**
 * Calculates the height for page size, generates canvases, and start loading pages.
 *
 * @param {object} pdf         The PDF document instance.
 * @param {number} currentPage The number of the page which must be rendered.
 */
function calculateHeight(pdf, currentPage) {
    pdf.getPage(parseInt(currentPage)).then(function(page) {
        var viewPort = page.getViewport(SCALE);
        var scale = DESIRED_WIDTH / viewPort.width;
        var scaledViewport = page.getViewport(scale);

        TOTAL_HEIGHT += scaledViewport.height;

        if (currentPage >= pdf.numPages) {
            DESIRED_HEIGHT = TOTAL_HEIGHT / pdf.numPages;

            for (var thePage = 1; thePage < pdf.numPages + 1; thePage++) {
                $('#main').append('<canvas class="the-page" id="page' + thePage +
                    '" width="' + DESIRED_WIDTH + '" height="' + DESIRED_HEIGHT + '">');
            }

            loadPage($('#current-page').text());
        }
        else {
            calculateHeight(pdf, currentPage + 1);
        }
    });
}

// ---------------------------------------------------------------------------------------------------------------------
/**
 * Replaces navigate panel to different places depending on display width.
 */
function navigatePanel() {
    if ($('#container-width').width() < SIZE_LINE) {
        $('#small-page-num').css('display', 'block');
        $('#page-nav-bar').css('display', 'none');
    }
    else {
        $('#small-page-num').css('display', 'none');
        $('#page-nav-bar').css('display', 'block');
    }
}

// ---------------------------------------------------------------------------------------------------------------------
/**
 * Load pages when the document is ready.
 */
$(document).ready(function() {
    loadDisplay();
    loadPages();
    navigatePanel();
});

// ---------------------------------------------------------------------------------------------------------------------
/**
 * Reload pages when the screen size is changed.
 */
window.addEventListener("resize", function() {
    if (DESIRED_WIDTH != $('#container-width').width()) {
        loadDisplay();
        navigatePanel();
        loadPages();
        RELOAD = true;
    }
});

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
