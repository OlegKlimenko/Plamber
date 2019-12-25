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

// Other.
var LAST_TOAST_SHOWN = new Date();
var TOAST_UPDATE_FREQ = -120000;   // 2 mins in milliseconds.

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
            if (PAGES_TO_RENDER.length) {
                renderPage(PDF_DOCUMENT, PAGES_TO_RENDER.pop());
            }
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
    var prevPageToRender = CURRENT_PAGE > 1 ? CURRENT_PAGE - 1 : null;
    var nextPageToRender = CURRENT_PAGE < PDF_DOCUMENT.numPages ? CURRENT_PAGE + 1 : null;

    if (prevPageToRender) PAGES_TO_RENDER.push(prevPageToRender);
    if (nextPageToRender) PAGES_TO_RENDER.push(nextPageToRender);
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

    if (!anonymousUser) {
        $.ajax({
            url: "set-current-page",
            type: "POST",
            data: {page: pageNum,
                   book: $("#book-id").text(),
                   csrfmiddlewaretoken: getCookie("csrftoken")},

            success: function result(json) {},

            error: function(jqXHR, errorThrown) {
                if (jqXHR.status === 0) {
                    var curDate = new Date();

                    if (LAST_TOAST_SHOWN - curDate < TOAST_UPDATE_FREQ) {
                        LAST_TOAST_SHOWN = curDate;
                        showToast("#error-toast", 1000);
                    }
                }
            }
        });
    }
}

// ---------------------------------------------------------------------------------------------------------------------
/**
 * Sets the page offset depending on pixels of selected page.
 *
 * @param {number} pageNum The number of a page.
 */
function setOffset(pageNum) {
    loadDisplay();
    PREVIOUS_OFFSET = pageNum > 1 ? $('#page' + (parseInt(pageNum) - 1)).offset().top : 0;
    CURRENT_OFFSET = $('#page' + pageNum).offset().top;
    NEXT_OFFSET = pageNum < (PDF_DOCUMENT.numPages - 1) ? $('#page' + (parseInt(pageNum) + 1)).offset().top : $('#page' + parseInt(pageNum)).offset().top;

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
 * Adjusts offset if document scroll passed multiple pages in one time for scroll down action.
 *
 * @param {number} documentScroll
 */
function scrollDownOffset(documentScroll) {
    var found_page = false;

    while (!found_page) {
        var page = $('#page' + CURRENT_PAGE)

        if (page.length) {
            var offset = page.offset().top;
        }
        else {
            CURRENT_PAGE -= 1;
            return;
        }

        if (offset <= documentScroll + HEADER_MARGIN) {
            CURRENT_PAGE += 1;
        }
        else {
            found_page = true;
        }
    }
    CURRENT_PAGE -= 1
}

// ---------------------------------------------------------------------------------------------------------------------
/**
 * Adjusts offset if document scroll passed multiple pages in one time for scroll up action.
 *
 * @param {number} documentScroll
 */
function scrollUpOffset(documentScroll) {
    while (true) {
        var offset = $('#page' + CURRENT_PAGE).offset().top;

        if (offset > documentScroll + HEADER_MARGIN) {
            CURRENT_PAGE -= 1;
        }
        else {
            return;
        }
    }
}

// ---------------------------------------------------------------------------------------------------------------------
/**
 * Renders pages when page was scrolled.
 */
$(document).scroll(function() {
    clearTimeout($.data(this, 'scrollTimer'));

    $.data(this, 'scrollTimer', setTimeout(function() {
        if (RELOAD) {
            RELOAD = false;
        }
        else {
            var documentScroll = $(document).scrollTop();

            if ((documentScroll + HEADER_MARGIN > NEXT_OFFSET) && (CURRENT_PAGE < PDF_DOCUMENT.numPages)) {
                scrollDownOffset(documentScroll);
                updateOffsets();
            }

            else if ((documentScroll + HEADER_MARGIN < PREVIOUS_OFFSET + DESIRED_HEIGHT) && (CURRENT_PAGE > 1)) {
                scrollUpOffset(documentScroll);
                updateOffsets();
            }
        }
    }, 50));
});

// ---------------------------------------------------------------------------------------------------------------------
/**
 * Updates offsets info for further calculations.
 */
function updateOffsets() {
    var prevPage = CURRENT_PAGE > 1 ? CURRENT_PAGE - 1 : 1;
    var nextPage = CURRENT_PAGE < PDF_DOCUMENT.numPages ? CURRENT_PAGE + 1 : CURRENT_PAGE;

    PREVIOUS_OFFSET = $('#page' + prevPage).offset().top;
    NEXT_OFFSET = $('#page' + nextPage).offset().top;

    setCurrentPage(CURRENT_PAGE);
    renderPages(CURRENT_PAGE);
}

// ---------------------------------------------------------------------------------------------------------------------
function progressCallBack(progress) {
    $('#loading-percent').text(parseInt(100 * progress.loaded / progress.total) + '%');
}

// ---------------------------------------------------------------------------------------------------------------------
/**
 * Sets settings for open PDF document; opens document and generates starting point elements.
 */
function loadPages() {
    clearTimeout($.data(this, 'scrollTimer'));

    $.data(this, 'scrollTimer', setTimeout(function() {
        var url = $("#book-url").text();

        PDFJS.workerSrc = "/static/app/js/third_party/pdf_js/pdf.worker.js";

        PDFJS.getDocument(url, null, null, progressCallBack).then(function (pdf) {
            PDF_DOCUMENT = pdf;

            DESIRED_WIDTH = $('#container-width').width();

            $('#main').empty();
            TOTAL_HEIGHT = 0;

            calculateHeight(PDF_DOCUMENT, 1);
        });
    }, 50));
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
        $('#small-page-nav').css('display', 'block');
        $('#page-nav-bar').css('display', 'none');
    }
    else {
        $('#small-page-nav').css('display', 'none');
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

    if (anonymousUser) {
        showToast("#anonymous-user-toast", 5000);
    }
});

// ---------------------------------------------------------------------------------------------------------------------
/**
 * Shows toast with desired message.
 *
 * @param {string} attr  Element CSS selector to show.
 * @param {number} delay The milliseconds delay to show toast.
 */
function showToast(attr, delay) {
    var toastElement = $(attr);
    toastElement.fadeIn(400).delay(delay).fadeOut(400);
}


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
    $("#loading-percent").css('display', 'block');
}

// ---------------------------------------------------------------------------------------------------------------------
/**
 * Hides the loading spinner
 */
function loadHide() {
    $("#loading").css('display', 'none');
    $("#loading-percent").css('display', 'none');
}

// ---------------------------------------------------------------------------------------------------------------------
/**
 * Changes page to page in input of button on big screens.
 */
function goToPageBig() {
    var pageNum = $('#big-page-num').val();
    validateNumberAndChangePage(pageNum);
}

// ---------------------------------------------------------------------------------------------------------------------
/**
 * Changes page to page in input of button on small screens.
 */
function goToPageSmall() {
    var pageNum = $('#small-page-num').val();
    validateNumberAndChangePage(pageNum);
}
// ---------------------------------------------------------------------------------------------------------------------
/**
 * Validates the page number and changes page offset and current page.
 */
function validateNumberAndChangePage(pageNum) {
    if (pageNum > 0 && pageNum < PDF_DOCUMENT.numPages + 1) {
        setCurrentPage(pageNum);
        setOffset(pageNum);
    }
    else {
        alert('Нет такого номера страницы.\nВведите от 1 до ' + PDF_DOCUMENT.numPages);
    }
}