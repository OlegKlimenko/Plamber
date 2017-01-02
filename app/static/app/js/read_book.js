// Constants.
var PDF_DOCUMENT;
var SCALE = 1;
var PAGE_RENDERING = false;
var PAGE_NUM_PENDING = null;

// Page outputting.
var DESIRED_HEIGHT = 1250;
var HEADER_MARGIN = 130;
var PAGE_SEPARATOR = 6;

// Page navigating.
var PREVIOUS_PAGE = 0;
var LAST_PAGE = 0;

var PAGES_TO_CLEAR = [];

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
        var scale = DESIRED_HEIGHT / viewPort.height;
        var scaledViewport = page.getViewport(scale);

        var canvas = document.getElementById("page" + pageNumber);
        var context = canvas.getContext("2d");

        canvas.height = scaledViewport.height;
        canvas.width = scaledViewport.width;

        var renderContext = {
            canvasContext: context,
            viewport: scaledViewport
        };

        page.render(renderContext);
    });
}

// ---------------------------------------------------------------------------------------------------------------------
/**
 * If another page rendering in progress, waits until the rendering is
 * finished. Otherwise, executes rendering immediately.
 *
 * @param {number} pageNum The number of a page.
 */
function queueRenderPage(pageNum) {
    if (PAGE_RENDERING) {
        PAGE_NUM_PENDING = pageNum;
    } else {
        renderPage(PDF_DOCUMENT, pageNum);
    }
}

// ---------------------------------------------------------------------------------------------------------------------
/**
 * Clears the canvas elements which is not used.
 */
function clearPages() {
    if (PAGES_TO_CLEAR.length != 0) {
        for (var page = 0; page < PAGES_TO_CLEAR.length; page++) {
            var canvas;
            canvas = $('#page' + PAGES_TO_CLEAR[page])[0];
            canvas.getContext('2d').clearRect(0, 0, canvas.width, canvas.height);
        }
        PAGES_TO_CLEAR = [];
    }
}

// ---------------------------------------------------------------------------------------------------------------------
/**
 * Renders the pages.
 *
 * @param {number} pageNum The number of a page.
 */
function renderPages(pageNum) {
    clearPages();

    if (pageNum > 1) {
        queueRenderPage(pageNum - 1);
        PAGES_TO_CLEAR.push(pageNum - 1);
    }
    if (pageNum < PDF_DOCUMENT.numPages)  {
        queueRenderPage(pageNum + 1);
        PAGES_TO_CLEAR.push(pageNum + 1);
    }

    queueRenderPage(pageNum);
    PAGES_TO_CLEAR.push(pageNum);
}
// ---------------------------------------------------------------------------------------------------------------------
/**
 * Sends ajax request for changing information about current readed page of each page of each user.
 *
 * @param {number} pageNum The number of a page.
 */
function setCurrentPage(pageNum) {
    $('#page-number').val(pageNum);

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
    var offset = $('#page' + pageNum).offset().top;
    $(document).scrollTop(offset - HEADER_MARGIN);
}

// ---------------------------------------------------------------------------------------------------------------------
/**
 * Sets the prev page values.
 */
function prevPage() {
    var prevPageValue = parseInt($('#page-number').val()) - 1;

    if (prevPageValue > 1) {
        setCurrentPage(prevPageValue);
        setOffset(prevPageValue);
    }
}

// ---------------------------------------------------------------------------------------------------------------------
/**
 * Sets the next page values.
 */
function nextPage() {
    var nextPageValue = parseInt($('#page-number').val()) + 1;

    if (nextPageValue < PDF_DOCUMENT.numPages) {
        setCurrentPage(nextPageValue);
        setOffset(nextPageValue);
    }
}

// ---------------------------------------------------------------------------------------------------------------------
/**
 * Set values and renders page after loading the page.
 *
 * @param {number} pageNum The number of a page.
 */
function loadPage(pageNum) {
    $('#page-number').val(pageNum);

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
    document_scroll = $(document).scrollTop();

    PREVIOUS_PAGE = parseInt((document_scroll + HEADER_MARGIN) / DESIRED_HEIGHT);
    current_page = parseInt((document_scroll + HEADER_MARGIN - PAGE_SEPARATOR * PREVIOUS_PAGE) / DESIRED_HEIGHT) + 1;

    if (LAST_PAGE != current_page) {
        LAST_PAGE = current_page;
        setCurrentPage(current_page);
        renderPages(parseInt(current_page));
    }

});

// ---------------------------------------------------------------------------------------------------------------------
/**
 * Sets settings for open PDF document; opens document and generates starting point elements.
 */
$(document).ready(function() {
    var url = $("#book-url").text();
    var pageNum = $('#current-page').text();

    PDFJS.workerSrc = "/static/app/js/third_party/pdf_js/pdf.worker.js";

    PDFJS.getDocument(url).then(function (pdf) {
        PDF_DOCUMENT = pdf;

        for (var currentPage = 1; currentPage < pdf.numPages + 1; currentPage++) {
            $('#main-area').append('<canvas class="the-page" id="page' + currentPage + '" height="1250" width="800">');
        }
        loadPage(pageNum);
    });
});

