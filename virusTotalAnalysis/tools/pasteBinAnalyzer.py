
import os
import pandas as pd
import requests

PASTEBIN_PATH = '../data/PasteBin'

def read_hashes_from_file(path):

    fname = os.path.abspath(path)
    df = pd.read_csv(fname)
    return df

if __name__ == "__main__" :
    seen = []
    pastbin = read_hashes_from_file('../data/pastebinURLs.csv')
    print "Read hashes"
    for index, row in pastbin.iterrows(): 
        shash = row[0]
        url = row[1]

        print '[i] checking', shash, url

        if 'raw.php?i=' in url:
            print("Inside raw loop")
            url = url.replace('raw.php?i=', '')

        if url in seen:
            continue

        id = url.split('/')[-1]

        print '[i] fetching', id, 'at', url

        try:
            response = requests.get(url)
        except Exception as e:
            raise

        if response.status_code == 200:
            downloaded_file = response.content
            sample_path = os.path.join(PASTEBIN_PATH, id)
            f = open(sample_path, 'w+')
            f.write(downloaded_file)
            f.close()
        else:
            print 'Error getting ', url, response.status_code

        seen.append(url)
