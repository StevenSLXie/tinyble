from tinyble.tinyble import Tinyble
from tinyble.query import where

def test_one_collection(db):
	collection = db.collection('example')

	collection.insert({'int': 1, 'string': 'a'})
	collection.insert({'int': 2, 'string': 'b'})

	assert collection.get(where('int')==1)['string'] == 'a'
	assert collection.get(where('string')=='b')['int'] == 2

	collection.clear()

def test_multiple_collections(db):
	col1 = db.collection('example1')

	col1.insert({'int': 1, 'string': 'a'})
	col1.insert({'int': 2, 'string': 'b'})


	col2 = db.collection('example2')

	col2.insert({'int': 3, 'string': 'c'})
	col2.insert({'int': 4, 'string': 'd'})

	assert col1.get(where('int')==1)['string'] == 'a'
	assert col1.get(where('string')=='b')['int'] == 2

	assert col2.get(where('int')==3)['string'] == 'c'
	assert col2.get(where('string')=='d')['int'] == 4

	col1.clear()
	col2.clear()


def test_insert(db):
	col = db.collection('example')

	col.insert({'type': 'apple', 'number': 1})
	col.insert({'type': 'pineapple', 'number': 2})
	col.insert({'type': 'blueberry', 'number': 3})

	assert len(col.search(where('number')<4)) == 3
	assert col.get(where('number') == 1)['type'] == 'apple'
	assert col.get(where('type') == 'pineapple')['number'] == 2

	col.clear()

def test_update(db):
	'''
	passed.
	But a workaround is used in write_in_page

	'''
	col = db.collection('example')

	col.insert({'type': 'apple', 'number': 1})
	col.insert({'type': 'pineapple', 'number': 2})
	col.insert({'type': 'blueberry', 'number': 3})

	assert col.get(where('type') == 'pineapple')['number'] == 2
	col.update({'number':10}, cond= where('type')=='pineapple')
	assert col.get(where('type') == 'pineapple')['number'] == 10

	col.clear()

def test_remove(db):

	col = db.collection('example')

	col.insert({'type': 'apple', 'number': 1})
	col.insert({'type': 'pineapple', 'number': 2})
	col.insert({'type': 'blueberry', 'number': 3})

	col.remove(eids=[3])

	col.insert({'type': 'mango', 'number': 4})

	col.remove(cond=where('number')<4)

	assert len(col.all()) == 1
	assert col.get(where('type') == 'mango')['number'] == 4

	col.clear()

def test_get(db):

	col = db.collection('example')

	col.insert({'type': 'apple', 'number': 1})
	col.insert({'type': 'pineapple', 'number': 2})
	col.insert({'type': 'blueberry', 'number': 3})

	assert col.get(where('type') == 'apple')['number'] == 1
	assert col.get(where('number') == 2)['type'] == 'pineapple'

	col.clear()
