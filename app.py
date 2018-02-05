import json
import lg 
import os
from flask import Flask, request, make_response, Response, jsonify
from slack import *
from threading import Thread


app = Flask(__name__)

SLACK_WEBHOOK_SECRET = os.environ.get('SLACK_WEBHOOK_SECRET')

lunchgroups = lg.LunchGroups()



@app.route('/slack', methods=['POST'])
def inbound():
	print(request.form)
	if request.form.get('token') == SLACK_WEBHOOK_SECRET:
		channel_id = request.form.get('channel_id')
		channel_name = request.form.get('channel_name')
		user_id = request.form.get('user_id')
		timestamp = request.form.get('ts')

		join_channel = lunchgroups.get_join_channel_id()
		if join_channel:
			close_open_channels_and_cleanup()

		include_user(user_id)

		lunchgroups.set_join_channel(channel_id, channel_name)
		channel_link = lunchgroups.get_join_channel_link()
		user_links = [user.get_link() for user in lunchgroups.get_users()]
		join_attachments = get_join_action_attachments(channel_link, user_links)
		join_message = send_attachment_message(channel_id, join_attachments)
		lunchgroups.set_join_channel_timestamp(join_message['ts'])
		
		message_organizer()
	return Response(), 200


@app.route('/message_action', methods=['POST'])
def buttons():
	form_json = json.loads(request.form["payload"])
	print(form_json)
	if form_json['token'] == SLACK_WEBHOOK_SECRET:
		if form_json['callback_id'] == "lunch_control":
			channel_id = form_json["channel"]["id"]
			channel_name = form_json["channel"]["name"]
			timestamp = form_json['message_ts']
			
			actions = form_json['actions']
			if actions[0]['value'] == 'create':
				if len(lunchgroups.get_users()) > 2:
					user_links = [user.get_link() for user in lunchgroups.get_users()]
					update_organizer_message(get_control_update_attachments(user_links))
					thread = Thread(target=conversation_async_action)
					thread.start()
			else:
				thread = Thread(target=delete_async_action, args=[channel_id, timestamp])
				thread.start()
		elif form_json['callback_id'] == "lunch_join":
			channel_id = form_json["channel"]["id"]
			channel_name = form_json["channel"]["name"]
			timestamp = form_json['message_ts']
			user_id = form_json['user']['id']
			
			user = include_user(user_id)
			if user:
				# tODO: add this when figure out how to delete
				# message_user(user_id)

				user_links = [user.get_link() for user in lunchgroups.get_users()]
				update_organizer_message(get_control_action_attachments(user_links))
				update_join_message()
		elif form_json['callback_id'] == "lunch_leave":
			channel_id = form_json["channel"]["id"]
			channel_name = form_json["channel"]["name"]
			timestamp = form_json['message_ts']
			user_id = form_json['user']['id']

			remove_user(user_id)
			send_delete_message(channel_id, timestamp)

			update_join_message()
	return make_response("", 200)


@app.route('/', methods=['GET'])
def base():
	return Response('It works!')



def include_user(user_id):
	user_info = users_info(user_id)
	username = user_info['name']
	profile = user_info['profile']
	firstname = profile.get('first_name') or ''
	lastname = profile.get('last_name') or ''
	
	user = lg.User(username, user_id, firstname, lastname)
	return lunchgroups.add_user(user)


def remove_user(user_id):
	return lunchgroups.remove_user(user_id)


def message_organizer():
	user = lunchgroups.get_organizer()
	if user:
		im = open_im_channel(user.get_handle())
		im_channel_id = im["channel"]["id"]
		user_links = [user.get_link() for user in lunchgroups.get_users()]
		attachments = get_control_action_attachments(user_links)
		im_results = send_control_message(user.get_handle(), attachments)
		timestamp = im_results['ts']
		channel_id = im_results['channel']
		lunchgroups.add_open_channel(channel_id, timestamp)


def message_user(user_id):
	im = open_im_channel(user_id)
	im_channel_id = im["channel"]["id"]
	channel_link = lunchgroups.get_join_channel_link()
	user_links = [user.get_link() for user in lunchgroups.get_users()]
	attachments = get_leave_action_attachments(channel_link, user_links)
	im_results = send_attachment_message(user_id, attachments)
	timestamp = im_results['ts']
	channel_id = im_results['channel']
	lunchgroups.add_open_channel(im_channel_id, timestamp)


def message_groups():
	lunchgroups.set_random_handle_groups()

	for users in lunchgroups.get_handle_groups():
		users_str = ",".join(users)
		send_conversation_messages(users_str)


def update_join_message():
	channel_id = lunchgroups.get_join_channel_id()
	timestamp = lunchgroups.get_join_channel_timestamp()
	channel_link = lunchgroups.get_join_channel_link()
	user_links = [user.get_link() for user in lunchgroups.get_users()]
	attachments = get_join_action_attachments(channel_link, user_links)
	update_attachment_message(channel_id, timestamp, attachments)


def update_organizer_message(attachments):
	channel_tuple = lunchgroups.get_organizer_channel_tuple()
	channel_id = lunchgroups.get_open_channel_id(channel_tuple)
	timestamp = lunchgroups.get_open_channel_timestamp(channel_tuple)
	update_attachment_message(channel_id, timestamp, attachments)


def close_open_channels_and_cleanup():
	join_channel_id = lunchgroups.get_join_channel_id()
	join_channel_timestamp = lunchgroups.get_join_channel_timestamp()
	send_delete_message(join_channel_id, join_channel_timestamp)

	for channel_tuple in lunchgroups.get_open_channel_tuples():
		channel_id = lunchgroups.get_open_channel_id(channel_tuple)
		channel_timestamp = lunchgroups.get_open_channel_timestamp(channel_tuple)
		send_delete_message(channel_id, channel_timestamp)

	lunchgroups.cancel()


def conversation_async_action():
	message_groups()


def delete_async_action(channel_id, timestamp):
	send_delete_message(channel_id, timestamp)
	close_open_channels_and_cleanup()



if __name__ == "__main__":
	app.run(debug=True)