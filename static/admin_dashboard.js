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
	$.getJSON('topics', loadTopics)
}
function clearTopics() {
	$('#tblTopics tr:gt(1)').remove()
}
function loadTopics(topics) {
	for (var i = 0; i < topics.length; i++)
		addTopicRow(topics[i])
}
function addTopicRow(topic) {
	var id = topic['id'], name = topic['name']
	var tdName = $('<td>').text(name)
	var tdActions = $('<td>')
	var btnDelete = $('<input>').attr('type', 'button')
								.attr('value', 'Видалити')
								.attr('onclick', 'deleteTopic('+id+', \''+name+'\');')
	tdActions.append(btnDelete)
	$('#tblTopics').find('tbody')
		.append($('<tr>')
			.append(tdName)
			.append(tdActions)
		)
}
function deleteTopic(id, name) {
	if (!confirm('Ви впевнені, що бажаєте видалити тему \"' + name + '\"?'))
		return
	$.ajax({
		url: 'topic',
		data: {action: 'delete', id: id},
		type: 'POST',
		success: reloadTopics
	})
}
function addTopic(name) {
	$.ajax({
		url: 'topic',
		data: {action: 'add', name: name},
		type: 'POST',
		success: reloadTopics
	})
}