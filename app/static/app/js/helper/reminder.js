$(document).ready(function(e) {
    if (reminder != 'false') {
        showReminder(reminder);
    }
});

function showReminder(reminder_id) {
    $('#' + reminder_id).css('display', 'block');
    $('#reminder-background').css('display', 'block');
}

function hideReminder(reminder_id) {
    $('#' + reminder_id).css('display', 'none');
    $('#reminder-background').css('display', 'none');
}

function updateReminder(field, value) {
    $.ajax({
        url: 'update-reminder',
        type: 'POST',
        data: {
            field: field,
            value: value,
            csrfmiddlewaretoken: getCookie("csrftoken")
        }
    });
}
