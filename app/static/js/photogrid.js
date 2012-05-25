$(document).ready(function(){
    $(".photo-container").each(function() {
        set_photo_click_handler($(this));
    })
});

function set_photo_click_handler(el) {
    el.hover(function() {
        $(this).find(".photo-caption").show();
    }, function() {
        $(this).find(".photo-caption").hide();
    })
}

var is_loading = false;
// `photos_per_page` is set in the template

function load_photos(featured, cur_tag, cur_set) {
    if (is_loading) {
        console.log("Already loading.");
        return;
    }

    // Toggle loading ui state
    is_loading = true;
    $("#photo-container-more .default").hide();
    $("#photo-container-more .loading").show();

    // Build arguments
    var args = {
        n: photos_per_page,
        last: photogrid_last_hash
    };
    if (featured) args["featured"] = 1;
    if (cur_tag) args["tag"] = cur_tag;
    if (cur_set) args["set"] = cur_set;

    // Make ajax request
    $.get("/ajax/photo/more",  args, function(data) {
        d = JSON.parse(data);
        photogrid_last_hash = d.last;

        for (var i=0; i<d.photos.length; i++) {
            item = $(d.photos[i]);
            item.insertBefore("#photo-container-more");
            set_photo_click_handler(item);
        }

        if (d.has_more) {
            $("#photo-container-more .default").show();
            $("#photo-container-more .loading").hide();
        } else {
            $("#photo-container-more").hide();
        }

        is_loading = false;
    })
}
