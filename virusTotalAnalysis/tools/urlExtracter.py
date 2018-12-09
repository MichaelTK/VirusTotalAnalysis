# -*- coding: utf-8 -*-
import pickle
import pprint
import os
import json

REPORT_PATH = '/home/kamyk/Documents/VirusTotalReports/data/reports'

def readUrlsFromFile(filename):
    report = pickle.load(open(filename))
    json_str = json.dumps(report['ITW_urls'])
    resp = json.loads(json_str)

    for x in resp:
        file = open("itw_urls.txt", "a")
        print(x)
        file.write(x+"\n")
        file.close()




if __name__ == "__main__" :
    for filename in os.listdir(REPORT_PATH):
        if filename.endswith(".report"):
            # print(os.path.join(directory, filename))
            readUrlsFromFile(REPORT_PATH+'/'+filename)
        else:
            continue
