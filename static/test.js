function bodyLoaded() {
	window.requestCount = 0
	submitEnable()
	answeredQuestionsMark()
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
	var url = 'update_answers'
	var params = 'question_id='+questionId+'&attempt_id='+attemptId+'&answers='+ansIDs
	var request = createRequest()
	request.open('POST', url, true)
	request.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
	request.onreadystatechange = function() {
		if (request.readyState == 4)
			window.requestCount--;
			submitEnable()
	}
	request.send(params)
	submitDisable();
	answeredQuestionsMark()
}

function submitEnable() {
	if (window.requestCount == 0) {
		$('#btnSubmit').removeAttr('disabled').attr('value', 'Зберегти')
		var hidFinished = document.getElementById('finished')
		var finished = allQuestionsAnsweredCheck()
		hidFinished.value = (finished ? '1' : '0')
		$('#btnSubmit').attr('value', finished ? 'Завершити' : 'Зберегти')
	}
}
function submitDisable() {
	if (window.requestCount == 0)
		$('#btnSubmit').attr('disabled', 'disabled').attr('value', 'Зберігаю...')
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
function answeredQuestionsMark() {
	$('td[name=questionContainer]').each(function(index, value) {
		var spQuestion = $(this).find('span[name=question]')
		console.log(spQuestion)
		if ($(this).find('input:checked').size() == 0)
			spQuestion.removeClass('answered')
		else
			spQuestion.addClass('answered')
	})
}