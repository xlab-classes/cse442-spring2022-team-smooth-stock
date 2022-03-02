$(document).ready(function() {
    var newsTableBody = document.getElementById('news-table').getElementsByTagName('tbody')[0];    
    var metaRow = newsTableBody.insertRow();
    var newCell = metaRow.insertCell();
    var newText = document.createTextNode('Meta');
    newCell.append(newText);
    let tickerCell = metaRow.insertCell().append(document.createTextNode('META'));

})