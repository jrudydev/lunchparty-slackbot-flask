import json
import os
from slackclient import SlackClient

SLACK_TOKEN = os.environ.get('SLACK_TOKEN')

slack_client = SlackClient(SLACK_TOKEN)


def list_channels():
	channels_call = slack_client.api_call("channels.list")
	if channels_call.get('ok'):
		return channels_call['channels']
	return None


def channel_info(channel_id):
	channel_info = slack_client.api_call("channels.info", channel=channel_id)
	if channel_info:
		return channel_info['channel']
	return None


def users_info(user_id):
	users_info = slack_client.api_call("users.info", user=user_id)
	if users_info:
		return users_info['user']
	return None


def open_im_channel(user_id):
	response = slack_client.api_call(
		"im.open",
		user=user_id,
		return_im=True
	)

	return response


def send_message(channel_id, message):
	slack_client.api_call(
		"chat.postMessage",
		channel=channel_id,
		text=message,
		username='lunchparty',
	)


def send_attachment_message(channel_id, attachments):
	'''
	Send an interactive slack message asking the users to join
	'''

	response = slack_client.api_call(
		"chat.postMessage",
		channel=channel_id,
		username='lunchparty',
		attachments=attachments
	)

	return response


def update_attachment_message(channel_id, timestamp, attachments):
	'''
	Send an interactive slack message asking the users to join
	'''

	response = slack_client.api_call(
		"chat.update",
		channel=channel_id,
		username='lunchparty',
		attachments=attachments,
		ts=timestamp,
	)

	return response



def send_control_message(channel_id, attachments):
	'''
	Send an interactive slack message asking the user for next action
	'''

	response = slack_client.api_call(
		"chat.postMessage",
		channel=channel_id,
		username='lunchparty',
		attachments=attachments
	)

	return response


def send_delete_message(channel_id, timestamp):
	response =  slack_client.api_call(
		"chat.delete",
		channel=channel_id,
		ts=timestamp,
	)

	return response


def send_conversation_messages(users):
	response = slack_client.api_call(
		"conversations.open",
		users=users
	)

	print(response)
	return response


def get_control_action_attachments(user_links):
	number_of_users = len(user_links)
	ready_users_str = ""
	if number_of_users > 1:
		ready_users = ", ".join(user_links)
		ready_users_str = ready_users + " are ready to be grouped.. "
	elif number_of_users > 0:
		ready_users_str = user_links[0] + " is ready to be grouped. "

	text = "You have started a lunch party. " + ready_users_str

	return json.dumps([
		{
			"fallback": "Control panel for lunch party",
            "text": text,
            "callback_id": "lunch_control",
            "color": "#3AA3E3",
            "attachment_type": "default",
            "actions": [
                {
                    "name": "choice",
                    "text": "Create Groups",
                    "type": "button",
                    "value": "create",
                    "style": "primary",
                },
                {
                    "name": "choice",
                    "text": "Cancel Lunch",
                    "type": "button",
                    "value": "cancel",
                }
            ],
            "mrkdwn_in": ["text", "pretext"],
        }
    ])


def get_join_action_attachments(channel_link, user_links):
	number_of_users = len(user_links)
	ready_users_str = ""
	if number_of_users > 1:
		ready_users = ", ".join(user_links)
		ready_users_str = ready_users + " are ready to go. "
	elif number_of_users > 0:
		ready_users_str = user_links[0] + " is ready to go. "

	text = "Lunch Party! " + user_links[0] + " will start lunch parties soon. "
	text += ready_users_str
	text += "Want to be randomly grouped for lunch with users in " + channel_link + "?"

	return json.dumps([
		{
			"fallback": "Option for join the lunch party",
            "text": text,
            "callback_id": "lunch_join",
            "color": "#3AA3E3",
            "attachment_type": "default",
            "actions": [
                {
                    "name": "choice",
                    "text": "Join Lunch Party",
                    "type": "button",
                    "value": "join",
                    "style": "primary",
                }
            ],
            "mrkdwn_in": ["text", "pretext"],
        }
    ])


def get_leave_action_attachments(channel_link, user_links):
	number_of_users = len(user_links)
	ready_users_str = ""
	if number_of_users > 0:
		ready_users = ", ".join(user_links)
		ready_users_str = ready_users + " will be grouped soon. "

	text = "You've joined " + user_links[0] + " for a random lunch party. "
	text += ready_users_str

	return json.dumps([
		{
			"fallback": "Option for leaving the lunch party",
            "text": text,
            "callback_id": "lunch_leave",
            "color": "#3AA3E3",
            "attachment_type": "default",
            "actions": [
                {
                    "name": "choice",
                    "text": "Leave Lunch Party",
                    "type": "button",
                    "value": "leave",
                    "style": "primary",
                }
            ],
            "mrkdwn_in": ["text", "pretext"],
        }
    ])


def get_control_update_attachments(user_links):
	ready_users = ", ".join(user_links) + " have been grouped."
		
 	attachments = json.loads(get_control_action_attachments(user_links))
 	attachments[0]['text'] = 'You started a lunch party. ' + ready_users
 	attachments[0]['text'] += '\n:white_check_mark: '
	attachments[0]['text'] += '*Lunch groups created and conversations have started*'
	attachments[0]['actions'] = []

	return json.dumps(attachments)

	

if __name__ == '__main__':
	channels = list_channels()
	if channels:
		print("Channels: ")
		for c in channels:
			channel_name = c['name']
			channel_id = c['id']
			print(channel_name + " (" + channel_id + ")")
			detailed_info = channel_info(c['id'])
			if detailed_info:
				print(detailed_info['latest']['text'])
			if channel_name == 'general':
				send_message(channel_id, "Hello" + 
					channel_name + "! It Worked!")
	else:
		print("Unable to authenticate.")
