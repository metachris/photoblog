function send_message() {
    var input_names = new Array("csrfmiddlewaretoken", "name", "email", "message");
    var checkbox_names = new Array("add_to_list");
    var vars = {}
    for (el in input_names) {
        vars[input_names[el]] = $("#contactModal [name=" + input_names[el] + "]").val();
    }
    for (el in checkbox_names) {
        vars[checkbox_names[el]] = $("#contactModal [name=" + checkbox_names[el] + "]").is(":checked");
    }
    console.log(vars);
}

function hide_contact_modal() {
    $("#contactModal").modal("hide");
}
