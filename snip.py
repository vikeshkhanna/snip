#!/usr/bin/env python
'''
@author: Vikesh Khanna
snip is a simple terminal client to submit SNAP's homework assignments. Works for courses - CS224W, CS246.
'''

from bs4 import BeautifulSoup
import urllib2
import re
import os, sys
import requests

def get_options(select):
	options = []

	for child in select.children:
		schild = str(child)
		s1 = re.search('value=\"(.*?)\"', schild)
		s2 = re.search('>(.*?)<', schild)

		if s1 and s2:
			value = s1.group(1)
			contents = s2.group(1)
			options.append((value, contents))

	return options

class ARGS:
	SUBMIT='submit'
	HOMEWORK='hw'
	QUESTION='q'
	SUNETID='--'
	VERBOSE='v'
	FORCE='f'
	HELP='h'

class PAGE_CONSTANTS:
	hw='hw'
	q='q'
	course='class'
	sunetid='sunetid'
	userfile='userfile'

def get_usage():
	return """snip submit <filename> [-hw 1] [-q 2] [--vikesh] [-v] [-f] [-h]
			v: Verbose response from SNAP server.
			f: Force. Does not ask for confirmation before posting.
			h: Help
		"""

def main(argv):
	if len(argv)<1:
		print get_usage()
		sys.exit(1)

	filename = argv[0]

	options = {ARGS.HOMEWORK:None, ARGS.QUESTION:None, ARGS.SUNETID:None, ARGS.VERBOSE:True, ARGS.FORCE:False}

	for i, arg in enumerate(argv):
		if arg.startswith('-'):
			if arg[:2]==ARGS.SUNETID:
				options[ARGS.SUNETID] = arg[2:]
			elif arg[1:]==ARGS.HOMEWORK:
				options[ARGS.HOMEWORK] = argv[i+1]
			elif arg[1:]==ARGS.QUESTION:
				options[ARGS.QUESTION] = argv[i+1]
			elif arg[1:]==ARGS.VERBOSE:
				options[ARGS.VERBOSE] = True
			elif arg[1:]==ARGS.FORCE:
				options[ARGS.FORCE] = True
			elif arg[1:]==ARGS.HELP:
				print(get_usage())
				return 0
			else:
				raise Exception("Invalid argument")

	if not os.path.isfile(filename):
		print("File does not exist")
		sys.exit(1)

	URL = "http://snap.stanford.edu/submit/index.php"

	response = urllib2.urlopen(URL)
	html = response.read()

	soup = BeautifulSoup(html)

	course = soup.find('input', {'name':PAGE_CONSTANTS.course})
	homework_select = soup.find('select', {'name':PAGE_CONSTANTS.hw})
	questions_select = soup.find('select', {'name':PAGE_CONSTANTS.q})
	inputs = soup.find_all('input')
	

	homeworks = get_options(homework_select)
	questions = get_options(questions_select)

	hcache = {hw[0]:hw[1] for hw in homeworks}
	qcache = {q[0]:q[1] for q in questions}

	print("Submitting %s for class %s..."%(filename, course['value']))

	possible = hcache.keys()
	hchoice = options[ARGS.HOMEWORK]

	if hchoice == None or hchoice not in possible:
		if hchoice!=None:
			print("You have chosen an unavilable homework. Please choose from this menu...")
		else:
			print("Choose the homework...")

		for hw in homeworks:
			print("%s: %s"%(hw[0], hcache[hw[0]]))

		while hchoice not in possible:
			print("Enter one of the values on the left: "),
			hchoice = str(raw_input())

		options[ARGS.HOMEWORK] = hchoice

	print("")

	possible = qcache.keys()
	qchoice = options[ARGS.QUESTION]

	if qchoice == None or qchoice not in possible:
		if qchoice!=None:
			print("You have chosen an unavilable question. Please choose from this menu...")
		else:
			print("Choose the question...")

		for q in questions:
			print("%s: %s"%(q[0], qcache[q[0]]))


		while qchoice not in possible:
			print("Enter one of the values on the left: "),
			qchoice = str(raw_input())

		options[ARGS.QUESTION] = qchoice

	print("")
	
	confirm = ""
	force = options[ARGS.FORCE]

	print("You have chosen to submit %s for %s. SunetID: %s.")

	while force!=True and confirm.lower()!='y' and confirm.lower()!='n':
		print("Confirm [y/n]: "%(qcache[qchoice], hcache[hchoice], options[ARGS.SUNETID])),
		confirm = raw_input()

	if confirm =='n':
		return

	payload = {}

	for item in inputs:
		try:
			payload[item['name']]=item['value']
		except:
			pass
		
	payload[PAGE_CONSTANTS.sunetid] = options[ARGS.SUNETID]
	payload[PAGE_CONSTANTS.hw] = hchoice
	payload[PAGE_CONSTANTS.q] = qchoice

	files = {}
	files[PAGE_CONSTANTS.userfile] = open(filename, 'rb')

	r = requests.post(URL, data=payload, files=files)	

	if "File was successfully uploaded. Thank you for your submission." in r.text:
		print "Success!"
	else:
		print "Error!"

	if options[ARGS.VERBOSE]:
		print r.text

	print "Status %d"%r.status_code

if __name__=="__main__":
	main(sys.argv[1:])
