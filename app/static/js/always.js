/**
 * This script file is loaded on every page.
 * Currently only contact form handling.
 */
var is_sending = false;
function send_message() {
    if (is_sending) return;
    is_sending = true;

    // Adjust UI
    $("#contactModal-form").hide();
    $("#contactModal-loading").show();
    $("#contactModal-btn-submit").addClass("disabled");

    // Collect data
    var input_names = new Array("csrfmiddlewaretoken", "name", "email", "message");
    var checkbox_names = new Array("add_to_list");
    var vars = {}
    for (el in input_names) {
        vars[input_names[el]] = $("#contactModal [name=" + input_names[el] + "]").val();
    }
    for (el in checkbox_names) {
        vars[checkbox_names[el]] = $("#contactModal [name=" + checkbox_names[el] + "]").is(":checked");
    }

    // Perform ajax request
    var req = $.ajax({
        url: "/ajax/contact/",
        type: "POST",
        data: vars,
        success: function(data) {
            if (data == "1") {
                $("#contactModal-loading").hide();
                $("#contactModal-success").show();
            } else {
                // handle errors
                for (el in input_names) {
                    if (data.indexOf(input_names[el]) != -1) {
                        $("#contactModal #ctrlgrp-" + input_names[el]).addClass("error");
                    } else {
                        $("#contactModal #ctrlgrp-" + input_names[el]).removeClass("error");
                    }
                }

                is_sending = false;  // enabled re-sending
                $("#contactModal-loading").hide();
                $("#contactModal-form").show();
                $("#contactModal-btn-submit").removeClass("disabled");
            }
        },
        error: function(data) {
            is_sending = false;  // enabled re-sending
            $("#contactModal-loading").hide();
            $("#contactModal-form").show();
            $("#contactModal-btn-submit").removeClass("disabled");
            alert("An error occurred. Please try again now or a bit later.")
        }
    });
}

function hide_contact_modal() {
    $("#contactModal").modal("hide");
}
