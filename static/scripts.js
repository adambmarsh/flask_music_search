
export function setPlayer(directoryPath,fileName){
      let uri = `stream?dir=${directoryPath}&fname=${fileName}`;
      let player = document.getElementById('player');
      if(player.src != uri){
        player.src = uri;
      }
      let listener = (event) => {player.play();
        player.removeEventListener("canplay",listener);
      }
      player.addEventListener("canplay", listener)
    }

function checkDuplicates() {
      let table = document.querySelector('#table');
      let rowCount = table.rows.length;
      let colCount = table.rows[0].cells.length;

      let isRowSpan = false;
      let startCell;
      let spanSize;
      let deletes = [];

      // skip the first column because it contains play buttons
      for (let colNo = 1; colNo < colCount; colNo++) {


        for (let rowNo = 1; rowNo < rowCount; rowNo++) {
          let thisCell = table.rows[rowNo].cells[colNo];
          if (thisCell === undefined) {
            console.log("Error: cell undefined");
          }
          let prevCell = table.rows[rowNo - 1].cells[colNo];
          if (thisCell.textContent === prevCell.textContent) {
            if (!isRowSpan) {
              startCell = prevCell;
              spanSize = 2;
            }
            else {
              spanSize++;
            }
            deletes.push([rowNo, colNo])
            isRowSpan = true;
          }
          else {
            if (isRowSpan === true) {
              isRowSpan = false;
              startCell.rowSpan = spanSize;
              spanSize = 0;
            }
          }
        }
      }
      deletes.sort((a, b) => {
    // First, compare by row index (descending)
    // If b.row is greater than a.row, b comes before a
    if (a[0] !== b[0]) { // a[0] is row, b[0] is row
        return b[0] - a[0];
    }
    // If row indices are equal, then compare by column index (descending)
    // If b.col is greater than a.col, b comes before a
    return b[1] - a[1]; // a[1] is col, b[1] is col
});
      if(deletes.length > 0){
          for (let i = 0; i < deletes.length; i++){
            try{
            table.rows[deletes[i][0]].deleteCell(deletes[i][1]);
            }
            catch(err){
              console.log(err.message);
            }
          }
        deletes = [];
      }
    }

function loadDoc(url, cFunction) {
      var xhttp;
      xhttp = new XMLHttpRequest();
      xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
          cFunction(this);
        }
      };

      var data = JSON.stringify({
        "query": document.getElementById("query").value,
        'columns': document.getElementById("columns").value
      });
      xhttp.open("POST", url, true);
      xhttp.setRequestHeader("Content-Type", "application/json");
      xhttp.send(data);
    }
function myFunction(xhttp) {
      const clean_response = xhttp.response.replace(/[\n ]/, '');
      const json_response = JSON.parse(clean_response);
      document.getElementById("output").innerHTML = json_response.html;
      const result_elements = document.getElementsByTagName("mark");
      for (let each of result_elements) {
        each.style.color = "red";
      }
      checkDuplicates();

    }
function preventEnter(event) {
      if (event.keyCode === 13) {
        event.preventDefault();
        document.getElementById("button").click();
        return false;
      }
    }

export function callback(){
      document.querySelector('#form').addEventListener("keydown",preventEnter);
      document.querySelector('#button').addEventListener("click",()=>{loadDoc('/form',myFunction)});
      }
