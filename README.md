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

##Example

###Create a new database and a new collection 

```Python
db = Tinyble('data')  # create a new database named "data"
collection = db.collection('example') # create a new collections under "data" named "example"


```




###To be done before publishing
- illustrate the use of auto-paging and internal timer
- add the tests code
