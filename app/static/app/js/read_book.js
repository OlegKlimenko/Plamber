// Constants
var PDF_DOCUMENT;
var SCALE = 1.5;
var PAGE_RENDERING = false;
var PAGE_NUM_PENDING = null;

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

        var canvas = document.getElementById("the-canvas");
        var context = canvas.getContext("2d");
        canvas.height = viewPort.height;
        canvas.width = viewPort.width;

        var renderContext = {
            canvasContext: context,
            viewport: viewPort
        };

        page.render(renderContext);
    });
}

// ---------------------------------------------------------------------------------------------------------------------
/**
 * If another page rendering in progress, waits until the rendering is
 * finised. Otherwise, executes rendering immediately.
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
 * Sends ajax request for changing information about current readed page of each page of each user.
 *
 * @param string pageNum The number of a page.
 */
function setCurrentPage(pageNum) {
    $.ajax({
        url: "set-current-page",
        type: "POST",
        data: {page: pageNum,
               book: $("#book_name").text(),
               csrfmiddlewaretoken: getCookie("csrftoken")},

        success: function result(json) {}
    });
}

// ---------------------------------------------------------------------------------------------------------------------
/**
 * Flips to the previous page of the PDF document and reset data to information of current page.
 */
function prevPage() {
    var pageNum = $("#current_page").text();

    if (pageNum <= 1) {
        return;
    }

    pageNum--;
    queueRenderPage(pageNum);

    $("#current_page").text(pageNum);
    setCurrentPage(pageNum);
}

// ---------------------------------------------------------------------------------------------------------------------
/**
 * Flips to the next page of the PDF document and reset data to information of current page.
 */
function nextPage() {
    var pageNum = $("#current_page").text();

    if (pageNum >= PDF_DOCUMENT.numPages) {
        return;
    }
    pageNum++;
    queueRenderPage(pageNum);

    $("#current_page").text(pageNum);
    setCurrentPage(pageNum);
}

// ---------------------------------------------------------------------------------------------------------------------
/**
 * Sets settings for open PDF document; opens document when page is loaded.
 */
$(document).ready(function() {
    var url = $("#book_url").text();
    var pageNum = Number($("#current_page").text());

    PDFJS.workerSrc = "/static/app/js/third_party/pdf_js/pdf.worker.js";

    PDFJS.getDocument(url).then(function (pdf) {
        PDF_DOCUMENT = pdf;

        renderPage(pdf, pageNum);

        document.getElementById("prev").addEventListener("click", prevPage);
        document.getElementById("next").addEventListener("click", nextPage);
    });
});
