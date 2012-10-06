function reloadTopics() {
	$('#tblTopics tr:gt(0)').remove()
	$.getJSON('topics', topicsFetched)
}
function topicsFetched(topics) {
	for (var i = 0; i < topics.length; i++)
		addTopicRow(topics[i])
}
function addTopicRow(topic) {
	var tdName = $('<td>').text(topic['name'])
	var tdActions = $('<td>')
	var aDelete = $('<a>').attr('href', 'topic?action=delete').text('Delete')
	tdActions.append(aDelete)
	$('#tblTopics').find('tbody')
		.append($('<tr>')
			.append(tdName)
			.append(tdActions)
		)
}