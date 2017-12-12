import json
import uuid
import os
import csv
import pathlib
from os import listdir
from os.path import isfile, join

def saveids(env, type, ids):
	path = './env/{env}/history/{type}/'.format(env=env,type=type)
	pathlib.Path(path).mkdir(parents=True, exist_ok=True)
	id = str(uuid.uuid4())
	filename = path + id + '.csv'
	print('saving new record ids in ' + filename)
	with open(filename, mode='w', encoding='utf-8') as f:
		for id in ids:
			csv.writer(f).writerow([id])

def getfiles(env, type):
	path = './env/{env}/history/{type}/'.format(env=env,type=type)
	return [join(path, f) for f in listdir(path) if isfile(join(path, f))]

def loadallids(env, type):
	ids = []
	for filename in getfiles(env,type):
		print('reading ' + filename)
		with open(filename,'r') as f:
			id_from_file = [data[0] for data in csv.reader(f)]
			ids.extend(id_from_file)
	return ids

def clearhistory(env, type):
	for filename in getfiles(env,type):
		print('deleting ' + filename)
		os.remove(filename)
