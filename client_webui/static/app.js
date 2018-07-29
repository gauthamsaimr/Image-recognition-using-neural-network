const client_url = "http://192.168.1.101:8080/getimage_camera";
var client_tts = "http://192.168.1.101:8080/tts";
const server_url = "http://192.168.1.11:5000/caption_b64" // Can be shortened once on server

var current_image = 1;
var loop_enabled = false;
const loop_interval = 2000;
var loop_id = null;
var started = false;
// var inited = false;

function send_caption_tts(caption) {
    $.post(client_tts, {text: caption}, function () {
	console.log("Text to speech is done.");
    });
}


function scrollto_end() {
    var window_bot = $(window).scrollTop() + $(window).height();
    var elem = $("#content");
    var elem_bot = elem.outerHeight() + elem.offset().top
    if(window_bot < elem_bot)
	window.scrollTo(0, document.body.scrollHeight);
}

function add_image_content(rawImage_b64) {
    $("<div/>").attr("class", "pre-div").append($("<img/>", {
	src: "data:image/jpeg;base64," + rawImage_b64,
	alt: "Captured image"
    })).appendTo("#content");
    add_caption_content(rawImage_b64);
}

function add_caption_content(rawImage_b64) {
    $("<p/>", {
	text: "Waiting for the caption ...",
	id: current_image
    }).appendTo("#content");
    setTimeout(scrollto_end, 1000);
    $.post(server_url, {img: rawImage_b64}, process_caption_data);
}

function process_caption_data(caption_json) {
    $("#" + current_image).remove();
    $("<p/>", {
	text: "Returned Caption: " + caption_json.caption
    }).appendTo("#content")
    current_image += 1;
    started = false;
    send_caption_tts(caption_json.caption);
    if(loop_enabled) {
	loop_id = setTimeout(start_single, loop_interval);
    }
}

function start_single() {
    if(!started) {
	started = true;
	$("<p/>", {
	    text: "Starting capture of image " + current_image + " from the picamera"
	}).appendTo("#content");
	$.get(client_url, add_image_content);
    } else {
	$("<p/>", {
	    text: "Capture has already begun, please wait until the previous one ends."
	}).appendTo("#content");
	scrollto_end();
    }
}

function start_loop() {
    if(!loop_enabled){
	loop_enabled = true;
	start_single();
    } else {
	$("<p/>", {
	    text: "Capture loop has already begun, please wait until the previous one ends."
	}).appendTo("#content");
	scrollto_end();
    }
}

function stop_loop() {
    loop_enabled = false;
    if(loop_id != null) {
	clearTimeout(loop_id);
	loop_id = null;
    }
}

$("#confirm-start").click(function() {
    start_single(); 
})

$("#confirm-start-loop").click(function() {
    start_loop(); 
})

$("#confirm-stop").click(function() {
    stop_loop();
});


$("#offline").change(function(){
    if (this.checked) {
	client_tts = "http://192.168.1.101:8080/tts_offline";
    } else{
	client_tts = "http://192.168.1.101:8080/tts";
    }
});
