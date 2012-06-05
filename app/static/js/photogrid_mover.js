// Array of moves in form of <hash>_<hash_next_item>
var moves = new Array();

$(function() {
    // Make the photo grid sortable
    $( ".photo-grid" ).disableSelection();
    $( ".photo-grid" ).sortable({
        stop: function(event, ui) {
            item_moved(ui.item.index());
        }

    });
});

window.onMorePhotosLoaded = function() {
    // After more photos have loaded, we need to make them sortable
    $( ".photo-grid" ).sortable("refresh");
};

function item_moved(new_pos) {
    var item = $(".photo-container:eq(" + new_pos + ")");
    var item_next = $(".photo-container:eq(" + new_pos + ")").next();
//    item.css("border", "1px solid red");
//    item_next.css("border", "1px solid green");

    hash_orig = item.attr("id").substr(2);
    hash_nextitem = item_next.attr("id").substr(2);
    moves.push(hash_orig + "_" + hash_nextitem);
}

function save() {
    $.get("/ajax/admin/photo-move/", { "moves": moves.join("|") }, function(data) {
        alert("saved");
    });
}
