function bodyLoaded() {
	reloadQuestions()
}
function reloadQuestions() {
	var topic_id = document.getElementById('topic_id').value
	$.getJSON('/admin/questions?json=1&topic_id='+topic_id+'&rnd=' + Math.random(), loadQuestions)
}
function loadQuestions(questions) {
	$('#tblQuestions tr:gt(0)').remove()
	var questionCount = 0
	for (var id in questions) {
		addQuestionRow(id, questions[id])
		questionCount++
	}
	$('#spQuestionCount').text(questionCount)
}
function addQuestionRow(id, question) {
	var text = question['text'],
		multiselect = question['multiselect'],
		comment = question['comment']
	var tdQuestion = $('<td>').text(text)
	var tdAnswers = $('<td>')
	var tdComment = $('<td>').text(comment != null ? comment : '')
	var tdActions = $('<td>')

	var ulAnswers = $('<ul>')
	for (var i = 0; i < question.answers.length; i++) {
		ans = question.answers[i]
		var liAnswer = $('<li>').text(ans.text)
		if (ans.correct == 1)
			liAnswer.addClass('correct')
		ulAnswers.append(liAnswer)
	}
	tdAnswers.append(ulAnswers)
	tdActions.append($('<input>')
		.attr('type', 'button')
		.attr('value', 'Видалити')
		.click(function() {
			if (!confirm('Ви впевнені, що хочете видалити це питання?'))
				return
			deleteQuestion(id)
		}))

	$('#tblQuestions').find('tbody')
		.append($('<tr>')
			.append(tdQuestion)
			.append(tdAnswers)
			.append(tdComment)
			.append(tdActions))
}
function deleteQuestion(questionId) {
	$.ajax({
		url: '/admin/question',
		data: {action: 'delete', question_id: questionId},
		success: reloadQuestions
	})
}