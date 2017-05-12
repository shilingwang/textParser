# textParser
textParser is a tool to extract useful information from academic papers.
# Prerequisites
textParser needs the library pyparsing:

http://pyparsing.wikispaces.com/

Please download the package and put it under the main folder.

Of course you can also install pyparsing, then please modify "./scripts/chromatin.py"
# Before parsing
Most of the cases the academic papers are in the format of pdf.

Please use pdfbox:
https://pdfbox.apache.org/download.cgi
to transform the pdf file into txt file and put the file in the folder "./txt"

# How to use
This parser has two parsing modes:

mode 0: histone grammar as X + Y + Z

mode "mapName": parsing protein information

# How to build the map
You need to build your own map to parse the information you want.
The maps are in .dat format. Please put your maps in ./scripts/maps

# To call the function
see the file "call.py"

Input should be the pmid of the article you want to parse.

Remember to put the txt file as well as the xml file of the article in the folder ./txt and ./xml

# Where you can find your output
The outputs are in the folder ./csv.
If you use mode 0 for parsing, the outputs are in ./csv/histone
If you use mode "mapName", the outputs are in ./csv/yourMapName

The output format is .csv

