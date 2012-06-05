function on_fullscreen_change(is_fullscreen) {
    console.log("Full screen state change to " + is_fullscreen);
    if (is_fullscreen) {
        $("#photo-main-container").removeClass("normal");
    } else {
        $("#photo-main-container").removeClass("fullscreen");
        $("#photo-main-container").addClass("normal");
    }
}

$(document).ready(function(){
    $("#photo-main-container img").click(function() {
        try {
            // Toggle full screen in capable browsers
            var e = document.getElementById("photo-main-container");
            if (runPrefixMethod(document, "FullScreen") || runPrefixMethod(document, "IsFullScreen")) {
                runPrefixMethod(document, "CancelFullScreen");
            } else {
                $("#photo-main-container").addClass("fullscreen");
                runPrefixMethod(e, "RequestFullScreen");
            }
        } catch (err) {
            // Fallback on non-html5 capable browsers
            $("#overlay").toggle();
        }
    });

    $("#overlay").click(function() {
        $(this).toggle();
    });

    // Add full screen event listeners to set css accordingly
    document.addEventListener("fullscreenchange", function () {
        on_fullscreen_change(document.fullscreen);
    }, false);

    document.addEventListener("mozfullscreenchange", function () {
        on_fullscreen_change(document.mozFullScreen);
    }, false);

    document.addEventListener("webkitfullscreenchange", function () {
        on_fullscreen_change(document.webkitIsFullScreen);
    }, false);
});

// Full-screen prefix detector (via http://www.sitepoint.com/html5-full-screen-api)
function runPrefixMethod(obj, method) {
    var pfx = ["webkit", "moz", "ms", "o", ""];
    var p = 0, m, t;
    while (p < pfx.length && !obj[m]) {
        m = method;
        if (pfx[p] == "") {
            m = m.substr(0,1).toLowerCase() + m.substr(1);
        }
        m = pfx[p] + m;
        t = typeof obj[m];
        if (t != "undefined") {
            pfx = [pfx[p]];
            return (t == "function" ? obj[m]() : obj[m]);
        }
        p++;
    }
}

