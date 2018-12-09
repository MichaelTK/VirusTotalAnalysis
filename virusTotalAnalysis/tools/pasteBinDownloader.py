
import os
import pandas as pd
import requests

PATH_TO_URL_FILE = './PasteBinContents/pastebinurls.txt'

def downloadPastebin(url):
    try:
        url = url.rstrip()
        print(url)
        r = requests.get(url)
    except Exception as e:
        print "EXCEPTION!"
        raise

    if r.status_code == 200:
        print "Status code 200"
        url = url[-8:]
        url = "./PasteBinContents/"+url
        content = r.text
        newFile = open(url,'w')
        newFile.write(content)
        newFile.close()
    else:
        print "Status code:"
        print r.status_code



if __name__ == "__main__" :
    urlFile = open(PATH_TO_URL_FILE,'r')

    with open(PATH_TO_URL_FILE) as fp:
        line = fp.readline()
        downloadPastebin(line)
        while line:
            line = fp.readline()
            downloadPastebin(line)
