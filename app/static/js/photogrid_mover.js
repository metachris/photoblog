function sortable() {
    $( ".photo-grid" ).sortable({
        stop: function(event, ui) {
            item_moved(ui.item.index());
        }

    });
    $( ".photo-grid" ).disableSelection();
}

$(document).ready(function(){
    $(function() {
        sortable();
    });
});

window.onMorePhotosLoaded = function() {
    $( ".photo-grid" ).sortable("refresh");
    console.log("asd");
};

var moves = new Array();
function item_moved(new_pos) {
    var item = $(".photo-container:eq(" + new_pos + ")");
    var item_next = $(".photo-container:eq(" + new_pos + ")").next();
    item.css("border", "1px solid red");
    item_next.css("border", "1px solid green");

    hash_orig = item.attr("id").substr(2);
    hash_nextitem = item_next.attr("id").substr(2);
    moves.push(hash_orig + "_" + hash_nextitem);
}

function save() {
    var args = {
        "moves": moves.join("|")
    }

    console.log(args);
    $.get("/ajax/admin/photo-move/", args, function(data) {
        alert("saved");
    });
}
