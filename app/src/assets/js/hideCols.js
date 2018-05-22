
function hideCol(el) {
  console.log("Clicked");

  var classname = el.id;
  var thisElem = document.getElementById(classname);
  var thisHeader = document.getElementById(classname+"_header")
  // console.log(isShown);
  // console.log(isShown.style.display);
  var classes = document.getElementsByClassName(classname);
  var checkFirst = classes[0].style.display;
  console.log(checkFirst);
  if (checkFirst === 'none') {
    for (var i = 0; i < classes.length; i++) {
      classes[i].style.display = "inline";
    }
    thisElem.innerHTML = "-";
    thisElem.style.color = "red";
    thisHeader.style.width = "inherit";
    // thisHeader.style.padding = "8px";
  }
  else {
    for (var i = 0; i < classes.length; i++) {
      classes[i].style.display = "none";
    }
    thisElem.innerHTML = "+";
    thisElem.style.color = "green";
    thisHeader.style.width = "5px";
    // thisHeader.style.padding = "0px";
    // thisHeader.style.paddingTop = "8px";
  }

  //hide all data in cols
  



}
