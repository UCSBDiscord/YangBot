import markovify
from datetime import timedelta

message_cache = 'cached_messages.txt'
SIMULATION_INTERVAL = timedelta(minutes=30)
def simulate():
	with open(message_cache) as file:
		text = file.read()
		markov_model = markovify.NewlineText(text)
		return clean_text(markov_model.make_sentence())


def clean_text(text):
	return text.replace('@', '')
	#This is its own method in case more needs to be cleaned