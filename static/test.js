function bodyLoaded() {
	submitStateUpdate()
}

function createRequest() {
	if (window.XMLHttpRequest){// code for IE7+, Firefox, Chrome, Opera, Safari
		return new XMLHttpRequest();
	} else {// code for IE6, IE5
		return new ActiveXObject("Microsoft.XMLHTTP");
	}
}

function answerUpdated(questionId) {
	var attemptId = document.getElementById('attemptId').value
	var inputs = document.getElementsByName(questionId)
	var ansIDs = ''
	for (var i = 0; i < inputs.length; i++)
		if (inputs[i].checked)
			ansIDs += inputs[i].value + ','

	var url = 'answerHandler'
	var params = 'question_id='+questionId+'&attempt_id='+attemptId+'&answers='+ansIDs
	var request = createRequest()
	request.open('POST', url, true)
	request.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
	request.send(params)
	submitStateUpdate()
}

function submitStateUpdate() {
	var canSubmit = true;
	$('td[name=questionContainer]').each(function(index, value) {
		if ($(this).find('input:checked').size() == 0)
			canSubmit = false;
	})
	if (canSubmit)
		$('#btnSubmit').removeAttr('disabled')
	else
		$('#btnSubmit').attr('disabled', 'disabled')
}