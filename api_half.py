from data import *

import urllib
from lxml import objectify, etree

def first_enum(iterable, default=(-1,None)):
  for (i,item) in enumerate(iterable):
    return (i,item)
  return default

class Half:
    conditions = [ 'Acceptable', 'Good', 'VeryGood', 'LikeNew', 'BrandNew' ] 
    sellers = list()

    def __init__(self, api_appname='APPNAME GOES HERE'):
        self.api_appname = api_appname

    def finditems_condition(self, edition, condition, maxprice=None):
        MAX_PAGE = 100

        listings = list()
        totalpages = None
        totalresults = None

        for page in range(1, MAX_PAGE):
            url = 'http://svcs.ebay.com/services/half/HalfFindingService/v1?' \
                    'OPERATION-NAME=findHalfItems' \
                    '&X-EBAY-SOA-SERVICE-NAME=HalfFindingService' \
                    '&SERVICE-VERSION=1.0.0' \
                    '&GLOBAL-ID=EBAY-US' \
                    '&X-EBAY-SOA-SECURITY-APPNAME=' + self.api_appname + \
                    '&RESPONSE-DATA-FORMAT=XML' \
                    '&REST-PAYLOAD' \
                    '&productID=' + edition.isbn + \
                    '&productID.@type=ISBN' \
                    '&paginationInput.pageNumber=' + str(page) + \
                    '&itemFilter(0).name=Condition' \
                    '&itemFilter(0).value=' + condition
            
            if maxprice != None:
                maxprice_str = '%.2f' % maxprice
                url = url + \
                    '&itemFilter(1).name=MaxPrice' \
                    '&itemFilter(1).value=' + maxprice_str + \
                    '&itemFilter(1).paramName=Currency' \
                    '&itemFilter(1).paramValue=USD'

            doc = urllib.urlopen(url)
            root = objectify.parse(doc).getroot()

            #print etree.tostring(root, pretty_print=True)

            # todo: check specifics of failure message
            if root.ack == 'Failure':
                # error or no more results
                break

            if totalpages == None:
                totalpages = root.paginationOutput.totalPages
                totalresults = root.paginationOutput.totalEntries
            else:
                assert(totalpages == root.paginationOutput.totalPages)
                assert(totalresults == root.paginationOutput.totalEntries)

# ERROR HERE
            if (page != root.paginationOutput.pageNumber):
                print 'page != root.paginationOutput.pageNumber)'
            #assert(page == root.paginationOutput.pageNumber)
            pageresults = root.paginationOutput.entriesPerPage

            try:
                items = root.product.item
            except AttributeError:
                # no results on this page to be added
                print 'AttributeError'
                break

            count = 0
            for it in items:
                for s in self.sellers:
                    if s.name == it.seller.userID:
                        seller = s
                        break
                else:
                    seller = Seller(it.seller.userID, 
                                        it.seller.feedbackScore.text, 
                                        it.seller.positiveFeedbackPercent.text)
                    self.sellers.append(seller)

                # create listing and append to seller and all listings
                li = HalfListing(edition, seller, 
                                    float(it.price.text), 
                                    it.condition, None)

                (i,prior) = first_enum(p for p in seller.listings if \
                                p.edition.book == li.edition.book)
                if (prior == None):
                    seller.listings.append(li)
                    listings.append(li)
                elif (prior.price > li.price):
                    del seller.listings[i]
                    seller.listings.append(li)
                    listings.append(li)

                count += 1
            assert(pageresults == count)

            if page == totalpages:
                break
        # end p in range(1,MAX_PAGES)

        return listings


    def finditems(self, edition, cond='Good', maxprice=None):
        listings = list()

        assert(cond in self.conditions)
        for c in self.conditions[self.conditions.index(cond):]:
            listings.extend( self.finditems_condition(edition, c, maxprice) )

        return listings

    def shippingcost_marginal(self, binding):
        if ( binding == 'Hardcover' or
            binding == 'Textbook Binding' ):
                return 2.49
        elif ( binding == 'Paperback' or
            binding == 'Mass Market Paperback' or
            binding == 'Bargain Book' ): 
                return 1.89
        else:
                return 999
                #assert(0)

