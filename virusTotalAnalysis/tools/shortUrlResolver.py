import httplib
import urlparse

SHORTENED_URLS_FILE_PATH="/home/kamyk/Documents/VirusTotal/virusTotalAnalysis/tools/shortenedurls.txt"
RESOLVED_URLS_FILENAME="resolvedShortUrlsTest.txt"

def unshorten_url(url):
    try:
        #print url
        parsed = urlparse.urlparse(url)
        h = httplib.HTTPConnection(parsed.netloc)
        h.request('HEAD', parsed.path)
        response = h.getresponse()

        if response.status/100 == 3 and response.getheader('Location'):
            print response.getheader('Location')
            return response.getheader('Location')
        else:
            print "Unable to resolve URL. Probably due to the wrong response code."
            return "Unable_to_resolve"

    except:
        print "An exception occurred."
        return "Exception"

def try_to_resolve(url):
    try:
        print "Current url is: " + url
        parsed = urlparse.urlparse(url)
        h = httplib.HTTPConnection(parsed.netloc)
        h.request('HEAD', parsed.path)
        response = h.getresponse()

        if response.status/100 == 3 and response.getheader('Location'):
            this_response = response.getheader('Location')
            resolution_result = try_to_resolve(this_response)
            if(resolution_result == "Unable_to_resolve" or resolution_result == "Exception"):
                print "Got unable to resolve. Returning current resolved url: " + this_response
                return this_response
            else:
                print "Got a resolved url. Returning the resolved url: " + resolution_result
                return resolution_result

        else:
            #print "Unable to resolve URL. Probably due to the wrong response code."
            return "Unable_to_resolve"

    except:
        #print "An exception occurred."
        return "Exception"

def readUrlsFromFile(path):
    with open(path) as f:
        lines = f.readlines()
    arrayOfUrls = splitLinesIntoUrls(lines)
    return arrayOfUrls

def splitLinesIntoUrls(array3):
    intermediaryArray = []
    lineUrls = []
    for line in array3:
        if line[0] == "\n":
            continue
        line = line.rstrip()
        line.replace('\n', ' ')
        intermediaryArray.append(line)
    for line in intermediaryArray:
        lineUrls.append(line.split())
    return lineUrls

def resolveUrls(array1):
    resolvedUrls=[]
    for urlList in array1:
        for url in urlList:
            print "The url to be unshortened is: " + url
            unshortenedUrl = try_to_resolve(url)

            #print "Unshortened Url about to be appended to resolvedUrls: " + unshortenedUrl
            resolvedUrls.append(unshortenedUrl)
    return resolvedUrls

def getUrlsFromArray(array1):
    urls=[]
    for urlList in array1:
        for url in urlList:
            urls.append(url)
    return urls

def saveResolvedUrls(arrayOfUnresolved, arrayOfResolved):
    file = open(RESOLVED_URLS_FILENAME, "w")
    #print "The first element of arrayOfResolved in saveResolvedUrls is: " + arrayOfResolved[0]
    for resolvedUrl in arrayOfResolved:
        file.write(resolvedUrl+"\n")
    file.close()

def saveResolvedUrlsTest(arrayOfUnresolved, arrayOfResolved):
    file = open(RESOLVED_URLS_FILENAME, "w")
    arrayOfUnresolved=getUrlsFromArray(arrayOfUnresolved)
    print "The first element of arrayOfResolved in saveResolvedUrls is: " + arrayOfResolved[0]
    print "The first element of arrayOfUnresolved in saveResolvedUrls is: " + arrayOfUnresolved[0]
    for i in range(0,len(arrayOfResolved)):
        file.write(arrayOfUnresolved[i])
        file.write(" ----> ")
        file.write(arrayOfResolved[i]+"\n")
    file.close()

if __name__ == "__main__" :
    arrayOfUrls=readUrlsFromFile(SHORTENED_URLS_FILE_PATH)
    resolvedUrls=resolveUrls(arrayOfUrls)
    #print "The first element of resolvedUrls about to be passed into saveResolvedUrls: " + resolvedUrls[0]
    saveResolvedUrlsTest(arrayOfUrls,resolvedUrls)
