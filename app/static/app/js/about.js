// ---------------------------------------------------------------------------------------------------------------------
/**
 * Sends message to moderators.
 */
function sendMessage() {
    $.ajax({
        url: 'send-message',
        type: 'POST',
        data: {
            mailer: $('#mailer').val(),
            text: $('#message-text').val(),
            csrfmiddlewaretoken: getCookie('csrftoken')
        },

        success: function(response) {
            console.log(response);
        }
    });
}
