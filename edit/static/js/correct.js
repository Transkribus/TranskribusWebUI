var initialWidth;
var scrollFactor;
var changed = false;
var isDragged = false;
var transcriptDivHeightString;
var savedZoom = 0;
var surroundingCount = 1;
var currentLineId;
var modalBelowMouse = 50;// TODO Decide whether to calculate this or have a simple default. Note pages with text near the lower edge...
var ballRadius = 50;// TODO Decide how to set this. 
var ignoreLeave = false;
var topLineId = null;

// "JSON.stringifies" contentArray and also strips out content which does not need to be submitted.
function getContent() {
	var lengthMinusOne = contentArray.length - 1;
	content = '{';
	for (var cI = 1; cI <= lengthMinusOne; cI++) {// cI = 1 since we skip the "line" which isn't real since it's the top of the page
		content += '"' + contentArray[cI][0] + '":"' + contentArray[cI][1] + '"';
		if (cI < lengthMinusOne)
			content += ',';
	}
	content += '}';
	return content;
}

// Modal functions:
function updateModalPosition(clickX, clickY) {
	$( ".modal" ).css("left", (clickX - parseInt($( ".modal-dialog" ).css("width"), 10)/2) + 'px');
	$( ".modal" ).css("top", clickY + modalBelowMouse);
}

// Line functions:
function getIndexFromLineId(lineId) {
	var length = contentArray.length;
	var index;// TODO Consider optimizing, i.e. "cache" the index and first compare with the previously requested lineId?
	for (index = 0; index < length; index++) {
		if (contentArray[index][0] == lineId)
			return index;
	}
	return null;
}
function getNextLineId(lineId) {
	index = getIndexFromLineId(lineId); 
	if (contentArray.length == (index + 1))
		return null;// If it's the last line, we don't have a next id.
	else
		return contentArray[index + 1][0];
}
function getPreviousLineId(lineId) {
	index = getIndexFromLineId(lineId);
	if (1 == index)
		return null;// If it's the first line, we don't have a previous id. Note: The first real line is [1] because the very first "line" in the array is "", i.e. not a line but the top of the page.
	else
		return contentArray[index - 1][0];
}
function setCurrentLineId(newId) {// We're not happy with just "=" to set the new id because we want to detect changes, if any, so we have this function.
	currentContent = $("#currentLine").val();
	if (null != currentLineId && contentArray[getIndexFromLineId(currentLineId)][1] != currentContent) {		
		if (!changed)
			setMessage("<div class='alert alert-warning'>" + transUnsavedChanges + "</div>");
		changed = true;
		contentArray[getIndexFromLineId(currentLineId)][1] = currentContent;
	}	
	currentLineId = newId;
}
function getHighlightBottomY(centerLineId) {
	return Math.round(scrollFactor*contentArray[Math.min(getIndexFromLineId(centerLineId) + surroundingCount, contentArray.length - 1)][2][5]);
}
function scrollToNextTop() { 
	var currentTop = -Math.round(parseInt($( ".transcript-map-div" ).css("top"), 10)/scrollFactor) + 1;// +1 to avoid problems caused by rounding.
	var newTop;
	for (idx = 0; idx < contentArray.length; idx++) {
		newTop = contentArray[idx][2][1];
		if (newTop > currentTop) {
			break;
		}
	}
	$( ".transcript-map-div" ).css("top", -Math.round(newTop*scrollFactor) + 'px');
}
function scrollToPreviousTop() { 
	var currentTop = -Math.round(parseInt($( ".transcript-map-div" ).css("top"), 10)/scrollFactor) - 1;// -1 to avoid problems caused by rounding.
	var newTop;
	for (idx = contentArray.length - 1; idx >= 0; idx--) {
		newTop = contentArray[idx][2][1];
		if (newTop < currentTop) {
			break;
		}
	}
	$( ".transcript-map-div" ).css("top", -Math.round(newTop*scrollFactor) + 'px');
}

// GUI:
function setMessage(message) {
	$("#message").html(message);
}
function buildLineList() {
	$(".line-list").html("");
	$('area').mapster('set', false);
	idArray = new Array(2*surroundingCount);
	i = surroundingCount - 1;
	id = currentLineId;
	while (i >= 0) { // TODO Fix this! It works but not because of how it should work (break = broken).
		id = getPreviousLineId(id);
		if (null == id) {
			break;
		}
		idArray[i] = id;
		i--;
	}
	i = surroundingCount;
	id = currentLineId;
	while (i < idArray.length) {
		id = getNextLineId(id);
		if (null == id)
			break;
		idArray[i] = id;
		i++;			
	}
	i = 0;
	while (i < surroundingCount) {
		id = idArray[i];
		if (null != id) {
			$(".line-list").append('<li>' + contentArray[getIndexFromLineId(id)][1] + '</li>');
			highlightLine(id);
		}
		i++;
	}
	$(".line-list").append('<li><input class="form-control added-line" type="text" id="currentLine" value="' + contentArray[getIndexFromLineId(currentLineId)][1] + '" /></li>');
	highlightLine(currentLineId);
	placeBalls(currentLineId);
	while (i < idArray.length) {
		id = idArray[i];
		if (null != id) {
			$(".line-list").append('<li>' + contentArray[getIndexFromLineId(id)][1] + '</li>');
			highlightLine(id);
		}
		i++;			
	}
	$("#currentLine").focus();
}

// Actions: 
function typewriterNext() { // Aka. "press typewriter enter scroll". Changes the selected lines and the modal content.
	newLineId = getNextLineId(currentLineId);
	if (newLineId != null)
		typewriterStep(newLineId, Math.round(scrollFactor*contentArray[Math.min(getIndexFromLineId(newLineId) + surroundingCount, contentArray.length - 1)][2][5]) - Math.round(scrollFactor*contentArray[Math.min(getIndexFromLineId(currentLineId) + surroundingCount, contentArray.length - 1)][2][5]))
}
function typewriterPrevious() {
	newLineId = getPreviousLineId(currentLineId);
	if (newLineId != null)
		typewriterStep(getPreviousLineId(currentLineId), Math.round(scrollFactor*contentArray[Math.min(getIndexFromLineId(newLineId) + surroundingCount, contentArray.length - 1)][2][5]) - Math.round(scrollFactor*contentArray[Math.min(getIndexFromLineId(currentLineId) + surroundingCount, contentArray.length - 1)][2][5]));
}
function typewriterStep(newLineId, delta) {
	var old = parseInt($( ".transcript-map-div" ).css("top"), 10);
	$( ".transcript-map-div" ).css("top", (old - delta) + 'px');
	resetCanvas();
	setCurrentLineId(newLineId);
	buildLineList();
}
function resetCanvas() {        
	var c=document.getElementById("transcriptCanvas");
	var ctx=c.getContext("2d");
	ctx.canvas.width = $('#transcriptImage').width();
	ctx.canvas.height = $('#transcriptImage').height();
	ctx.fillStyle = "rgba(0, 0, 0, 0.15)";
	ctx.fillRect(0,0,ctx.canvas.width,ctx.canvas.height);
	ctx.save();
}
function placeBalls(lineId) {
	var length = contentArray.length;
	var coords =  Array(8);// TODO Four coordinate pairs are not needed...
	for (j = 0; j < length; j++) {// TODO Stop the loop sooner!
		if (contentArray[j][0] == lineId) {
			for (k = 0; k < coords.length; k++) {
				coords[k] = Math.round(scrollFactor*contentArray[j][2][k]);
			}
		}
	}
	var lineHeight = (coords[5] - coords[1]); // We use this to get "appropriate" places for the balls in relation to the lize size...
	var c=document.getElementById("transcriptCanvas");
	var ctx=c.getContext("2d");
	ctx.beginPath(); 
	ctx.arc(coords[0] -1.5 * lineHeight, coords[1] + lineHeight / 2, 10, 0, 2*Math.PI);
	ctx.arc(coords[4] + 1.5 * lineHeight, coords[1] + lineHeight / 2, 10, 0, 2*Math.PI);
	ctx.fillStyle = "rgba(0, 255, 0, 1)";
	ctx.fill();
}
function highlightLine(lineId) {
	var length = contentArray.length;
	var coords =  Array(8);// TODO Four coordinate pairs are not needed for a rectangle...
	for (j = 0; j < length; j++) {// TODO Stop the loop sooner!
		if (contentArray[j][0] == lineId) {						
			for (k = 0; k < coords.length; k++)
				coords[k] = Math.round(scrollFactor*contentArray[j][2][k]);
		}
	}
	var c=document.getElementById("transcriptCanvas");
	var ctx=c.getContext("2d");
	ctx.clearRect(coords[0], coords[1], coords[4] - coords[0], coords[5] - coords[1]);
}

function setZoom(zoom, x, y) {
	if (1 == arguments.length) {
		x = parseInt($( ".transcript-map-div" ).css("width"), 10)/2;
		y = parseInt($( ".transcript-map-div" ).css("height"), 10)/2;
	}
	var newZoom = savedZoom + zoom;
	if (newZoom >= 0) 
		savedZoom = newZoom;
	else
		return;// We don't allow zooming out more than what the size originally was.
	var zoom_factor = savedZoom / 100;
	$('#transcriptImage').mapster('resize', Math.round(initialWidth * (1 + zoom_factor)));
	widthBefore = parseInt($( ".transcript-map-div" ).css("width"), 10);
	heightBefore = $('#transcriptImage').height();
	$( ".transcript-map-div" ).css("width", $('#transcriptImage').width() + 'px');// If the image is offset so that it can grow within the div, we let it.
	$( ".transcript-div" ).css("height", transcriptDivHeightString);// We wish to preserve the height.
	ratio = parseInt($( ".transcript-map-div" ).css("width"), 10)/widthBefore - 1;
	newLeftOffset = $( ".transcript-map-div" ).offset().left - x * ratio;
	newTopOffset = $( "#transcriptImage" ).offset().top - y * ratio;
	$( ".transcript-map-div" ).offset({top: newTopOffset, left: newLeftOffset}); 
	scrollFactor = $('#transcriptImage').width() / $('#transcriptImage').get(0).naturalWidth;	
	resetCanvas();
}
