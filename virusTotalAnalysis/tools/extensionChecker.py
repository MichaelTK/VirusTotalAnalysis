import requests
import magic

RESOLVED_URLS_FILENAME = "resolvedShortUrlsTest.txt"
FILETYPES_FILENAME = "extensionsVsFiletypes.csv"

def checkExtensions(arrayOfUrls):
    i = 0
    for url in arrayOfUrls:
        r = requests.get(url, allow_redirects=True)
        open('tempFile', 'wb').write(r.content)
        fileType=magic.from_file(tempFile)
        urlTypeArray[i][0] = url
        urlTypeArray[i][1] = fileType
        i = i + 1
    return urlTypeArray

def saveExtensionsVsFiletypes(arrayOfExtensionsVsFiletypes):
    file = open(RESOLVED_URLS_FILENAME, "w")
    file.write(url+","+fileType+"\n")
    file.close()

#FIX THIS
def readUrlsFromFile(path):
    with open(path) as f:
        lines = f.readlines()
    arrayOfLines = splitLinesIntoUrls(lines)
    for entity in arrayOfLines:
        arrayOfUrls.append(entity[2])
    return arrayOfUrls

if __name__ == "__main__" :
    urlsToCheck = readUrlsFromFile(RESOLVED_URLS_FILENAME)
    extensionsVsFiletypes = checkExtensions(urlsToCheck)
    saveExtensionsVsFiletypes(extensionsVsFiletypes)
