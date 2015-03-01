from os import listdir
import json
import os


def find_current_file(name, path):
	if os.path.exists(path):
		files = listdir(path)
	else:
		#os.makedirs(path)
		return 1 , path + '/' + name + '_1.json'

	files_of_interest = []

	for f in files:
		if name in f:
			files_of_interest.append(f)

	if len(files_of_interest) == 0:
		return 1, path + '/' + name + '_1.json'

	d = []
	for f in files:
		f = f.replace('.json', '')
		try:
			n = int(f.replace(name+'_', ''))
			d.append(n)
		except ValueError:
			pass

	return max(d), path + '/' + name + '_' + str(max(d)) + '.json'

def find_nth_file(name, path, index):
	return path + '/' + name + '_' + str(index)+'.json'



def find_num_of_entries_of_current_file(filepath):
	handle = open(filepath, 'r')
	handle.seek(0)
	content = json.load(handle)
	return len(content)


def find_list_of_files(name, path):
	files = listdir(path)

	files_of_interest = []

	for f in files:
		if name in f:
			files_of_interest.append(f)

	return files_of_interest





