#!/usr/bin/env python
# coding=utf-8

# wahlstand.py does the wahlstand


import sys
import os.path
import re
import time
import datetime

# returns string representation of a HTML table containing the ballot box number,
# the ballot box name, and the number of votes for each list at each of the ballot
# boxes.
def html_table(headers, data, indices, prevdata=None):
	if(prevdata == None):
		comp = False
	else:
		comp = True
	
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
	
	for key in data:
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

# for each list: calculate total of votes and return in a dictionary
def bboxsum(headers, data, indices):
	lists = headers[indices:]
	
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
def diagdata(headers, data, colors, indices, seats):
	listvotes = bboxsum(headers, data, indices)
	seats = stlgs(listvotes, seats)
	colors = dict(zip(headers[indices:], colors[indices:]))
	
	diagdata = list()
	for listname in headers[indices:]:
		diagdata.append({"label" : listname, "value" : seats[listname], "color" : colors[listname]})
	
	return diagdata
	
	


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

	fobj = open(filename+".prev", "r", -1, "utf_8")

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

fobj = open(filename, "r", -1, "utf_8")
oldfile = open(filename+".prev", "w", -1, "utf_8")

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
# CREATE HTML OUTPUT FROM TEMPLATE
#
print("Writing html file from template")

content = html_table(headers, data, 2, prevdata)

diagramdata = diagdata(headers, data, colors, 2, 43)

template = open("template.html", "r", -1, "utf_8")
htmlfile = open("html/index.html", "w", -1, "utf_8")

for line in template:
	# replace placeholders
	line = line.replace("%CONTENT%", content)
	line = line.replace("%DIAGRAMDATA%", str(diagramdata))
	line = line.replace("%DATETIME%", datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'))
	htmlfile.write(line)
	
template.close()
htmlfile.close()

sys.exit(0)