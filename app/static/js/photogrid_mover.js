function sortable() {
    $( ".photo-grid" ).sortable({
        update: function(event, ui) {
            console.log(event);
            console.log(ui);
            console.log(ui.position);
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
