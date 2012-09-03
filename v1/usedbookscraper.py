import re
import mechanize
from BeautifulSoup import BeautifulSoup

mech = mechanize.Browser()
url = "http://www.half.ebay.com/"

conditions = ["Brand New","Like New","Very Good","Good","Acceptable"]
all_listings = []
sellers = []
editions = []
books = []
class Listing:
#    edition, price, condition, seller, comments
    pass

class Seller:
#   name, ratings, feedback, listings
    pass

class Edition:
#   title, isbn, url, book
    pass

class Book:
    pass

#print "Enter ISBN-13: "
#isbnlist = raw_input().strip().split('\t')
#isbnlist = ["9781888363340"]
#csv = ["$100\t9781888363340" ]

infile = open("books.csv","r")

while (infile):
    line = infile.readline().strip()

    if ( len(line) == 0 ):
        break

    isbnlist = line.split('\t')

    if ( len(isbnlist) == 0 ):
        break

    if (isbnlist[0][0] == "$"):
        max_price = float(isbnlist[0].strip("$")) - 1.89
        del isbnlist[0]
    else:
        max_price = 10000

    b = Book()
    listings = []

    for isbn in isbnlist:
        print
        print isbn

        mech.open(url)
        mech.select_form(name="search")
        mech["query"] = isbn
        mech["m"] = ["books"]
        page = mech.submit()

        print mech.title()
        print page.geturl()

        # Still at a search page. If there are results follow the first link
        if ( mech.title().find("Search Results") != -1 ):
            # todo: handle case where ISBN search returns multiple results
##            try:
##                page = mech.follow_link(url_regex="product.half.ebay.com")
##                print mech.title()
##                print page.geturl()
##            except mechanize.LinkNotFoundError:
##                print "No results"
##                pass
                continue

        e = Edition()
        e.title = mech.title()
        e.url = page.geturl()
        e.isbn = isbn
        e.book = b
        editions.append(e)

        for cond in conditions:
            try:
                page = mech.follow_link(text_regex=cond)
            except mechanize.LinkNotFoundError:
                # todo: handle single page only results
                print "No extended results page for %s" % cond
                pass
                continue
            
            html = page.read()
            soup = BeautifulSoup(html)

            headrow = soup.find(text=re.compile("Price")).parent.parent
            row = headrow.nextSibling.nextSibling
            while( row != None ):
                cells = row.findAll("td",text=True)

                st = Seller()
                st.name = cells[8].strip()
                st.ratings = cells[10].strip()
                st.feedback = cells[13].strip()

                s = None
                for ss in sellers:
                    if ( ss.name == st.name ):
                        #assert ( ss.ratings == st.ratings )
                        #assert ( ss.feedback == st.feedback )
                        s = ss
                        break
                if ( s == None ):
                    s = st
                    s.listings = []
                    sellers.append(s)

                c = Listing()
                c.price = float(cells[2].strip().strip("$").replace(",",""))
                c.condition = cond
                c.comments = cells[17].strip()
                c.seller = s
                c.edition = e

                listings.append(c)
                row = row.nextSibling.nextSibling
            # end listings page loop
        #end of book conditions loop
    # end editions loop
    
    listings = sorted(listings, key=lambda c: c.price)

    for i, c in enumerate(listings):
        if ( c.condition == conditions[0] or c.condition == conditions[1]
             or c.condition == conditions[2] ):
            max_price = min( max_price, c.price + 3.49 - 1.89 )
            print
            print max_price
            break
        
    if ( max_price != None ):
        for i, c in enumerate(listings):
            if c.price > max_price:
                del listings[i:]
                break

    all_listings.extend( listings )
    print "books loop"
#end books loop
print "end books loop"

for c in all_listings:
    print "$%6.2f %-1.1s %-7s %-4s %-20.20s %-.30s" % (c.price, c.condition, c.seller.ratings, c.seller.feedback, c.seller.name, c.edition.title)
    nomatch = True
    for i,l in enumerate(c.seller.listings):
        if ( l.edition.book == c.edition.book ):
            if ( c.price < l.price ):
                del c.seller.listings[i]
            else:
                nomatch = False
            break
    if (nomatch):
        c.seller.listings.append( c )
        
print

sellers = sorted( sellers, key=lambda s: len(s.listings), reverse=True )
sellers = filter( lambda s: (len(s.listings) > 2), sellers )

for s in sellers:
    print "%-20.20s %7s %4s" % (s.name, s.ratings, s.feedback)
    sum = 0
    for l in s.listings:
        print "    $%6.2f %-1.1s %-30.30s" % (l.price, l.condition, l.edition.title)
        sum = sum + l.price
    print "    $%6.2f" % (sum)


