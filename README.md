# textParser
textParser is a tool to extract useful information from academic papers.
# Prerequisites
textParser needs the library pyparsing:

http://pyparsing.wikispaces.com/

Please download the package and put it under the main folder.

Of course you can also install pyparsing, then please modify "./scripts/chromatin.py"
# How to use
This parser has two parsing modes:

mode 0: histone grammar as X + Y + Z

mode "mapName": parsing protein information

# To call the function
see the file "call.py"

Input should be the pmid of the article you want to parse.

Remember to put the txt file as well as the xml file of the article in the folder ./txt and ./xml

