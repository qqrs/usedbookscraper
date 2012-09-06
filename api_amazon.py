from data import *

import urllib2
from lxml import objectify, etree
import bottlenose

# Returns first item in list
def first(iterable, default=None):
  for item in iterable:
    return item
  return default

def binding_isbook(format):
    if ( format == 'Hardcover' or
        format == 'Paperback' or
        format == 'Mass Market Paperback' or
        format == 'Bargain Book' or 
        format == 'Textbook Binding' ):
            return True
    else:
            return False

class Amazon:
    MAX_HTTP_RETRIES = 7

    def __init__(self, api_awskey="AWSKEY GOES HERE",
                    api_secretkey="SECRET KEY GOES HERE",
                    api_assockey="ASSOC KEY GOES HERE"):
        self.bn_amazon = bottlenose.Amazon(api_awskey, api_secretkey, 
                                                                api_assockey)

    def get_bookversion_list(self, book):
        for attempts in range(1,self.MAX_HTTP_RETRIES):
            try:
                response = self.bn_amazon.ItemLookup(
                    SearchIndex = "Books", 
                    MerchantId = "Amazon",
                    Condition = "New",
                    IdType = "ISBN", 
                    ItemId = book.isbn,
                    ResponseGroup = "ItemAttributes,AlternateVersions")
                break
            except urllib2.HTTPError, error:
                print "HTTPError %d: retry %d" % (error.code, attempts)
        else:
            print "Max network tries reached"
            return None

        root = objectify.fromstring(response)
        #print etree.tostring( root, pretty_print = True )

        item = first(i for i in root.Items.Item if \
                binding_isbook(i.ItemAttributes.Binding) == True  )

        #editions = list()
        #e = Edition(book, item.ASIN.text, item.ItemAttributes.Title.text)
        #editions.append(e)
        asins = list()
        asins.append(item.ASIN.text)

        try:
            for v in item.AlternateVersions.AlternateVersion:
                if binding_isbook(v.Binding) == False:
                    continue
                #editions.append( Edition(book, v.ASIN.text, v.Title.text) )
                asins.append( v.ASIN.text )
        except AttributeError:
            # no alternate versions
            pass

        return asins


    def get_bookversion_info(self, book, asin):
        for attempts in range(1, self.MAX_HTTP_RETRIES):
            try:
                response = self.bn_amazon.ItemLookup(
                    MerchantId = "Amazon",
                    Condition = "New",
                    IdType = "ASIN", 
                    ItemId = asin,
                    ResponseGroup = "ItemAttributes,OfferListings")
                break
            except urllib2.HTTPError, error:
                print "HTTPError %d: retry %d" % (error.code, attempts)
        else:
            print "Max network tries reached"
            return None

        root = objectify.fromstring(response)
        #print etree.tostring( root, pretty_print = True )

        item = root.Items.Item
        total = item.Offers.TotalOffers
        assert total < 2

        #li = AmazonListing(edition)
        v = AmazonBookVersion( book, asin,
                                item.ItemAttributes.Title.text.strip(),
                                item.ItemAttributes.Binding.text )

        try:
            v.isbn = item.ItemAttributes.ISBN.text
        except AttributeError:
            v.isbn = None

        if total == 0:
            v.newprice == None
        else:
            v.newprice = item.Offers.Offer.OfferListing.Price.Amount/100.0

        return v 


    def get_bookeditions(self, book):
        asins = self.get_bookversion_list(book)
        assert len(asins) > 0

        #first_version = None
        best = None
        #version_isbns = list()
        editions = list()
        for asin in asins:
            try:
                r = self.get_bookversion_info(book, asin)
            except AttributeError:
                print "  Incomplete listing: %s" % (asin)

            if r == None:
                continue

            #if first_version == None:
                #first_version = r

            if r.isbn != None:
                for e in editions:
                    if r.isbn == e.isbn:
                        break
                else:
                    e = Edition(r)
                    editions.append(e)

                #if r.isbn not in version_isbns:
                    #version_isbns.append(r.isbn)

            if r.newprice == None:
                continue
            #if r.available_amazon == False:
                #continue

            if best == None:
                best = r
            elif best.newprice > r.newprice:
                best = r

        if best == None:
            book.newprice = None
        else:
            book.newprice = best.newprice
            book.newversion = best

        return editions

        # done here; rest is just print
        #if best == None:
            #assert( first_version != None )
            #best = first_version
            #price = '  ---  '
        #else:
            #price = '$%3.2f' % (best.newprice)
            #
        #if best.isbn == None:
            #isbn_str = '???'
        #else:
            #isbn_str = best.isbn
#
        #print '%7s %10s %13s %10.10s %.35s' % (price, best.asin, best.isbn, 
                                                    #best.binding, best.title)
        #print '  ',
        #for e in editions:
            #print e.isbn + ' ', 
        #print ''
#

