#!/usr/bin/env python3

# wahlstand.py does the wahlstand


import sys
import os.path
import re
import time
import datetime
from copy import deepcopy
import json
import shutil

config = None

with open('config.json') as jsonfile:
	config = json.load(jsonfile)
	
class Election:
	def __init__(self):
		self.bboxes = {}
		self.lists = {}
		self.votes = {}
		
	def readFromFile(self, filename):
		with open(filename, 'r') as infile:
			firstline = infile.readline()
			listnames = re.split("\t+", firstline.rstrip())
			
			

			secondline = infile.readline()
			colors = re.split("\t+", secondline.rstrip())
			
			if(len(listnames) != len(colors)):
				print("Wrong data format: Not as many colors as lists found. Exiting.")
				sys.exit(1)
			
			listid = 0
			for i in range(len(listnames)):
				if(listnames[i][0] != "!"):
					self.lists[listid] = List(listid, listnames[i], colors[i])
					listid += 1

			linenr = 2
			for line in infile:
				linenr += 1
				items = re.split("\t+", line.rstrip())
				
				if(len(items) < len(self.lists)+2 and len(items) > 1):
					bboxid = int(items[0])
					bboxname = items[1]
					
					self.bboxes[bboxid] = BallotBox(bboxid, bboxname)
					self.votes[bboxid] = None
				elif(len(items) == len(self.lists)+2):
					bboxid = int(items[0])
					bboxname = items[1]
					
					self.bboxes[bboxid] = BallotBox(bboxid, bboxname)
					self.votes[bboxid] = {}
					for i in range(len(items[2:])):
						self.votes[bboxid][i] = int(items[i+2])
				else:
					print("Wrong format at line {0}. Fix or delete {1}.prev and try again".format(linenr, filename))
					sys.exit(1)
	def getVoteCount(self):
		sum = 0
		for line in self.votes:
			if(self.votes[line] != None):
				for listid in self.lists:
					sum += self.votes[line][listid]
		return sum
	
	def getInvalidCount(self, invalid_key="Ungültig"):
		invalid_id = 0
		for listid in self.lists:
			if(self.lists[listid].name == invalid_key):
				invalid_id = listid
		sum = 0
		for line in self.votes:
			if(self.votes[line] != None):
				sum += self.votes[line][invalid_id]
		return sum
	
	def getAbstentionsCount(self, abstentions_key="Enthaltung"):
		abstentions_id = 0
		for listid in self.lists:
			if(self.lists[listid].name == abstentions_key):
				abstentions_id = listid
		sum = 0
		for line in self.votes:
			if(self.votes[line] != None):
				sum += self.votes[line][abstentions_id]
		return sum

class BallotBox:
	def __init__(self, id, name):
		self.id = id
		self.name = name

class List:
	def __init__(self, id, name, color):
		self.id = id
		self.name = name
		self.color = color
		self.auxiliary = False
		if(name[0] == "#"):
			self.name = name[1:]
			self.auxiliary = True

def copy_files_raw(config):
	files = []
	files.append(config['file_sp_current'])
	for f in config['files_ua']:
		files.append(f)
	
	for f in files:
		shutil.copy(f, "./html/raw/")
	

# returns string representation of a HTML table containing the ballot box number,
# the ballot box name, and the number of votes for each list at each of the ballot
# boxes.
def html_table(data):
	table = ""
	
	table += "<table class='table table-hover table-condensed'>\n<thead>"
	table += "	<tr><td>Nr.</td><td>Urne</td>"
	
	for list in data.lists:
		table += "<th class='list'>{0}</th>".format(data.lists[list].name)
	table += "</tr>\n</thead>\n<tbody>"
	
	for bboxid in sorted(data.bboxes.keys()):
		table += "<tr><td>{0.id}</td><td>{0.name}</td>".format(data.bboxes[bboxid])
		
		if(data.votes[bboxid] != None):
			for listid in sorted(data.lists.keys()):
				table += "<td class='list'>{0}</td>".format(data.votes[bboxid][listid])
		else:
			for listid in sorted(data.lists.keys()):
				table += "<td></td>"
				
			
		table += "</tr>\n"
		
	table += "</tbody>\n</table>\n"
	
	return table

def html_delta_table(deltadata):
	
	table = ""
	
	table += "<table class='table table-hover table-condensed'>\n<thead>"
	table += "	<tr><td>Nr.</td><td>Urne</td>"
	
	for list in deltadata.lists:
		table += "<th class='list'>{0}</th>".format(deltadata.lists[list].name)
	table += "</tr>\n</thead>\n<tbody>"
	
	for bboxid in sorted(deltadata.bboxes.keys()):
		table += "<tr><td>{0.id}</td><td>{0.name}</td>".format(deltadata.bboxes[bboxid])
		
		if(deltadata.votes[bboxid] != None):
			for listid in sorted(deltadata.lists.keys()):
				colorclass = ""
				if(deltadata.votes[bboxid][listid] < 0):
					colorclass = " text-danger"
				if(deltadata.votes[bboxid][listid] > 0):
					colorclass = " text-success"
				table += "<td class='list{1}'>{0}</td>".format(deltadata.votes[bboxid][listid], colorclass)
		else:
			for listid in sorted(deltadata.lists.keys()):
				table += "<td></td>"
				
			
		table += "</tr>\n"
		
	table += "</tbody>\n</table>\n"
	
	return table

def get_barchart_array(data, auxiliary=True):
	lists = data.lists
	
	barlist = list()
	
	for bboxid in data.votes:
		line = data.votes[bboxid]
		if(line != None):
			d = list()
			for listid in lists:
				if(auxiliary or not lists[listid].auxiliary):
					d.append({"label" : lists[listid].name, "value" : line[listid], "color" : lists[listid].color})
			barlist.append(d)
		else:
			d = list()
			for listname in lists:
				if(auxiliary or not lists[listid].auxiliary):
					d.append({"label" : lists[listid].name, "value" : 0, "color" : lists[listid].color})
			barlist.append(d)
	return barlist

def get_votetable(data, bbox):
	lists = data.lists
	
	line = data.votes[bbox]
	
	table = '''<table class="table table-bordered">
				<tr>'''
					
	if(line != None):
		for listid in lists:
			table += '<td>{0}</td>\n'.format(line[listid])
		table += '</tr>\n<tr>'
	else:
		for listid in lists:
			table += '<td>-</td>\n'
	
	table += '</tr>\n<tr>' 
	for listid in lists:
		table += '<th>{0}</th>\n'.format(lists[listid].name)
	
	table += '</tr>\n</table>'
	return table

# for each list: calculate total of votes and return in a dictionary
def bboxsum(data):
	
	
	bboxsum = {}
	for listid in data.lists:
		if(not data.lists[listid].auxiliary):
			bboxsum[listid] = 0
	
	for bboxid in data.votes:
		if(data.votes[bboxid] != None):
			for listid in data.lists:
				if(not data.lists[listid].auxiliary):
					bboxsum[listid] += data.votes[bboxid][listid]
	
	return bboxsum

# do the Sainte-Laguë/Schepers method to determine the number of
# seats for each list (bboxsum is a dictionary containing pairs of
# list:numberofvotes)
def stlgs(bboxsum, seats):
	div = float(1)
	for votes in bboxsum.values():
		div += votes
	
	# div starts with a value where sum will certainly
	# be smaller than seats.
	
	div += 1000
	sum = 0
	
	while(sum<seats):
		div = max(div-1000, 0.00001)
		sum = 0
		for list in bboxsum.values():
			sum += round(list/div)
	
	while(sum>seats):
		div += 100
		sum = 0
		for list in bboxsum.values():
			sum += round(list/div)
			
	while(sum<seats):
		div = max(div-10, 0.00001)
		sum = 0
		for list in bboxsum.values():
			sum += round(list/div)
			
	while(sum>seats):
		div += 1
		sum = 0
		for list in bboxsum.values():
			sum += round(list/div)
	
	while(sum<seats):
		div = max(div-0.1, 0.00001)
		sum = 0
		for list in bboxsum.values():
			sum += round(list/div)
	
	while(sum>seats):
		div += 0.01
		sum = 0
		for list in bboxsum.values():
			sum += round(list/div)
	
	seats = dict(bboxsum)
	for key in seats:
		seats[key] = round(seats[key]/div)
	print("A divisor has been found: {0}".format(div))
	return seats

# return a list of dictionaries providing the data for the diagram
def diagdata(data, seats=0, apply_stlgs=True):
	listvotes = bboxsum(data)
	if(apply_stlgs):
		seats = stlgs(listvotes, seats)
	else:
		seats = listvotes
	
	diagdata = list()
	for listid in data.lists:
		if(not data.lists[listid].auxiliary):
			diagdata.append({"label" : data.lists[listid].name, "value" : seats[listid], "color" : data.lists[listid].color})
	
	return diagdata
	

def get_vote_count(data):
	return data.getVoteCount()

def get_invalid_count(data, invalid_key):
	return data.getInvalidCount(invalid_key)

def get_abstentions_count(data, abstentions_key):
	return data.getAbstentionsCount(abstentions_key)

def get_list_count(data, list_id):
	count = 0
	for bboxid in data.votes:
		if(data.votes[bboxid] != None):
			count += data.votes[bboxid][list_id]
	return count

def get_html_summary_result_table(data, config, deltadata=None, invalid_key="Ungültig", abstentions_key="Enthaltung"):

	voters_count = config['count_voters_current']
	vote_count = get_vote_count(data)
	invalid_count = get_invalid_count(data, invalid_key)
	valid_count = vote_count - invalid_count
	abstentions_count = get_abstentions_count(data, abstentions_key)
	participation = vote_count / voters_count * 100
	
	if(deltadata != None):
	
		d_voters_count = voters_count - config['count_voters_prev']
		d_vote_count = get_vote_count(deltadata)
		d_invalid_count = get_invalid_count(deltadata, invalid_key)
		d_valid_count = d_vote_count - d_invalid_count
		d_abstentions_count = get_abstentions_count(deltadata, abstentions_key)
		d_participation = participation - config['participation_prev']
		
		d_voters_count_cls = ''
		d_vote_count_cls = ''
		d_invalid_count_cls = ''
		d_valid_count_cls = ''
		d_abstentions_count_cls = ''
		d_participation_cls = ''
		
		if(d_voters_count<0):
			d_voters_count_cls = ' class="text-danger"'
		elif(d_voters_count>0):
			d_voters_count_cls = ' class="text-success"'
			d_voters_count = '+'+str(d_voters_count)
			
		if(d_vote_count<0):
			d_vote_count_cls = ' class="text-danger"'
		elif(d_vote_count>0):
			d_vote_count_cls = ' class="text-success"'
			d_vote_count = '+'+str(d_vote_count)
			
		if(d_invalid_count<0):
			d_invalid_count_cls = ' class="text-danger"'
		elif(d_invalid_count>0):
			d_invalid_count_cls = ' class="text-success"'
			d_invalid_count = '+'+str(d_invalid_count)
			
		if(d_valid_count<0):
			d_valid_count_cls = ' class="text-danger"'
		elif(d_valid_count>0):
			d_valid_count_cls = ' class="text-success"'
			d_valid_count = '+'+str(d_valid_count)
			
		if(d_abstentions_count<0):
			d_abstentions_count_cls = ' class="text-danger"'
		elif(d_abstentions_count>0):
			d_abstentions_count_cls = ' class="text-success"'
			d_abstentions_count = '+'+str(d_abstentions_count)
			
		if(d_participation<0):
			d_participation_cls = ' class="text-danger"'
		elif(d_participation>0):
			d_participation_cls = ' class="text-success"'
			d_participation = '+'+str(d_participation)

	
	
		return '''<div class="col-md-6 col-md-offset-3"><table class="table table-bordered table-hover">
		<tr><td>Wahlberechtigte</td><td>{0}</td><td{12}>{6}</td></tr>
		<tr><td>Abgegebene Stimmen</td><td>{1}</td><td{13}>{7}</td></tr>
		<tr><td>Ungültige Stimmen</td><td>{2}</td><td{14}>{8}</td></tr>
		<tr><td>Gültige Stimmen</td><td>{3}</td><td{15}>{9}</td></tr>
		<tr><td>Enthaltungen</td><td>{4}</td><td{16}>{10}</td></tr>
		<tr><td>Wahlbeteiligung</td><td>{5:10.2f} %</td><td{17}>{11:10.2f} </td></tr>
		</table></div>\n<div class="clearfix"></div>'''.format(voters_count,
				vote_count,
				invalid_count,
				valid_count,
				abstentions_count,
				participation,
				d_voters_count,
				d_vote_count,
				d_invalid_count,
				d_valid_count,
				d_abstentions_count,
				d_participation,
				d_voters_count_cls,
				d_vote_count_cls,
				d_invalid_count_cls,
				d_valid_count_cls,
				d_abstentions_count_cls,
				d_participation_cls)
	else:
		return '''<div class="col-md-6 col-md-offset-3"><table class="table table-bordered table-hover">
		<tr><td>Wahlberechtigte</td><td>{0}</td></tr>
		<tr><td>Abgegebene Stimmen</td><td>{1}</td></tr>
		<tr><td>Ungültige Stimmen</td><td>{2}</td></tr>
		<tr><td>Gültige Stimmen</td><td>{3}</td></tr>
		<tr><td>Enthaltungen</td><td>{4}</td></tr>
		<tr><td>Wahlbeteiligung</td><td>{5:10.2f} %</td></tr>
		</table></div>\n<div class="clearfix"></div>'''.format(voters_count,
				vote_count,
				invalid_count,
				valid_count,
				abstentions_count,
				participation)

def get_html_list_result_table(data, deltadata=None):
	
	table = '<div class="col-md-6 col-md-offset-3"><table class="table table-bordered table-hover">'
	
	
	if(deltadata != None):
		table += '<tr><th>Liste</th><th>Stimmen</th><th>+/-</th></tr>'
	else:
		table += '<tr><th>Option</th><th>Stimmen</th></tr>'
		
	for listid in data.lists:
		listname = data.lists[listid].name
		if(deltadata != None):
			delta_value = get_list_count(deltadata, listid)
			delta_cls = ''
			if(delta_value<0):
				delta_cls = ' class="text-danger"'
			elif(delta_value>0):
				delta_cls = ' class="text-success"'
				delta_value = '+'+str(delta_value)
		table += '<tr><td>{0}</td><td>{1}</td>'.format(listname, get_list_count(data, listid))
		if(deltadata != None):
			table += '<td{1}>{0}</td>'.format(delta_value, delta_cls)
		table += '</tr>\n'
	table += '</table></div>\n<div class="clearfix"></div>'
	
	return table

def data_delta(current, last):
	delta = deepcopy(current)
	
	for linekey in delta.votes:
		if(delta.votes[linekey] != None):
			for key in delta.votes[linekey]:
				delta.votes[linekey][key] = int(delta.votes[linekey][key]) - int(last.votes[linekey][key])
	
	return delta
	

 # # # # #
#  MAIN  #
 # # # # #

#
# COMMAND LINE PARAMETERS
#
filename = config['file_sp_current']

if(not os.path.isfile(filename)):
	print("File {0} not found!".format(filename))
	sys.exit(1)


#	
# CREATE DATASTRUCTURE FROM [filename].prev IF PRESENT
# AND STORE AS prevdata
#
if(not os.path.isfile(filename+".prev")):
	prevdata = None
else:
	print("Reading {0}".format(filename+".prev"))
	
	prevdata = Election()
	prevdata.readFromFile(filename+".prev")

#
# CREATE DATASTRUCTURE FROM [filename]
# AND STORE AS data
#
print("Reading {0}".format(filename))

data = Election()
data.readFromFile(filename)

#	
# CREATE DATASTRUCTURE FROM lastelection.csv IF PRESENT
# AND STORE AS prevdata
#
lastelectionfile = config['file_sp_prev']

if(not os.path.isfile(lastelectionfile)):
	lastelectiondata = None
else:
	print("Reading {0}".format(lastelectionfile))

	lastelectiondata = Election()
	lastelectiondata.readFromFile(lastelectionfile)

deltadata = data_delta(data, lastelectiondata)

#
# CREATE HTML OUTPUT FROM TEMPLATEs
#
print("Writing single html file from template")

content = html_table(data)

deltatable = html_delta_table(deltadata)

summary = get_html_summary_result_table(data, config, deltadata, "Ungültig", "Enthaltung" )
summary += "\n\n\n"
summary += get_html_list_result_table(data, deltadata)

diagramdata = diagdata(data, 43)

template = open("template_index.html", "r")
htmlfile = open("html/index.html", "w")

for line in template:
	# replace placeholders
	line = line.replace("%CONTENT%", content)
	line = line.replace("%DELTATABLE%", deltatable)
	line = line.replace("%SUMMARY%", summary)
	line = line.replace("%DIAGRAMDATA%", str(diagramdata))
	line = line.replace("%DATETIME%", datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'))
	htmlfile.write(line)
	
template.close()
htmlfile.close()



print("Writing tabbed stuff")

tabul = '<li><a href="#urne{0}" data-toggle="tab"{1}>{0}</a></li>'

tabcontent = '''<div class="tab-pane fade" id="urne{0}">
		<div class="jumbotron">
			<h1>{1} <small>Urne {0}</small></h1>
			
			<svg class="chart{0}"></svg>
			
			{2}
		</div>

	</div>'''
	
	
tabul_all = ''
tabcontent_all = ''

for bboxid in data.bboxes:
	bbox = data.bboxes[bboxid]
	votetable = get_votetable(data, bboxid)
	
	
	tabcontent_all += (tabcontent.format(bbox.id, bbox.name, votetable) + "\n")
	
	if(data.votes[bboxid] != None):
		hasdataclass = ' class="hasdata"'
	else:
		hasdataclass = '';
		
	tabul_all += (tabul.format(bbox.id, hasdataclass) + "\n")
	
	
bardata = get_barchart_array(data)

template = open("template_tabs.html", "r")
htmlfile = open("html/tabs.html", "w")

for line in template:
	# replace placeholders
	line = line.replace("%TABUL%", tabul_all)
	line = line.replace("%TABCONTENT%", tabcontent_all)
	line = line.replace("%DIAGRAMDATA%", str(diagramdata))
	line = line.replace("%BARDATA%", str(bardata))
	line = line.replace("%DATETIME%", datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'))
	htmlfile.write(line)

template.close()
htmlfile.close()

def get_ua_stat_table(data):
	table = "<table><tr>"
	for listid in sorted(data.lists):
		list = data.lists[listid]
		table += "<th>{0}</th>".format(list.name)
	table += "</tr>\n<tr>"
	
	for listid in sorted(data.lists):
		list = data.lists[listid]
		table += "<td>{0}</td>".format(data.votes.name)
	
	table += "</table>"

#
# CREATE UA HTML OUTPUT FROM TEMPLATEs
#
print("Writing single html file from UA template")

uatable = []
uastats = []
diagramdata = []
for uafile in config['files_ua']:
	uadata = Election()
	uadata.readFromFile(uafile)
	
	table = get_html_summary_result_table(uadata, config, None, "Ungültig", "Enthaltung" )
	uatable.append(table)

	stats = get_html_list_result_table(uadata, None)
	uastats.append(stats)
	
	
	diagramdata.append(diagdata(uadata, apply_stlgs=False))


ua1table = uatable[0]
ua2table = uatable[1]
ua3table = uatable[2]
ua1stats = uastats[0]
ua2stats = uastats[1]
ua3stats = uastats[2]
diagram1data = str(diagramdata[0])
diagram2data = str(diagramdata[1])
diagram3data = str(diagramdata[2])

template = open("template_ua.html", "r")
htmlfile = open("html/ua.html", "w")

for line in template:
	# replace placeholders
	line = line.replace("%UA1TABLE%", ua1table)
	line = line.replace("%UA1STATS%", ua1stats)
	line = line.replace("%DIAGRAM1DATA%", diagram1data)
	line = line.replace("%UA2TABLE%", ua2table)
	line = line.replace("%UA2STATS%", ua2stats)
	line = line.replace("%DIAGRAM2DATA%", diagram2data)
	line = line.replace("%UA3TABLE%", ua3table)
	line = line.replace("%UA3STATS%", ua3stats)
	line = line.replace("%DIAGRAM3DATA%", diagram3data)
	line = line.replace("%DATETIME%", datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'))
	htmlfile.write(line)
	
template.close()
htmlfile.close()

copy_files_raw(config)

sys.exit(0)