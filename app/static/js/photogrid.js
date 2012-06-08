/**
 * Helper for photo-grid and photo-flow.
 *
 * - Ajax load more pages
 * - Set image hover handler
 */

//COOKIE_NAME_GRIDPAGE = "lastGridPage";

var el_win = $(window);
var el_doc = $(document);

// var scroll_load_more_enabled ... set in photogrid.html
var scroll_enabled = true; // to disable temporarily. only works if scroll_load_more_enabled is true.

$(document).ready(function(){
    // Set hover handler
    $(".photo-container").each(function() {
        set_photo_hover_handler($(this));
    });

    // Set scroll handler
    if (scroll_load_more_enabled) {
        el_win.scroll(function() {
            check_scroll_bottom();
        });
        check_scroll_bottom();
    }

    // If user comes back from an image after loading more, auto-load more
//    var grid_page_last = getCookie(COOKIE_NAME_GRIDPAGE);
//    if (grid_page_last) {
//        console.log("--- skip to page " + grid_page_last);
//    }
//    setCookie(COOKIE_NAME_GRIDPAGE, "", 30);
});


// Scroll helper
function check_scroll_bottom() {
    if (scroll_enabled) {
        if (el_win.scrollTop() >= el_doc.height() - el_win.height() - 180) {
            load_photos();
        }
    }
}

// Photo hover handler
function set_photo_hover_handler(el) {
    // Update hover mechanism for all photos (at start and after loading another page)
    el.hover(function() {
        $(this).find(".photo-caption").show();
    }, function() {
        $(this).find(".photo-caption").hide();
    })
}

// Stuff for loading more pages
var is_loading = false;
var page = 0;
var last_response;

// Stack of photos to fade in
var photos_to_add = new Array();

function load_photos() {
    if (is_loading) {
//        console.log("Already loading.");
        return;
    }

    if (last_response && !last_response.has_more) {
//        console.log("No more available");
        return;
    }

    // Toggle loading ui state
    is_loading = true;

    $("#photo-container-more .default").hide();
    $("#photo-container-more .loading").show();

    if (mode_flow) {
        load_photos_flow();
    } else {
        load_photos_grid();
    }
}

function load_photos_grid() {
    // Make ajax request
    $.get("/ajax/photo/more/", photogrid_info, function(data) {
        d = JSON.parse(data);
        photogrid_info["last_hash"] = d.last_hash;

        // Add the hidden photos to the DOM
        for (var i=0; i<d.photos.length; i++) {
            var photo = $(d.photos[i]);
            photo.hide();
            photo.insertBefore("#photo-container-more");
            photos_to_add.push(photo);
        }

        // Show new photos (fade in)
        $("#photo-container-more").fadeOut("normal", function() {
            // When container is faded out, start showing images
            $("#photo-container-more .default").show();
            $("#photo-container-more .loading").hide();
            show_new_photos();
        });

        // If not more, hide 'more' element
        if (!d.has_more) {
            $("#photo-container-more").fadeOut();
        }

        // If callbacks are registered, call now
        if (window.onMorePhotosLoaded) {
            window.onMorePhotosLoaded();
        }

        page++;
        last_response = d;

//        setCookie(COOKIE_NAME_GRIDPAGE, page, 30);
    })
}

function load_photos_flow() {
    args = photogrid_info;
    args["type"] = "flow";
    args["page"] = page;

    // Make ajax request
    $.get("/ajax/photo/more/", args, function(data) {
        d = JSON.parse(data);
        photogrid_info["last_hash"] = d.last_hash;

        page++;
        last_response = d;

        // Build the HTML block, hide all images and add them to the fade-in array
        block = $(d.html);
        block.find("img").each(function() {
            $(this).hide();
            photos_to_add.push($(this));
        });

        // Fade out more-container and start show-image sequence
        $("#photo-container-more").fadeOut("normal", function() {
            // When container is faded out, start showing images
            block.insertBefore("#end-of-flow");
            $("#photo-container-more .default").show();
            $("#photo-container-more .loading").hide();
            show_new_photos();
        });

        // Hide more-container if no more images
        if (!last_response.has_more) {
            $("#photo-container-more").fadeOut();
        }

        // If callbacks are registered, call now
        if (window.onMorePhotosLoaded) {
            window.onMorePhotosLoaded();
        }
    });
}

function show_new_photos() {
    // Fade in one photo after another
    photo = photos_to_add.shift();
    if (photo) {
        set_photo_hover_handler(photo);
        photo.fadeIn("normal", function() {
            show_new_photos();
        });
    } else {
        is_loading = false;
        if (last_response && last_response.has_more) {
            $("#photo-container-more").fadeIn();
            el_win.scroll();
        }
    }
}

//function setCookie(cookie_name, value, min_valid) {
//    var base_date = new Date(), expiry_date = new Date(base_date);
//    expiry_date.setMinutes(base_date.getMinutes() + min_valid);
//
//    var c_value=escape(value) + ((expiry_date==null) ? "" : "; expires="+expiry_date.toUTCString());
//    document.cookie=cookie_name + "=" + c_value;
//}
//
//function getCookie(cookie_name) {
//    var i,x,y,ARRcookies=document.cookie.split(";");
//    for (i=0;i<ARRcookies.length;i++) {
//        x=ARRcookies[i].substr(0,ARRcookies[i].indexOf("="));
//        y=ARRcookies[i].substr(ARRcookies[i].indexOf("=")+1);
//        x=x.replace(/^\s+|\s+$/g,"");
//        if (x==cookie_name) {
//            return unescape(y);
//        }
//    }
//}
