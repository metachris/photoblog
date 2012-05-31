$(document).ready(function(){
    $("#photo-main").click(function() {
        // Full screen capable browsers get full screen
        try {
            toggle_fullscreen();
        } catch (err) {
            $("#overlay").toggle();
        }
    });

    $("#overlay").click(function() {
        $(this).toggle();
    });
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

function toggle_fullscreen() {
    var e = document.getElementById("photo-main-frame");
    if (runPrefixMethod(document, "FullScreen") || runPrefixMethod(document, "IsFullScreen")) {
        runPrefixMethod(document, "CancelFullScreen");
    } else {
        runPrefixMethod(e, "RequestFullScreen");
    }
}
