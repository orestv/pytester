function bodyLoaded() {
	reloadQuestions()
}
function reloadQuestions() {
	var attemptId = document.getElementById('attempt_id').value
	$.getJSON('/attempt_report?json=1' +
		'&attempt_id=' + attemptId +
		'&rnd=' + Math.random(), loadQuestions)
}
function loadQuestions(questions) {
	$('#tblQuestions tr:gt(0)').remove()
	var questionCount = 0
	var correctCount = 0
	console.log(questions)
	for (var id in questions) {
		if (addQuestionRow(id, questions[id]))
			correctCount++
		questionCount++
		console.log(questionCount)
	}
	$('#spTotal').text(questionCount)
	$('#spResult').text(correctCount)
}
function addQuestionRow(id, question) {
	var text = question['text'],
		multiselect = question['multiselect'],
		comment = question['comment']
	var tdQuestion = $('<td>').text(text).attr('colspan', '2')
	var tdAnswers = $('<td>').css('width', '70%')
	var tdComment = $('<td>').text(comment != null ? comment : '')
	var inputType = multiselect == 1 ? 'checkbox' : 'radio'

	var correct = true
	for (var i = 0; i < question.answers.length; i++) {
		ans = question.answers[i]
		var input = $('<input>').attr('type', inputType)
			.attr('disabled', 'disabled')
		var spAnswer = $('<span>')
		// spAnswer.text(ans.text)
		spAnswer.append(input).append(ans.text)
		if (ans.correct == 1)
			spAnswer.addClass('ans_correct')
		if (ans.selected == 1) {
			input.attr('checked', 'checked')
			if (ans.correct != 1)
				spAnswer.addClass('ans_wrong')
		}
		if (ans.correct != ans.selected) {
			correct = false
		}
		tdQuestion.addClass(correct ? 'question_correct' : 'question_wrong')
		tdAnswers.append(spAnswer)
	}

	$('#tblQuestions').find('tbody')
		.append($('<tr>')
			.append(tdQuestion))
		.append($('<tr>')
			.append(tdAnswers)
			.append(tdComment))
		.append($('<tr>')
			.append($('<td>')
				.attr('colspan', '2').append($('<hr>'))))
	return correct;
}