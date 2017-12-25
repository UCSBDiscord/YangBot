import discord
import asyncio
import secretvalues
from datetime import datetime
from datetime import timedelta
import recordconvo

def prune(send_message):
	pos = send_message.find('>')
	return send_message[pos+1:]


def contains(text, choices):
	split_text = text.split()
	split_text = [s.lower() for s in split_text]
	for word in choices:
		if word in split_text:
			return True
	return False


server_id, gauchito_id, login_token = secretvalues.get_values()

on_join_message = "Hello, %s, and welcome to the UCSB Discord Server!\n \nWe ask that you introduce yourself so that the other members can get to know you better. Please post an introduction to our dedicated introductions channel with the following format:\n\n1) Discord handle (username#XXXX)\n2) School/Year/Major or the equivalent (UCSB/3rd/Underwater Basketweaving)\n3) Reason for joining the server (Make new friends)\n4) How you found us. If you found us through another person, please list their name or their discord handle because we like to keep track of who invites other people.\n \nAlso, please read the rules. We don't want to have to ban you because you failed to read a short list of rules.\n \n \n(Disclaimer: This bot is NOT Chancellor Yang, and does not represent his opinions. Attributing anything said by this bot to Chancellor Yang will result in a swift banning)" 


#YangBot's responses
choiced_responses = {
	"dank": "I sure hope you're talking about dank memes and not that dank green!",
	"blaze": "I sure hope you're talking about the pizza!",
	"alcohol": "Reminder that underage drinking is prohibited at UCSB.", #should only be triggered by gauchito
	"mj": "Despite the passing of Prop 64, marijuana usage is prohibited at UCSB except for university-approved research.",
	"adderall": "If you need to study, go to the UCSB Library. Most people focus the best on the 8th floor.",
	"fire": "Put on a mask and get back to studying",
	"drug": "Substance abuse is prohibited at UCSB",
	"party": "Go back to studying"
}


#Words that trigger YangBot. These are directly connected to the responses above with the words on the left
trigger_words = {
	"dank": ['dank'],
	"blaze": ['blaze'],
	"alcohol": ['alcohol', 'vodka', 'wine', 'beer', 'drunk', 'whiskey', 'beers'], #should only be triggered by gauchito
	"mj": ['mj', '420', 'weed', 'kush', 'marijuana'],
	"adderall": ['adderall', 'adderal', 'addy'],
	"drug": ['drug', 'acid', 'lsd', 'shrooms', 'xanax', 'coke', 'cocaine'],
	"fire": ['fire'],
	"party": ['party']
}


#Words that only are triggered by gauchitos
gauchito_only = ["alcohol", "party"]


#Recent channel messages
recent_channel_messages = {}

client = discord.Client()


async def trigger(message):
	global last_trigger
	for option, words in trigger_words.items():
		if option not in gauchito_only:
			if contains(message.content, words):
				last_trigger = datetime.now()
				await client.send_message(message.channel, choiced_responses[option])
				break
		elif gauchito_id in [role.id for role in message.author.roles]:
			if contains(message.content, words):
				last_trigger = datetime.now()
				await client.send_message(message.channel, choiced_responses[option])
				break

async def yang_send(message):
	if message.author.server_permissions.manage_server:
		if len(message.channel_mentions) != 0:
			await client.send_message(message.channel_mentions[0], prune(message.content))
			if message.content[5] == 'h':
				await client.delete_message(message)
		else:
			await client.send_message(message.channel, 'Syntax is "$send [channel mention] text"')
	else:
		await client.send_message(message.channel, 'Invalid Permissions')


@client.event
async def on_ready():
	print('Logged in as')
	print(client.user.name)
	print(client.user.id)
	print('--------')
	for server in client.servers:
		for channel in server.channels:
			if server.me.permissions_in(channel).send_messages:
				recent_channel_messages[channel.id] = []
	print('Channels loaded')
	print(recent_channel_messages)

@client.event
async def on_message(message):
	#TODO stuff
	global recording, recent_channel_messages
	try:
		if message.server.id == server_id and message.author != client.user:
			if message.channel.id in recent_channel_messages.keys():
				recent_channel_messages[message.channel.id].append(message.content)
				is_same = same_message_response(message.channel.id)
				if is_same:
					await client.send_message(message.channel, message.content)
					recent_channel_messages[message.channel.id].clear()
			if recording is not None and recording == message.channel:
				recordconvo.record_message(message)
			if message.content[0:5] == '$send':
				await yang_send(message)
			elif message.content[0:7] == '$record' and message.author.server_permissions.manage_server:
				if recording is None:
					recordconvo.record_init()
					recording = message.channel
				else:
					await client.send_message(message.channel, "Already recording in %s" % (recording.mention))
			elif message.content[0:11] == '$stoprecord' and message.author.server_permissions.manage_server:
				recordconvo.record_end()
				recording = None
			elif message.timestamp - last_trigger > timedelta(minutes=2):
				await trigger(message)
	except Exception as e:
		print('There was an error somewhere in on_message: ' +str(e))


@client.event
async def on_message_edit(before, after):
	try:
		if after.server.id == server_id and after.author != client.user:
			if recording is not None and recording == after.channel:
				recordconvo.record_message_edit(after)
	except:
		print('There was an error somewhere in on_message_edit')

@client.event
async def on_message_delete(message):
	try:
		if message.server.id == server_id and message.author != client.user:
			if recording is not None and recording == message.channel:
				recordconvo.record_message_delete(message)
	except:
		print('There was an error somewhere in on_message_delete')

@client.event
async def on_member_join(member):
	try:
		await client.send_message(member, content=(on_join_message % (member.mention)))
	except:
		print('There was an error somewhere in on_member_join')

def same_message_response(channel_id):
	if len(recent_channel_messages[channel_id]) > 3:
		recent_channel_messages[channel_id].pop(0)
	if len(recent_channel_messages[channel_id]) < 3:
		return False
	s = recent_channel_messages[channel_id][0].lower()
	if s == recent_channel_messages[channel_id][1].lower() and s == recent_channel_messages[channel_id][2].lower():
		return True
	else:
		return False

recording = None
last_trigger = datetime.now() - timedelta(minutes=2)
client.run(login_token)
