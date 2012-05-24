$(document).ready(function(){
    $(".photo-container").each(function() {
        $(this).hover(function() {
            $(this).find(".photo-caption").show();
        }, function() {
            $(this).find(".photo-caption").hide();
        })
    })
});
