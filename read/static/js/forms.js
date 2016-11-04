$('form').on('submit', function(event) {
	event.preventDefault();
	var $form = this;
	$.ajax({
		type: $form.method,
		url: $form.action,
		data: new FormData($($form)[0]),
		processData: false,
		contentType: false,
		success: function(data) { // A server-side error results in a success response since we get an error message.
			responseData = $.parseJSON(data);
			$("#messages").html(responseData.MESSAGE);
			if ('true' == responseData.RESET) // But only a successful response should reset the form.
				$form.reset();
		},
	});
});