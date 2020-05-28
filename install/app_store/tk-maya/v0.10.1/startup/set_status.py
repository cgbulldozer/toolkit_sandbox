
def status_update(sg,task,user):
	id_ = task['id']
	user = user['name']

	data = {
        'sg_description': 'Opened by user - '+user,
        'sg_status_list': 'ip'
        }

	sg.update('Task',id_, data)
	return