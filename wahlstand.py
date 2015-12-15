#!/usr/bin/env python3

# wahlstand.py does the wahlstand


import sys
import os.path
import re
import time
import datetime
from copy import deepcopy

# returns string representation of a HTML table containing the ballot box number,
# the ballot box name, and the number of votes for each list at each of the ballot
# boxes.
def html_table(headers, data, indices, prevdata=None, start=None, end=None):
	if(prevdata == None):
		comp = False
	else:
		comp = True
	
	if(start==None):
		start = 0
	if(end==None or end >= len(data)):
		end = len(data)
	
	if indices > len(headers):
		indices = len(headers)
	
	table = ""
	
	table += "<table class='table table-hover table-condensed'>\n<thead>"
	table += "	<tr>"
	
	i = 0
	for item in headers:
		if(i < indices):
			cls = ""
		else:
			cls = " class='list'"
		i += 1
		
		table += "<th{0}>{1}</th>".format(cls, item)
	table += "</tr>\n</thead>\n<tbody>"
	
	keys = list(data.keys())
	
	for key in keys[start:end]:
		line = data[key]
		if(comp):
			oldline = prevdata[key]
			if(len(line) == len(headers) and len(oldline) != len(headers)):
				table += "	<tr class='success'>"
			else:
				table += "	<tr>"
		else:
			table += "	<tr>"
		if(len(line) == len(headers)):
			i = 0
			for hi in headers:
				if(i < indices):
					cls = ""
				else:
					cls = " class='list'"
				i += 1
				
				table += "<td{0}>{1}</td>".format(cls, line[hi])
		elif(len(line) >= indices):
			for i in range(indices):
				table += "<td>{0}</td>".format(line[headers[i]])
			for i in range(indices, len(headers)):
				table += "<td> </td>"
		else:
			for i in range(len(headers)):
				table += "<td>ERR</td>"
		
		table += "</tr>\n"
	table += "</tbody>\n</table>\n"
	
	return table

def html_delta_table(headers, deltadata, indices):	
	if indices > len(headers):
		indices = len(headers)
	
	table = ""
	
	table += "<table class='table table-hover table-condensed'>\n<thead>"
	table += "	<tr>"
	
	i = 0
	for item in headers:
		if(i < indices):
			cls = ""
		else:
			cls = " class='list'"
		i += 1
		
		table += "<th{0}>{1}</th>".format(cls, item)
	table += "</tr>\n</thead>\n<tbody>"
	
	keys = list(deltadata.keys())
	
	for key in keys:
		line = deltadata[key]
		table += "	<tr>"
		if(len(line) == len(headers)):
			i = 0
			for hi in headers:
				item = line[hi]
				if(i < indices):
					cls = ""
				else:
					cls = " class='list'"
					item = int(item)
					if(item < 0):
						cls = " class='list text-danger'"
					if(item > 0):
						cls = " class='list text-success'"
						item = '+'+str(item)
				i += 1
				
				table += "<td{0}>{1}</td>".format(cls, item)
		elif(len(line) >= indices):
			for i in range(indices):
				table += "<td>{0}</td>".format(line[headers[i]])
			for i in range(indices, len(headers)):
				table += "<td> </td>"
		else:
			for i in range(len(headers)):
				table += "<td>ERR</td>"
		
		table += "</tr>\n"
	table += "</tbody>\n</table>\n"
	
	return table

def get_barchart_array(headers, data, colors, indices):
	lists = headers[indices:]
	colors = dict(zip(headers[indices:], colors[indices:]))
	
	barlist = list()
	
	for key in data:
		line = data[key]
		if(len(line) == len(headers)):
			d = list()
			for listname in lists:
				d.append({"label" : listname, "value" : int(line[listname]), "color" : colors[listname]})
			barlist.append(d)
		else:
			d = list()
			for listname in lists:
				d.append({"label" : listname, "value" : 0, "color" : colors[listname]})
			barlist.append(d)
	return barlist

def get_votetable(headers, data, indices, bbox):
	lists = headers[indices:]
	
	line = data[bbox]
	
	table = '''<table class="table table-bordered">
				<tr>'''
					
	if(len(line) == len(headers)):
		for listname in lists:
			table += '<td>{0}</td>\n'.format(line[listname])
		table += '</tr>\n<tr>'
	else:
		for listname in lists:
			table += '<td>-</td>\n'
	
	table += '</tr>\n<tr>' 
	for listname in lists:
		table += '<th>{0}</th>\n'.format(listname)
	
	table += '</tr>\n</table>'
	return table

# for each list: calculate total of votes and return in a dictionary
def bboxsum(headers, data, indices, listcount):
	lists = headers[indices:indices+listcount]
	
	bboxsum = {}
	for list in lists:
		bboxsum[list] = 0
	
	for line in data.values():
		if(len(line) == len(headers)):
			for list in lists:
				bboxsum[list] += int(line[list])
	
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
def diagdata(headers, data, colors, indices, listcount, seats):
	listvotes = bboxsum(headers, data, indices, listcount)
	seats = stlgs(listvotes, seats)
	colors = dict(zip(headers[indices:indices+listcount], colors[indices:indices+listcount]))
	
	diagdata = list()
	for listname in headers[indices:indices+listcount]:
		diagdata.append({"label" : listname, "value" : seats[listname], "color" : colors[listname]})
	
	return diagdata
	

def get_vote_count(data, headers, indices):
	listheaders = headers[indices:]
	
	count = 0
	for line in data.values():
		if(len(line) == len(headers)): #data available
			for header in listheaders:
				count += int(line[header])
	return count

def get_invalid_count(data, invalid_key):
	count = 0
	for line in data.values():
		if(len(line) == len(headers)): #data available
			count += int(line[invalid_key])
	return count

def get_abstentions_count(data, abstentions_key):
	count = 0
	for line in data.values():
		if(len(line) == len(headers)): #data available
			count += int(line[abstentions_key])
	return count

def get_list_count(data, list_key):
	count = 0
	for line in data.values():
		if(len(line) == len(headers)): #data available
			count += int(line[list_key])
	return count

def get_html_summary_result_table(headers, data, indices, listcount, invalid_key, abstentions_key, deltadata):
	voters_count = 33581
	vote_count = get_vote_count(data, headers, indices)
	invalid_count = get_invalid_count(data, invalid_key)
	valid_count = vote_count - invalid_count
	abstentions_count = get_abstentions_count(data, abstentions_key)
	participation = vote_count / voters_count * 100
	
	d_voters_count = voters_count - 32265
	d_vote_count = get_vote_count(deltadata, headers, indices)
	d_invalid_count = get_invalid_count(deltadata, invalid_key)
	d_valid_count = d_vote_count - d_invalid_count
	d_abstentions_count = get_abstentions_count(deltadata, abstentions_key)
	d_participation = participation - 13.2
	
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

def get_html_list_result_table(headers, data, indices, listcount, deltadata):
	listnames = headers[indices:listcount+indices]
	
	table = '''<div class="col-md-6 col-md-offset-3"><table class="table table-bordered table-hover">
	<tr><th>Liste</th><th>Stimmen</th><th>+/-</th></tr>'''
	for listname in listnames:
		delta_value = get_list_count(deltadata, listname)
		delta_cls = ''
		if(delta_value<0):
			delta_cls = ' class="text-danger"'
		elif(delta_value>0):
			delta_cls = ' class="text-success"'
			delta_value = '+'+str(delta_value)
		table += '<tr><td>{0}</td><td>{1}</td><td{3}>{2}</td></tr>\n'.format(listname, get_list_count(data, listname), delta_value, delta_cls)
	table += '</table></div>\n<div class="clearfix"></div>'
	
	return table

def data_delta(current, last):
	delta = deepcopy(current)
	
	for linekey in delta:
		for key in delta[linekey]:
			if(key not in ('Urne', 'Nr.')):
				delta[linekey][key] = int(delta[linekey][key]) - int(last[linekey][key])
	
	return delta
	

 # # # # #
#  MAIN  #
 # # # # #

#
# COMMAND LINE PARAMETERS
#
if(len(sys.argv) == 2):
	filename = sys.argv[1]
else:
	filename = "currentelection.csv"

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

	fobj = open(filename+".prev", "r")

	# extract list names
	firstline = fobj.readline()
	headers = re.split("\t+", firstline.rstrip())

	secondline = fobj.readline()


	prevdata = {} # this holds all data from previous run

	linenr = 1
	for line in fobj:
		linenr += 1
		items = re.split("\t+", line.rstrip())
		
		if(len(items) < len(headers) and len(items) > 1):
			prevdata[int(items[0])] = {headers[0] : items[0], headers[1] : items[1]}
		elif(len(items) == len(headers)):
			prevdata[int(items[0])] = dict(zip(headers, items))
		else:
			print("Wrong format at line {0}. Fix or delete {1}.prev and try again".format(linenr, filename))
			fobj.close()
			sys.exit(1)

	fobj.close()

#
# CREATE DATASTRUCTURE FROM [filename]
# AND STORE AS data
#
print("Reading {0}".format(filename))

fobj = open(filename, "r")
oldfile = open(filename+".prev", "w")

# extract list names
firstline = fobj.readline()
headers = re.split("\t+", firstline.rstrip())
oldfile.write(firstline)

# extract diagram colors of lists
secondline = fobj.readline()
colors = re.split("\t+", secondline.rstrip())
oldfile.write(secondline)


data = {} # this holds all the current data

linenr = 1
for line in fobj:
	oldfile.write(line)
	linenr += 1
	items = re.split("\t+", line.rstrip())
	
	if(len(items) < len(headers) and len(items) > 1): # no data for this ballot box yet
		data[int(items[0])] = {headers[0] : items[0], headers[1] : items[1]}
		
	elif(len(items) == len(headers)): # regular line with data for every list
		data[int(items[0])] = dict(zip(headers, items))
		
	else:
		print("Wrong format at line {0}".format(linenr))
		fobj.close()
		oldfile.close()
		sys.exit(1)

fobj.close()
oldfile.close()

#	
# CREATE DATASTRUCTURE FROM lastelection.csv IF PRESENT
# AND STORE AS prevdata
#
lastelectionfile = 'lastelection.csv'

if(not os.path.isfile(lastelectionfile)):
	lastelectiondata = None
else:
	print("Reading {0}".format(lastelectionfile))

	fobj = open(lastelectionfile, "r")

	# extract list names
	firstline = fobj.readline()
	headers = re.split("\t+", firstline.rstrip())

	secondline = fobj.readline()


	lastelectiondata = {} # this holds all data from last election

	linenr = 1
	for line in fobj:
		linenr += 1
		items = re.split("\t+", line.rstrip())
		
		if(len(items) < len(headers) and len(items) > 1):
			lastelectiondata[int(items[0])] = {headers[0] : items[0], headers[1] : items[1]}
		elif(len(items) == len(headers)):
			lastelectiondata[int(items[0])] = dict(zip(headers, items))
		else:
			print("Wrong format at line {0}. Fix or delete {1}.prev and try again".format(linenr, filename))
			fobj.close()
			sys.exit(1)

	fobj.close()

deltadata = data_delta(data, lastelectiondata)

#
# CREATE HTML OUTPUT FROM TEMPLATEs
#
print("Writing single html file from template")

content = html_table(headers, data, 2, prevdata)

deltatable = html_delta_table(headers, deltadata, 2)

summary = get_html_summary_result_table(headers, data, 2, 5, "Ungültig", "Enthaltung", deltadata)
summary += "\n\n\n"
summary += get_html_list_result_table(headers, data, 2, 5, deltadata)

diagramdata = diagdata(headers, data, colors, 2, 5, 43)

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
			<h1>{1} <small>Urne {0}</small> {3}</h1>
			
			<svg class="chart{0}"></svg>
			
			{2}
		</div>

	</div>'''
	
	
tabul_all = ''
tabcontent_all = ''

for key in data:
	line = data[key]
	votetable = get_votetable(headers, data, 2, key)
	
	isnewlabel = ''
	if(prevdata != None):
		currline = data[key]
		oldline  = prevdata[key] 
		if(len(currline) != len(oldline)):
			isnewlabel = ' <span class="label label-primary">Neu</span>'
	
	tabcontent_all += (tabcontent.format(key, line[headers[1]], votetable, isnewlabel) + "\n")
	
	if(len(line) == len(headers)):
		hasdataclass = ' class="hasdata"'
	else:
		hasdataclass = '';
		
	tabul_all += (tabul.format(key, hasdataclass) + "\n")
	
	
bardata = get_barchart_array(headers, data, colors, 2)

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


sys.exit(0)