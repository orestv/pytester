function bodyLoaded() {
	reloadTopics()
}

function btnAddTopic_clicked() {
	var name = document.getElementById('txtTopicName').value
	if (name.trim().length == 0)
		return
	addTopic(name)
}

function reloadTopics() {
	clearTopics()
	$.getJSON('/admin/topics?rnd=' + Math.random(), loadTopics)
}
function clearTopics() {
	$('#tblTopics tr:gt(1)').remove()
}
function loadTopics(topics) {
	for (var i = 0; i < topics.length; i++)
		addTopicRow(topics[i])
}
function addTopicRow(topic) {
	var id = topic['id'], name = topic['name'], questionCount = topic['question_count']
	var tdName = $('<td>')
	var tdQuestions = $('<td>').css('text-align', 'center').text(questionCount)
	var tdActions = $('<td>')
	var aQuestion = $('<a>').attr('href', '/admin/questions?topic_id=' + id)
							.text(name)
	var btnDelete = $('<input>').attr('type', 'button')
								.attr('value', 'Видалити')
								.click(function() {
									deleteTopic(id, name)
								})
	var btnRename = $('<input>').attr('type', 'button')
								.attr('value', 'Переіменувати')
								.click(function() {
									topicRenamePrepare(id, name)
								})
	tdName.append(aQuestion)
	tdActions.append(btnRename)
		.append(btnDelete)
	$('#tblTopics').find('tbody')
		.append($('<tr>')
			.attr('id', 'row_' + id)
			.append(tdName)
			.append(tdQuestions)
			.append(tdActions)
		)
}

function topicRenamePrepare(id, name) {
	var row = $('#row_' + id)
	row.empty()
	var input = $('<input/>').attr('type', 'text')
							.attr('value', name)
	var btnSave = $('<input/>').attr('type', 'button')
								.attr('value', 'Зберегти')
								.click(function() {
									var name = input[0].value
									if (name.length == 0)
										return
									renameTopic(id, name)
								})
	var btnCancel = $('<input/>').attr('type', 'button')
								.attr('value', 'Відмінити')
								.click(reloadTopics)
	row.append($('<td>').append(input))
		.append($('<td>').append(btnSave).append(btnCancel))
}

function deleteTopic(id, name) {
	if (!confirm('Ви впевнені, що бажаєте видалити тему \"' + name + '\"?'))
		return
	$.ajax({
		url: '/admin/topic',
		data: {action: 'delete', id: id},
		type: 'POST',
		success: reloadTopics
	})
}
function addTopic(name) {
	$.ajax({
		url: '/admin/topic',
		data: {action: 'add', name: name},
		type: 'POST',
		success: reloadTopics
	})
}
function renameTopic(id, name) {
	$.ajax({
		url: '/admin/topic',
		data: {action: 'rename', id: id, name: name},
		type: 'POST',
		success: reloadTopics
	})
}