function showRow(rowId) {
    document.getElementById(rowId).style.display = "";
}
function hideRow(rowId) {
    document.getElementById(rowId).style.display = "none";
}

function toggleRow(rowId) {
    if (document.getElementById(rowId).style.display == "") {
        document.getElementById(rowId).style.display = "none";
    }
    else if (document.getElementById(rowId).style.display == "none") {
        document.getElementById(rowId).style.display = "";
    }
    else {
        console.log("ERROR: toggle style.display is not empty or none");
    }
}

$(document).ready(function() {
    
    $("button").click(function() {
        var t = $(this).attr('btn_id');
        toggleRow(t);
        console.log(t);
    })
})