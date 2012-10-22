function bodyLoaded() {
	submitStateUpdate()
	window.requestCount = 0
}

function createRequest() {
	if (window.XMLHttpRequest){// code for IE7+, Firefox, Chrome, Opera, Safari
		return new XMLHttpRequest();
	} else {// code for IE6, IE5
		return new ActiveXObject("Microsoft.XMLHTTP");
	}
}

function updateAnswer(questionId) {
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
	request.onreadystatechange = function() {
		if (request.readyState == 4)
			submitEnable()
	}
	request.send(params)
	submitDisable();
}

function submitEnable() {
	window.requestCount--
	if (window.requestCount == 0)
		$('#btnSubmit').removeAttr('disabled')
	var hidFinished = document.getElementById('finished')
	hidFinished.value = (allQuestionsAnsweredCheck() ? '1' : '0')
}
function submitDisable() {
	if (window.requestCount == 0)
		$('#btnSubmit').attr('disabled', 'disabled')
	window.requestCount++
}
function allQuestionsAnsweredCheck() {
	var answered = true
	$('td[name=questionContainer]').each(function(index, value) {
		if ($(this).find('input:checked').size() == 0)
			answered = false;
	})
	return answered
}

function submitStateUpdate() {
	var canSubmit = true
	$('td[name=questionContainer]').each(function(index, value) {
		if ($(this).find('input:checked').size() == 0)
			canSubmit = false;
	})
	if (canSubmit)
		$('#btnSubmit').removeAttr('disabled')
	else
		$('#btnSubmit').attr('disabled', 'disabled')
}