$(document).ready(function() {
    
    $("button").click(function() {
        var t = $(this).attr('btn_id');
        $("tr."+t).toggle();
    })
})