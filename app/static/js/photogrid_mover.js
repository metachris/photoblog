function sortable() {
    $( ".photo-list" ).sortable({
        update: function(event, ui) {
            console.log(event);
            console.log(ui);
            console.log(ui.position);
        }
    });
    $( ".photo-list" ).disableSelection();
}

$(document).ready(function(){
    $(function() {
        sortable();
    });
});

window.onMorePhotosLoaded = function() {
    $( ".photo-list" ).sortable("refresh");
    console.log("asd");
};
