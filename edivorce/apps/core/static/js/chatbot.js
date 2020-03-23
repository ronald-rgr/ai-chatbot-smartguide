$('#target').on('submit', function(e){
    e.preventDefault();
    const input_message = $('#input_message').val()
    // return if the user does not enter any text
    if (!input_message) {
      return
    }
	
	var d = new Date();
    var h = d.getHours();
    var m = addZero(d.getMinutes());

    $('.chat-container').append(`

        <div class="row">
            <div class="chat-message col-md-10 human-message">
                ${input_message}
            </div>
			<div class ="human-msg-time">
                ${h}: ${m}
            </div>
        </div>
    `)

    // loading 
    $('.chat-container').append(`
        <div class="chat-message text-center col-md-2 col-offset-md-10 bot-message" id="loading">
            <b>...</b>
        </div>
    `)

    // clear the text input 
    $('#input_message').val('')

    //add the close button
    document.getElementById('closeChatContainer').style.display = "block"

    // send the message
    submit_message(input_message)
});

function submit_message(message) {
    $.post( "/send_message", {message: message}, handle_response);
    $(".chat-container").stop().animate({ scrollTop: $(".chat-container")[0].scrollHeight }, 1000);

    function handle_response(data) {
	
	var d = new Date();
	var h = d.getHours();
	var m = addZero(d.getMinutes());	
		
    // append the bot repsonse to the div
    $('.chat-container').append(`
        <div class ="bot-msg-time">
                    ${h}: ${m}
        </div>
        <div class="row">
            <div class="chat-message col-md-10 bot-message">
                ${data.message}
            </div>
        <div>
    `)
    // remove the loading indicator
    $( "#loading" ).remove();
    $(".chat-container").stop().animate({ scrollTop: $(".chat-container")[0].scrollHeight }, 1000);
    }
	
	document.getElementById('closeChatContainer').style.display = "block"
}

function displayChat() {
    document.getElementById('chatContainer').style.display = "block"
    if (document.getElementsByClassName('bot-message').length != 0 || document.getElementsByClassName('human-message').length != 0) {
        document.getElementById('closeChatContainer').style.display = "block"
    }
       
}

function closeChat() {
    document.getElementById('chatContainer').style.display = "none"
    document.getElementById('closeChatContainer').style.display = "none"
}

function addZero(i) {
    if (i < 10) {
        i = "0" + i;
    }
    return i;
}

