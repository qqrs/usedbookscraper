from data import *

import urllib
from lxml import objectify, etree

class Goodreads:
    def __init__(self, api_key='KEY GOES HERE'):
        self.api_key = api_key

    def getreadinglist(self, user='USER ID GOES HERE', shelf='to-read'):
        url = 'http://www.goodreads.com/review/list/%s.xml?' \
                'shelf=%s&key=%s&v=2' \
                % (user, shelf, self.api_key)
        doc = urllib.urlopen(url)
        root = objectify.parse(doc).getroot()
        #print etree.tostring(root, pretty_print=True)

        total = int(root.reviews.attrib['end'])

        books = list()
        for r in root.reviews.review:
            b = Book(r.book.isbn.text, r.book.title.text.strip())
            books.append(b)

        # todo: handle pagination and raise exception instead of assert
        assert len(books) == total
        return books

