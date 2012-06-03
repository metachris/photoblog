$(document).ready(function(){
    $(".photo-container").each(function() {
        set_photo_hover_handler($(this));
    })
});

function set_photo_hover_handler(el) {
    el.hover(function() {
        $(this).find(".photo-caption").show();
    }, function() {
        $(this).find(".photo-caption").hide();
    })
}

var is_loading = false;

function load_photos() {
    if (is_loading) {
        console.log("Already loading.");
        return;
    }

    // Toggle loading ui state
    is_loading = true;
    $("#photo-container-more .default").hide();
    $("#photo-container-more .loading").show();

    // Build arguments
    console.log(photogrid_info);

    // Make ajax request
    $.get("/ajax/photo/more", photogrid_info, function(data) {
        console.log("More Photos 200");

        d = JSON.parse(data);
        photogrid_info["last_hash"] = d.last_hash;

        for (var i=0; i<d.photos.length; i++) {
            item = $(d.photos[i]);
            item.insertBefore("#photo-container-more");
            set_photo_hover_handler(item);
        }

        if (d.has_more) {
            $("#photo-container-more .default").show();
            $("#photo-container-more .loading").hide();
        } else {
            $("#photo-container-more").hide();
        }

        is_loading = false;
        if (window.onMorePhotosLoaded) {
            window.onMorePhotosLoaded();
        }
    })
}
