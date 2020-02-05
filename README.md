# Function List

#### auth(email, password, output)

Logs in with credential given and dumps session cookies to output.cjar and writes refresh token to output.rtoken.

#### load(input)

Loads cookies from input.cjar file.

#### getImg(url)

Returns image fetched from 'secureUrl'.

#### getThumbnail(url)

Returns image fetched from 'url'.

#### search(keyword)

Returns json from the search API.

Mainly used for obtaining seriesid.

#### getSingles(seriesid)

Returns json from singles API.

Mainly used for obtaining singleid.

#### singleToText(singleid)

Returns OCRed  text from single images.

Currently broken because of pytesseract's weird border detection.

#### jPrint(data)
Prints parsed json.
