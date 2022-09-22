The problem takes the input file as image or folder of images for text extraction of book meta-data.We need to design and develop an application which extracts the metadata from a collection
of book cover pages. The cover pages of an book are scanned images (taken as a single image file) of the first few pages of the book. An example is shown at the end of this document. 
The cover page normally contains the following information (in addition to other stuff):Title of the book,Names of the authors,Publishers,ISBN numbers

The scanned images will be in the JPEG or PNG format as of now. The application will be a command-line tool which will support the following arguments:A flag that tells whether to process
a single input file or a directory containing many files.Path of the input file or the directory.

Steps to run:
change the tesseract_cmd in file to your downloaded loaction
the cmd should be like : python 2019CSB1114.py --az main_Dataset.csv --file C:\Users\USER\dontknow --flag

Required package are argparse, cv2,pytesseract,spacy.

