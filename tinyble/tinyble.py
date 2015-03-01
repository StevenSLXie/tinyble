from JSONStorage import JSONStorage
from Collection import Collection
import os


'''
The Tinyble Class
'''


class Tinyble(object):
	def __init__(self, db_name):
		self.db_name = db_name
		if not os.path.exists(os.getcwd() + '/' + db_name):
			os.makedirs(os.getcwd() + '/' + db_name)

	def collection(self, name='_default_collection'):
		collection = Collection(name, self)

		return collection
