usedbookscraper

Python script to save on shipping for used books at half.com. Pulls reading list from goodreads.com and finds half.com sellers who have many books from the list. Sets the max price for the used book search by pulling the new book price from Amazon.

TODO:
* More robust API calls for Half and Amazon
* Find new source to look up alternate editions from an ISBN which doesn't throttle API requests to 1 per second
* Build a Flask or Django or GAE interface for the script and put it on the web
