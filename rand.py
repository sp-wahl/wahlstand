#! /usr/bin/env python3

import random

LISTS = 10
BALLOTBOXES = 25

votes = []

def split(number, items):
    k = []
    summ = 0
    for i in range(items):
        x = random.randint(0,int((number - summ) / 5)) + random.randint(0,int((number - summ) / 5)) + random.randint(0,int((number - summ) / 5))
        summ += x
        k.append(x)
    random.shuffle(k)
    return k

for listno in range(LISTS):
    votes.append(random.randint(1,900))

m = []
for listno in range(LISTS):
    l = split(votes[listno], BALLOTBOXES)
    m.append([])
    for bboxno in range(BALLOTBOXES):
        m[listno].append(l[bboxno])



for bboxno in range(BALLOTBOXES):
    line = ""
    for listno in range(LISTS):
        line += "{0}\t\t".format(m[listno][bboxno])
    print(line)