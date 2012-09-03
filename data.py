
class Book:
    def __init__(self, isbn, title):
        self.isbn = isbn        # isbn of one edition from goodreads user 
        self.title = title
        self.newprice = None    # new price sold by Amazon
        self.newversion = None
        self.editions = None

class Edition:
    def __init__(self, version):
        self.book = version.book
        self.title = version.title
        self.isbn = version.isbn
        self.amazon_book_version = version
    #def __init__(self, book, asin, title):
        #self.book = book
        #self.title = title
        #self.isbn = None 
        #self.binding = None

class AmazonBookVersion:
    def __init__(self, book, asin, title, binding):
        self.book = book
        self.asin = asin
        self.title = title
        self.binding = binding
        self.newprice = None
        self.isbn = None

class HalfListing:
    def __init__(self, edition, seller, price, condition, comments):
        self.edition = edition
        self.seller = seller
        self.price = price
        self.condition = condition
        self.comments = comments


class Seller:
    def __init__(self, name, ratings, feedback):
        self.name = name
        self.ratings = ratings
        self.feedback = feedback
        self.listings = list() 

