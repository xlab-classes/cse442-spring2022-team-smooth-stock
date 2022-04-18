function showRow(rowId) {
    document.getElementById(rowId).style.display = "";
}
function hideRow(rowId) {
    document.getElementById(rowId).style.display = "none";
}

$(document).ready(function() {
    console.log("js is being included!");
    var newsTableBody = document.getElementById('news-table').getElementsByTagName('tbody')[0];    
    var metaRow = newsTableBody.insertRow();
    var newCell = metaRow.insertCell();
    var newText = document.createTextNode('Meta');
    newCell.append(newText);
    let tickerCell = metaRow.insertCell().append(document.createTextNode('META'));
})