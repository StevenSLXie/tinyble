#Tinyble

##Introduction
Tinyble is a super lightweight database inheriting [TinyDB](https://github.com/msiemens/tinydb). It is a document-oriented NoSQL but can also be used as a SQL database. It is most suitable for small applications where MongoDB is too way overkill.
The features are:

- Written in pure Python and works well with most Python versions
- Very small, stored in JSON format and requires no external server
- Different from TinyDB, flexible auto-paging is provided to enable fast write-in and read-out
- Combine in-memory caching with disk storage to trade-off speed and reliability

##Difference from TinyDB
TinyDB stores each table in a single JSON file. For every IO operation, the JSON file will be wholly read and rewritten. As the file size gets larger or when there are many write-in operations, the speed can be dramatically slow.
Tinyble uses a separate thread to manage all the write/update operations. Specifically, all newly-updated data will first be stored in memory and an internal timer expires, they will be batch-written in the JSON file. This reduces
the number of IO operations. Moreover, a limit on the JSON file size is imposed when the size exceeds the limit, a new JSON file is created. This limits the volume of each read operation.


The internal timer and the file size can be set by users.


##Version
The latest version is v0.1.4. The current version is still on experimental status. Please use it with caution. Please contact me if you find any bugs/problems.

###v0.1.4(07.03.2015)
- added the close() function

###v0.1.3(04.03.2015)
- fixed the print bug
- fixed the 'get' method bug

##How to install
The easiest way to install is to use
```
(sudo) pip install tinyble
```

in the command line tool.

##Working with Django
A very simple and ugly example showing the use of Tinyble with Django can be found in [Tinyble with Django](https://github.com/StevenSLXie/django_with_tinyble)

##Example

###Create a new database and a new collection

```Python
db = Tinyble('data')  # create a new database named "data"
collection = db.collection('example') # create a new collections under "data" named "example"


```

###Insert some data
```Python
col = db.collection('example')

col.insert({'type': 'apple', 'number': 1})
col.insert({'type': 'pineapple', 'number': 2})
col.insert({'type': 'blueberry', 'number': 3})


```

###Update some data
```Python
col.update({'number':10}, cond= where('type')=='pineapple')

```

###Delete some data
```Python
col.remove(eids=[3])
col.remove(cond=where('number')<4)

```

Other usages are very similar to TinyDB.


###Set the parameters
```Python
col.setting(file_size=100, query_cache_size=10, write_freq=5)
```

The above setting means each JSON file is limited to 100 entries and the database will store the latest 10 query results in memory and write-to-disk frequency is 5s.