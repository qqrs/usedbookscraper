from data import *

from apikeys import goodreads_key, goodreads_userid
from apikeys import half_appname
from apikeys import amazon_awskey, amazon_secretkey, amazon_assockey

from api_goodreads import *
from api_half import *
from api_amazon import *

gr = Goodreads(goodreads_key)
books = gr.getreadinglist(user=goodreads_userid)
#books = gr.getreadinglist('5624110')
#for b in books:
    #print '%13s %s' % (b.isbn, b.title)

#
half = Half(half_appname)
#b = Book('0425238091','title')
#ed = Edition(b, 'title', '0425238091')
#ed.isbn = '0425238091'
#listings = half.finditems(ed,'Good','6.00')
#listings.sort(key=lambda li: li.price)
#for li in listings:
    #print '$%7.2f %20s %20s' % (li.price, li.seller.name, li.condition)


#
amazon = Amazon(amazon_awskey, amazon_secretkey, amazon_assockey)
#isbn = '9781416572503'
#isbn = '0425238091'
#b = Book(isbn,'title')
#eds = amazon.get_bookversions(b)
#for e in eds:
    #print "%12s  %s" % (e.asin, e.title)
#for e in eds:
    #li = amazon.get_bookversion_info(e)
    #if li.price == None:
        #price = '  ---  '
    #else:
        #price = '%7.2f' % (li.price)
    #print '%7s %13s %s' % (price, li.edition.isbn, li.title)
#

#books = books[:3]

for b in books:
    editions = amazon.get_bookeditions(b)
    b.editions = editions
    if b.newprice != None:
        print '%7s %10s %13s %10.10s %.35s' % (b.newprice, b.newversion.asin, 
                                                b.newversion.isbn, 
                                                b.newversion.binding, 
                                                b.title)
    else:   
        print '%7s %10s %13s %10.10s %.35s' % ('  ---  ','','','',b.title) 

sellers = half.sellers
for b in books:
    #print '%7.2f %s' % (half.shippingcost_marginal(b.newversion.binding), b.title)
    for e in b.editions:
        if b.newprice == None:
            maxprice = None
        else:
            assert(e.amazon_book_version != None)
            ship = half.shippingcost_marginal(e.amazon_book_version.binding)
            maxprice = b.newprice - ship 

        print '*' + e.isbn
        # call half api to get listings
        listings = half.finditems(e, maxprice=maxprice)
    print ''
    #for e in b.editions:
        #print '  ' + e.isbn
# b.editions.sort

sellers = sorted( sellers, key=lambda s: len(s.listings), reverse=True )
sellers = filter( lambda s: (len(s.listings) > 2), sellers )

#for s in sellers:
	#print s.name
	#for L in s.listings:
		#print '$%5.2f %s' % (L.price, L.edition.title)


for i,s in enumerate(sellers):
    print "%3d %-20.20s %7s %4s" % (i, s.name, s.ratings, s.feedback)
    sum = 0
    for L in s.listings:
        print "    $%6.2f %-1.1s %-30.30s" % \
            (L.price, L.condition, L.edition.title)
        sum = sum + L.price
    print "    $%6.2f" % (sum)


