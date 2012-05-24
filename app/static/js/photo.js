$(document).ready(function(){
    $("#photo-main").click(function() {
        $("#overlay").toggle();
    });
    $("#overlay").click(function() {
        $(this).toggle();
    });
});
