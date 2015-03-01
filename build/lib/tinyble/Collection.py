import threading
import math
from JSONStorage import JSONStorage
from utils import find_current_file, find_num_of_entries_of_current_file, find_list_of_files, find_nth_file
from LRU import LRUCache
import os


class Element(dict):
	"""
	Represents an element stored in the database.
	This is a transparent proxy for database elements. It exists
	to provide a way to access an element's id via ``el.eid``.
	"""
	def __init__(self, value=None, eid=None, **kwargs):
		super(Element, self).__init__(**kwargs)

		if value is not None:
			self.update(value)
			self.eid = eid


class Collection(object):
	def __init__(self, name, database):


		# The maximum limit of each JSON file
		self.FILE_SIZE_LIMIT = 5

		# The write-in frequency
		self.WRITE_IN_FREQ = 0.2

		# The size for the query cache file
		self.QUERY_CACHE_SIZE_LIMIT = 20

		# The number of JSON files and the path for the current JSON file
		self.file_num, self.current_file = find_current_file(name, os.getcwd()+'/'+database.db_name)

		self.storage = JSONStorage(self.current_file)


		self.name = name
		self._db = database

		# Cache for the whole collection
		self._cache = {}

		# Cache for the latest file that is being used to write in
		self._current_cache = {}

		#Cache for the most frequently queried items
		# self._query_cache = LRUCache(self.QUERY_CACHE_SIZE_LIMIT)


		# Each entry has a unique id as the primary key

		existing_ids = self._read().keys()

		if existing_ids:
			self._last_id = max(i for i in existing_ids)
		else:
			self._last_id = 0

		self._load_query_cache()
		self.update_storage()

	def setting(self, file_size=None, query_cache_size=None, write_freq=None):
		if file_size is not None:
			self.FILE_SIZE_LIMIT = file_size

		if query_cache_size is not None:
			self.QUERY_CACHE_SIZE_LIMIT = query_cache_size

		if write_freq is not None:
			self.WRITE_IN_FREQ = write_freq

	def _load_query_cache(self):

		self.query_storage = JSONStorage(os.getcwd()+'/'+ self._db.db_name + '/' + self.name + '_query.json')
		self._query_cache = LRUCache(self.QUERY_CACHE_SIZE_LIMIT, self.query_storage.read(is_ordered_dict=True))

		print self._query_cache.items.keys()


	def update_storage(self):
		if len(self._current_cache) >= self.FILE_SIZE_LIMIT:
		# If we enter this function because of the file size limit, we do the following:
			## write to the file
			## create the next file
			## point our current storage block to the next file
			self.storage.write(dict(self._current_cache))
			# print time.ctime(), 'size limit'
			self._current_cache = {}
			self.file_num += 1
			self.storage = JSONStorage(os.getcwd()+'/'+ self._db.db_name + '/' + self.name + '_' + str(self.file_num) + '.json')
		else:
		# Else, it is just because of the timer expiration, we do the regular write-in
			# print time.ctime(), 'regular write-in', len(self._current_cache)

			self.storage.write(dict(self._current_cache))
			self.query_storage.write(self._query_cache.items)
			# print self._query_cache.items

		# Set the timer again. Make it periodic.
		self.t = threading.Timer(self.WRITE_IN_FREQ, self.update_storage)
		self.t.start()

	def process_element(self, func, cond=None, eid=None):
		data = self._read()

		if eid is not None:
			for i in eid:
				func(data, eid)

		else:
			for eid in list(data):
				if cond(data[eid]):
					func(data, eid)

		self._write(data)

	def _get_next_id(self):
		current = self._last_id + 1
		self._last_id = current

		return current

	def _read(self):

		if self._cache == {}:
		# When the current collection is first read, read it all at once to the cache.
			self._read_all()
		return self._cache


	def _read_all(self):
		for i in range(1, self.file_num+1):
			raw = JSONStorage(find_nth_file(self.name, os.getcwd()+'/'+self._db.db_name, i)).read()
			for key in list(raw):
				eid = int(key)
				self._cache[eid] = Element(raw[key], eid)
				if i == self.file_num:
					self._current_cache[eid] = Element(raw[key], eid)

	def _write(self, values):

		self.storage.write(values)

	def __len__(self):
		return len(self._read())

	def all(self):
		return list(self._read().values())

	def insert(self, value):

		eid = self._get_next_id()
		self._cache[eid] = value
		self._current_cache[eid] = value


		'''
		If the file in-use reaches the size limit, we do the following:
		1. cancel the timer
		2. enter the update_storage
		Otherwise, we can just wait until the timer expires
		'''
		if len(self._current_cache) >= self.FILE_SIZE_LIMIT:
			self.t.cancel()
			self.update_storage()

	def insert_multiple(self, values):
		for value in values:
			self.insert(value)

	def update(self, fields, cond=None, eids= None):

		'''
		Update can be performed by specifying eid or cond, or both.
		But at least one of them should be specified.
		'''

		if cond is None and eids is None:
			eids = self._cache.keys()

		if cond is not None:
			eids = self._select_to_be_updated_eid(cond, eids)

		pages_eid = self._group_eids(eids)

		self._update_cache(eids, pages_eid, fields)
		self._update_disk(pages_eid, fields)

	def _update_disk(self, pages_eid, fields, remove=False):
		# do the update for the files
		temp_caches = {}

		for page in pages_eid:
			temp_caches[page] = self._read_page(page)
			temp_caches[page] = self._write_in_page(fields, pages_eid[page], temp_caches[page], remove)

		for page in temp_caches:
			self._update_page(page, temp_caches[page])

	def _group_eids(self, eids):
		'''
		group eids based on which page it belongs to
		'''

		pages_eid = {}
		for i in eids:
			page = int(math.ceil(float(i)/float(self.FILE_SIZE_LIMIT)))
			if page not in pages_eid:
				pages_eid[page] = [i]
			else:
				pages_eid[page].append(i)

		return pages_eid

	def _select_to_be_updated_eid(self, cond, eids):

		# Given a condition, return a list of id that satisfies the condition
		filtered_ids = []

		if eids is None:
			# if edis not specified, iterate all possible eids
			for id in self._cache:
				if cond(self._cache[id]):
					filtered_ids.append(id)
		else:
			# check whether the given id satisfied the cond
			for id in eids:
				if cond(self._cache[id]):
					filtered_ids.append(id)
		return filtered_ids

	def _update_cache(self, eids, pages_eid, fields=None, remove=False):
		# update the cache first before write-in to the file

		for i in eids:
			if remove:
				self._cache.pop(i, None)
			else:
				self._cache[i].update(fields)
		for page in pages_eid:
			if page == self.file_num:
				for id in pages_eid[page]:
					if remove:
						self._current_cache.pop(id, None)
					else:
						self._current_cache[id].update(fields)


	def _read_page(self, page):

		'''
		Used for update()
		read every related page
		return a temp_cache
		'''

		page_content = JSONStorage(find_nth_file(self.name, os.getcwd()+'/'+self._db.db_name, page)).read()
		temp_cache = {}
		for key in list(page_content):
			id = int(key)
			temp_cache[id] = Element(page_content[key], id)
		return temp_cache

	def _write_in_page(self, fields, eids, temp_cache, remove=False):
		# write in the updated items
		for eid in eids:
			if remove:
				temp_cache.pop(eid, None)
			else:
				try:
					temp_cache[eid].update(fields)
				except KeyError:
					pass
		return temp_cache

	def _update_page(self, page, cache):

		'''
		Write in the temp_cache given by _read_page
		'''

		page_content = JSONStorage(find_nth_file(self.name, os.getcwd()+'/'+self._db.db_name, page))
		page_content.write(cache)

	def remove(self, cond=None, eids=None):

		if cond is None and eids is None:
			# this means removing all elements
			eids = self._cache.keys()

		if cond is not None:
			eids = self._select_to_be_updated_eid(cond, eids)

		pages_eid = self._group_eids(eids)

		self._update_cache(eids, pages_eid, fields=None, remove=True)

		self._update_disk(pages_eid, fields=None, remove=True)

	def search(self, cond):

		elements = self._query_cache.get(str(cond))

		if elements == -1:
			# print 'False'
			elements = [e for e in self.all() if cond(e)]
			self._query_cache.set(str(cond), elements)
		return elements

	def clear(self):
		self.remove()

	def get(self, cond, eid=None):

		if eid is not None:
			return self._cache[eid]

		elements = self.search(cond)

		if elements == []:
			return {}
		return elements[0]



