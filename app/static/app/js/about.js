/**
 * Sends message to moderators.
 */
function sendMessage() {
    var mail_input = $('#user-email');
    var text_input = $('#message-text');

    if (!mail_input.val() || !text_input.val()) {
        showToast('Пожалуйста, заполните все поля формы.');
    }
    else {
        $.ajax({
            url: 'send-message',
            type: 'POST',
            data: {
                email: mail_input.val(),
                text: text_input.val(),
                csrfmiddlewaretoken: getCookie('csrftoken')
            },

            success: function(response) {
                showToast('Спасибо за ваше сообщение!\n' +
                          'Сообщение успешно отправлено!\n');
                clearInputs();
            },

            error: function(jqXHR, errorThrown) {
                errorHandler(jqXHR, errorThrown);
            }
        });
    }
}

// ---------------------------------------------------------------------------------------------------------------------
function clearInputs() {
    $('#user-email').val('');
    $('#message-text').val('');
}

// ---------------------------------------------------------------------------------------------------------------------
/**
 * Outputs an error message depending to response of the server.
 */
function errorHandler(jqXHR, errorThrown) {
    var msg;

    if (jqXHR.status === 0) {
        msg = 'Не удалось соединиться с сервером...\nПроверьте подключение к интернету.';
    } else if (jqXHR.status === 400) {
        msg = 'Вы ввели некорректный email.\nВведите снова и попробуйте еще раз.'
    } else if (jqXHR.status === 500) {
        msg = 'Произошла внутренняя ошибка сервера. Попробуйте еще раз или свяжитесь с нами.';
    }

    showToast(msg);
}

// ---------------------------------------------------------------------------------------------------------------------
/**
 * Outputs toast with message passed in param.
 */
function showToast(msg) {
    var toast_elem = $('#error-toast');

    toast_elem.text(msg);
    toast_elem.fadeIn(400).delay(10000).fadeOut(400);
}
