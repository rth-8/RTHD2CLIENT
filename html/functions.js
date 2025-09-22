function doRefresh(idx) {
    list = document.getElementById("refresh_button_img").classList;
    if (list.contains("refresh_spin")) {
        //nothing
    }
    else {
        list.remove("refresh_static");
        list.add("refresh_spin");
        // window.location.href = "about:blank?refresh="+idx;
    }
}

function toProfile() {
    window.location.href = "about:blank?profile";
}
