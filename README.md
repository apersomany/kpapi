# KPAPI
KakaoPage API for python made by dissecting the KakaoPage REST API

What works
 - Logging in
 - Searching
 - Ferching singles of series
 - Fetching single download data
 - Using tickets
 - Fetching images
 - Fetching thumbnails
 
 TODOs
 - [ ] Purchasing tickets
 - [ ] Logging in with encrypted credentials (currently credentials are sent in plaintext)
 - [ ] Saving single(s) as EPUB 
 - [ ] Account registration

This is my first time ever writing a documentation for a program i've written, so it's probably shit.

 ## Class account
 ### Constuctor
 Same as auth() method
 
    account = kpapi.accounts("username@example.org", "password")

 ### Methods
#### auth(email, password, proxies=None)
Logs in with given credentials. Not meant to be called, but invoked by the constructor.

#### refresh()
Refreshes session with refresh_token,

#### useTicket(seriesid, singleid)
Uses ticket, returns response in json format.

#### getSingle(singleid)
Returns a list of download data. in json format

    getImg(getSingle(singleid)[page]['secureUrl'])
fetches the image of given singleid and page.
This method will probably be renamed to getDownloadData() and be replaced with a method that returns a list of images.

#### getImg(secureUrl)
Returns image at(?) secureUrl.

## Functions
#### randomHashGen()
Returns a random 32 character long alphanumerical string.
Meant to be invoked by the constructor.

#### getImg(secureUrl)
Similar to the method of the account class but only works with free content.

#### getThumbnail(url)
Returns thumbnail at url.

#### search(keyword)
Reutrns seach response in a list of jsons.

#### getSingle(single)
Similar to the getSingle() method of the account class but only works with free content.

#### getSingles(seriesid, order='asc/desc' , pagesize, page)
Returns a list of singles in json format.

#### jsonPrint(json)
Prettyprints the given json.
