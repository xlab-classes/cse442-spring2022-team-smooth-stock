$(document).ready(function() {
    var newsTableBody = document.getElementById('news-table').getElementsByTagName('tbody')[0];    
    var metaRow = newsTableBody.insertRow();
    var newCell = metaRow.insertCell();
    var newText = document.createTextNode('Meta');
    newCell.append(newText);
    let tickerCell = metaRow.insertCell().append(document.createTextNode('META'));


    $('button').click(function(event) {
        //let urlCall = "./run?query=" + escape(view_query)
        $.get("./createaccount", function(){
            $.ajax({
                url: '/createaccount',
                type: 'POST',
                success: function(response){
                    console.log(response);
                },
                error: function(error){
                    console.log(error);
                }
            })
        });
    });
})