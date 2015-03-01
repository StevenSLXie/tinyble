import  collections

class LRUCache:
	def __init__(self, capacity, ordered_dict = None):
		self.capacity = capacity

		if ordered_dict is not None:
			self.items = ordered_dict
		else:
			self.items = collections.OrderedDict()

	def get(self, key):
		if not key in self.items:
			return -1
		value = self.items.pop(key)
		self.items[key] = value
		return value

	def set(self, key, value):
		try:
			self.items.pop(key)
		except KeyError:
			if len(self.items) >= self.capacity:
				self.items.popitem(last=False)
		self.items[key] = value

