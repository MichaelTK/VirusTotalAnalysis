#import virustotal
import sys, os, time, json, pickle, csv
import requests
import hashlib
import pprint
import pandas as pd
from datetime import datetime, timedelta

#from virus_total_apis import IntelApi, PublicApi, PrivateApi

from settings import API_KEY




LIST_HASHES = [
  '/home/kamyk/Downloads/INPUT_HASHES11.txt'
]

#OUTPUT_FOLDER = os.path.join('../../data/VirusTotal/reports', os.path.basename(os.path.splitext(LIST_HASHES)[0]))
OUTPUT_FOLDER = 'data11'

DELAY_RATE=1
REQUEST_PER_MINUTE = 1000 * DELAY_RATE
REQUEST_PER_DAY = 20000 * DELAY_RATE
#REQUEST_PER_DAY = 21000


executable_types = ' and (type:peexe or type:pedll or type:neexe or type:nedll or type:mz or type:msi or type:com or type:coff or type:elf or type:rpm or type:linux or type:macho or type:symbian or type:palmos or type:wince or type:android or type:iphone)'



all_quarters_ordered = ['2009Q1', '2009Q2', '2009Q3', '2009Q4',
                        '2010Q1', '2010Q2', '2010Q3', '2010Q4',
                        '2011Q1', '2011Q2', '2011Q3', '2011Q4',
                        '2012Q1', '2012Q2', '2012Q3', '2012Q4',
                        '2013Q1', '2013Q2', '2013Q3', '2013Q4',
                        '2014Q1', '2014Q2', '2014Q3', '2014Q4',
                        '2015Q1', '2015Q2', '2015Q3', '2015Q4',
                        '2016Q1', '2016Q2', '2016Q3', '2016Q4',
                        '2017Q1', '2017Q2', '2017Q3', '2017Q4',
                        '2018Q1', '2018Q2'] #'2018Q3', '2018Q4'


def build_quarter_string(year, month):

    numeric_quarter = int(math.ceil(month/3.0))
    return str(year) + 'Q' + str (numeric_quarter)

def get_vt_quarter_year(date):

    quarter_year = None
    date_object = datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
    quarter_year = build_quarter_string(date_object.year, date_object.month)
    return quarter_year

def qet_vt_date_range(quarter):

    split = quarter.split('Q')
    year = split[0]
    quarter_of_a_month = int(split[1])

    lower_month = (quarter_of_a_month - 1) * 3 + 1
    upper_month = lower_month + 3 - 1

    if lower_month < 10:
        lower_month = '0' + str(lower_month)

    if upper_month < 10:
        upper_month = '0' + str(upper_month)

    last_date_month = '31'
    if quarter_of_a_month == 2 or quarter_of_a_month == 3:
        last_date_month = '30'

    return year, year + '-' + str(lower_month) + '-01' + '00:00:00', year + '-' + str(upper_month) + '-' + str(last_date_month) + '23:59:59'


def hash256(tfile):

    f = open(tfile, 'rb')
    fr = f.read()
    hasher_256 = hashlib.sha256()
    hasher_256.update(fr)
    sha256 = hasher_256.hexdigest()
    return sha256

def read_hashes_from_folder(fname):

    hash_samples = []
    map_hash_name = open(os.path.basename(fname) + '_map_hash_name.txt', 'wb')

    for root, subdirs, files in os.walk(fname):
        for filename in files:
            file_path = os.path.join(root, filename)

            file_hash = hash256(file_path)

            if 'apk' in file_path:
                map_hash_name.write(file_path + '\t' + file_hash + '\n')
                hash_samples.append(file_hash)

    map_hash_name.close()
    return hash_samples

def read_hashes_from_yara_file(fname):

    content = []
    with open(fname) as f:
        for line in f.readlines():
            filepath = line.split()[1]
            filename = os.path.basename(filepath)
            if '_' in filename:
                hashnum = filename.split('_')[1].strip()
            else:
                hashnum = filename.strip()
            content.append(hashnum)
    return content

def read_hashes_from_reportedAV_file(fname):

    content = []
    with open(fname, 'rb') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')

        for row in reader:
            hashnum = os.path.basename(row[0])[:-len('.json')]
            content.append(hashnum)
    return content

def read_hashes_from_PaloAltoNetworks_file(fname):

    df_palo = pd.read_csv(fname)
    return list(df_palo['SHA256'])


def read_hashes_from_file(fname):

    content = []
    fname = os.path.abspath(fname)

    if 'VirusShare' in fname or (not 'reportedAV' in fname and '_VT_' in fname):
        return read_hashes_from_yara_file(fname)
    elif 'reportedAV' in fname:
        return read_hashes_from_reportedAV_file(fname)
    elif 'VirusTotal/search' in fname and fname.endswith('json'):
        with open(fname, 'r') as handle:
            return json.load(handle)
    elif 'PaloAlto' in fname and fname.endswith('.csv'):
        return read_hashes_from_PaloAltoNetworks_file(fname)
    else:
        with open(fname) as f:
            for line in f.readlines():
                content.append(str(line).strip())
        return content

def retrieve_complete(hash_sample, binary=False, report=False, behaviour=False, network=False, output_folder='outputs', previous_samples=[]):

    c_req_b = 0
    retry_b = False
    if binary:
        c_req_b, retry_b = retrieve_binary(hash_sample, output_folder=output_folder, previous_samples=previous_samples)

    c_req_r, retry_r = retrieve_intelligence(hash_sample, report=report,behaviour=behaviour,network=network,output_folder=output_folder,previous_samples=previous_samples)

    return c_req_b+c_req_r, retry_b|retry_r


def retrieve_binary(hash_sample, output_folder = 'outputs', previous_samples = []):

    req = 0
    retry = False
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    output_folder_bin = os.path.join(output_folder, 'bin')
    if not os.path.exists(output_folder_bin):
        os.makedirs(output_folder_bin)

    sample_path = os.path.join(output_folder_bin, hash_sample)

    if os.path.exists(sample_path) or hash_sample in previous_samples and os.stat(sample_path).st_size > 0:
        print '[%s] Skipping...'% hash_sample
        return req, retry
    print '[%s] Retrieving binary...'% hash_sample
    params = {'apikey': API_KEY, 'hash': hash_sample}
    try:
        response = requests.get('https://www.virustotal.com/vtapi/v2/file/download', params=params)
    except requests.exceptions.ReadTimeout:
        retry = True
        return 1, retry
    except Exception as e:
        raise

    print '--------', response
    if response.status_code == 200:
        downloaded_file = response.content
        f = open(sample_path, 'w+')
        f.write(downloaded_file)
        f.close()
        req += 1
    elif response.status_code == 204:
        retry = True

    return req, retry


def retrieve_intelligence_many(hash_samples, report=False, behaviour=False, network=False, binary=False, output_folder='outputs', previous_samples = []):

    t_day = time.time()
    t_min = time.time()
    req_min = 0
    req_day = 0

    for hash_sample in hash_samples:
        while True:
            try:
                c_req, retry = retrieve_complete(hash_sample.strip(), binary=binary, report=report, behaviour=behaviour, network=network, output_folder=output_folder, previous_samples=previous_samples)
                #if c_req > 0:
                #    time.sleep(60.0/REQUEST_PER_MINUTE)
            except requests.exceptions.ConnectionError:
                c_req = 0
                retry = True
            except ValueError, e:
                print '[w] ValueError', hash_sample
                print str(e)
                import traceback
                traceback.print_exc()
                sys.exit()

            req_min += c_req
            req_day += c_req

            duration = time.time() - t_min
            day = time.time() - t_day

            if req_day >= REQUEST_PER_DAY:
                print '------ CONSUMED DAILY QUOTA ------'
                #time.sleep(int(24*60*60 - day) + 60)
                time.sleep(1*60*60) # sleep one hour and then retry
                t_day = time.time()
                req_day = 0
            elif day > 24*60*60:
                t_day = time.time()
                req_day = 0

            if (req_min >= REQUEST_PER_MINUTE and duration < 60.0) or retry:
                time.sleep(int(60) + 1)
                t_min = time.time()
                req_min = 0
            elif duration > 60.0:
                t_min = time.time()
                req_min = 0

            if not retry:
                break
            else:
                print '[%s] Retrying...'% hash_sample


def retrieve_intelligence(hash_sample, report=False, behaviour=False, network=False, output_folder = 'outputs', previous_samples = []):
    retry = False
    req = 0
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    if hash_sample in previous_samples:
        print '[%s] Skipping...'% hash_sample
        return req, retry

    #print '[%s] Retrieving data...'% hash_sample

    if report:

        output_folder_reports = os.path.join(output_folder, 'reports')
        if not os.path.exists(output_folder_reports):
            os.makedirs(output_folder_reports)

        report_filename = os.path.join(output_folder_reports, hash_sample + '.report')
        to_download = False
        if not os.path.exists(report_filename) or os.stat(report_filename).st_size == 0:
            to_download = True
        else:
            json_report = pickle.load(open(report_filename, "rb" ))
            if not 'sha256' in json_report:
                to_download = True

        if to_download:
            params = {'apikey': API_KEY, 'resource': hash_sample, 'allinfo': 'true'}
            response = requests.get('https://www.virustotal.com/vtapi/v2/file/report', params=params)
            #print '--------', response
            if response.status_code == 200:
                report = response.json()
                #print '--------', report

                f = open(report_filename, 'w+')
                pickle.dump(report, f)
                f.close()
                req += 1
            elif response.status_code == 204:
                retry = True

    if behaviour:

        output_folder_behavior = os.path.join(output_folder, 'behaviours')
        if not os.path.exists(output_folder_behavior):
            os.makedirs(output_folder_behavior)

        report_filename = os.path.join(output_folder_behavior, hash_sample + '.behaviour')

        if not os.path.exists(report_filename) or os.stat(report_filename).st_size == 0:
            params = {'apikey': API_KEY, 'hash': hash_sample}
            response = requests.get('https://www.virustotal.com/vtapi/v2/file/behaviour', params=params)
            if response.status_code == 200:
                report = response.json()
                f = open(report_filename, 'w+')
                pickle.dump(report, f)
                f.close()
                req += 1
            elif response.status_code == 204:
                retry = True

    if network:

        output_folder_net = os.path.join(output_folder, 'network')
        if not os.path.exists(output_folder_net):
            os.makedirs(output_folder_net)

        report_filename = os.path.join(output_folder_net, hash_sample + '.pcap')
        if not os.path.exists(report_filename) or os.stat(report_filename).st_size == 0:
            response = get_net_traffic(hash_sample,report_filename)
            if response and response.status_code == 200:
                req += 1
            elif response and response.status_code == 204:
                retry = True

    return req, retry

# Adapted from https://www.virustotal.com/en/documentation/private-api/#get-network-traffic
def get_net_traffic(hash_sample,filename):
    #print "[%s] Retrieving network traffic"%hash_sample
    response = None
    req = 0
    params = {'apikey': API_KEY,'hash': hash_sample}

    headers = {
      "Accept-Encoding": "gzip, deflate",
      "User-Agent" : "gzip,  My Python requests library example client or username"
    }

    first_bytes = None
    with open(filename, 'wb') as handle:
        response = requests.get('https://www.virustotal.com/vtapi/v2/file/network-traffic', params=params, headers=headers, stream=True)

        if response.status_code == 204:
            return response

        if not response.ok:

            try:
                report = response.json()
                print "[%s] Something went wrong: %s" % (hash_sample,report['verbose_msg'])

            except ValueError, e:
                print "[%s] Something went wrong: %s" % (hash_sample,str(response))

            return response
        for block in response.iter_content(4096):
            handle.write(block)
            if not first_bytes:
                first_bytes = str(block)[:4]

        handle.close()

        valid_pcap_magics = [ '\xd4\xc3\xb2\xa1', '\xa1\xb2\xc3\xd4', '\x4d\x3c\xb2\xa1', '\xa1\xb2\x3c\x4d' ]
        if first_bytes in valid_pcap_magics:
            print "[%s] PCAP downloaded"%hash_sample
            return response
        elif first_bytes.startswith('{"'):
            print "[%s] NOT found" %hash_sample
            return response
        else:
            print "[%s] Unknown file"%hash_sample
            return response

    return response


def make_search(query, positives, dates, output_folder, filebasename = None):

    output_folder_searches = os.path.join(output_folder, 'searches')
    if not os.path.exists(output_folder_searches):
        os.makedirs(output_folder_searches)

    params = {'apikey': API_KEY, 'query': query + ' and p:' + str(positives) + ' and ' + dates}

    print '[i] Searching for:', params['query']

    if filebasename:
        filename = os.path.join(output_folder_searches, filebasename + '.json')
    else:
        filename = os.path.join(output_folder_searches, params['query'] + '.json')
    if executable_types in filename:
        filename = filename.replace(executable_types, 'and executables')
    if not os.path.exists(filename):

        params['offset'] = None

        samples = []
        stop = False
        response_json = []
        while not stop:
            try:
                results = None
                while results is None:
                    response = requests.get('https://www.virustotal.com/vtapi/v2/file/search', params=params)

                    #print '--------', response
                    if response.status_code == 200:
                        response_json = response.json()

                        pprint.pprint(response_json)

                        if 'hashes' in response_json:
                            results = response_json[u'hashes']
                            samples.extend(results)
                        elif 'verbose_msg' in response_json and response_json['verbose_msg'] == 'No samples matching the search criteria':
                            stop = True
                            break

                        if 'offset' not in response_json or response_json['offset'] is None:
                            stop = True
                        else:
                            params['offset'] = response_json[u'offset']

                    else:
                        print("\tError downloading hashes, retrying... " + str(response.status_code))
                        time.sleep(60)
                        results = None


            except KeyboardInterrupt:
                print("Caught CTRL-C!")
                break


        f = open(filename, 'w')
        json.dump(samples, f)
        f.close()

    else:
        with open(filename, 'r') as handle:
            response_json = json.load(handle)

    if 'hashes' in response_json:
        return response_json[u'hashes']
    elif type(response_json) == list:
        return response_json
    else:
        return []


def make_search_vt_api(query, positives, year, output_folder):

    output_folder_searches = os.path.join(output_folder, 'searches')
    if not os.path.exists(output_folder_searches):
        os.makedirs(output_folder_searches)

    params = {'apikey': API_KEY, 'query': query + ' p:' + str(positives) + ' fs:' + str(year) + '-01-0100:00:00+'}
    print '[i] Searching for:', params['query']

    samples = []
    filename = os.path.join(output_folder_searches, params['query'] + '.json')
    if not os.path.exists(filename):

        intel_api = IntelApi(params['apikey'])
        nextpage = None

        while True:

            try:
                results = None
                while results is None:
                    #nextpage, results = intel_api.get_hashes_from_search('behavior: pool.minexmr.com', nextpage)
                    nextpage, results = intel_api.get_hashes_from_search(params['query'], nextpage)
                    if results.status_code != 200:
                        print("\tError downloading hashes, retrying...")
                        time.sleep(60)
                        results = None
                    else:
                        results = results.json()
                        samples.extend(response_json[u'hashes'])

                if nextpage is None:
                    break

            except KeyboardInterrupt:
                print("Caught CTRL-C!")
                break

    else:
        with open(filename, 'r') as handle:
            samples = json.load(handle)

    return samples


def retrieve_samples(out_folder, dates, positives):

    OUTPUT_FOLDER_YEAR = os.path.join(out_folder, year)

    try:
        previous_samples = os.listdir(OUTPUT_FOLDER_YEAR)
    except OSError:
        previous_samples = []

    print 'Searching...', year

    hashes = make_search(query='behavior: pool.minexmr.com', positives=positives, dates=dates)

    #TODO offsets: On each request you will get at most 300 files matching the query. You can get the next 300 files by passing the offset
    # received in the previous query as an argument to the next query. In those cases the query argument most be identical to the one passed to the previous request.

    req_min = 0
    req_day = 0
    t_day = time.time()
    t_min = time.time()
    for hash_sample in hashes:

        while True:
            c_req, retry = retrieve_complete(hash_sample, binary=False, report=True, behaviour=False, network=False, output_folder=OUTPUT_FOLDER_YEAR, previous_samples=previous_samples)

            req_min += c_req
            req_day += c_req

            duration = time.time() - t_min
            day = time.time() - t_day

            if req_day >= REQUEST_PER_DAY:
                print '------ CONSUMED DAILY QUOTA ------'
                time.sleep(int(24*60*60 - day) + 60)
                t_day = time.time()
                req_day = 0
            elif day > 24*60*60:
                t_day = time.time()
                req_day = 0

            if (req_min >= REQUEST_PER_MINUTE and duration < 60.0) or retry:
                time.sleep(int(60) + 1)
                t_min = time.time()
                req_min = 0
            elif duration > 60.0:
                t_min = time.time()
                req_min = 0

            if not retry:
                break
            else:
                print '[%s] Retrying...'% hash_sample


def load_reports(report_folder):

    for report in os.listdir(report_folder):
        if report.endswith('report'):
            json_report = pickle.load( open( os.path.join(report_folder, report), "rb" ))
            #print pprint.pprint(json_report)
            if 'sha256' in json_report:
                print json_report['sha256'],'\t', json_report['positives'], json_report['malicious_votes'], '\t', json_report['first_seen']
            else:
                print report, 'was not available'


def load_reports_from_file(hash_samples, output_folder):

    for sample in hash_samples:
        filepath = os.path.join(output_folder, 'reports', sample + '.report')
        json_report = pickle.load( open( filepath, "rb" ))
        print pprint.pprint(json_report)
        if 'sha256' in json_report:
            print json_report['sha256'],'\t', json_report['positives'], json_report['malicious_votes'], '\t', json_report['first_seen']
        else:
            print report, 'was not available'


def search_miners_in_reports(report_folder):
    for root,subdirs,files in os.walk(report_folder):
        for report in files:
            if report.endswith('json'):
                json_report = json.load( open( os.path.join(root, report), "rb" ))
                if 'sha256' in json_report:
                    scans=json_report['scans']
                    toPrint=root+'/'+report
                    for av in scans.keys():
                        if scans[av]['detected'] and 'miner' in scans[av]['result'].lower():
                            toPrint+=',"%s__%s"'%(av,scans[av]['result'])
                    if ',' in toPrint:
                        print toPrint
        for subdir in subdirs:
            search_miners_in_reports(subdir)

            sys.exit()


def search():

    for quarter in all_quarters_ordered:
        search_quarter(quarter)


def search_quarter(quarter, positives='5+'):


    #TODO: Once we are given access, test different operators for 'query'
    # (see https://www.virustotal.com/intelligence/help/file-search/#search-modifiers)
    # Snort:
    # ../data/snort_rules_miner.rules
    # Specifically interesting is the rule with snort-id 46237
    # https://github.com/Hestat/minerchk/blob/master/monero-snort.rules

    print '----------------', quarter
    output_folder = OUTPUT_FOLDER

    year, lower_month, upper_month = qet_vt_date_range(quarter)
    dates = 'fs:' + lower_month + '+' + ' and ' + 'fs:' + upper_month + '-'

    # ------- RETRIEVE HASHES FROM BEHAVIOR @ pool.minexmr.com
    #samples = make_search('behavior: pool.minexmr.com' + executable_types, positives, dates, output_folder, filebasename = 'behavior: pool.minexmr.com ' + quarter)
    #print len(samples)

    # ------- RETRIEVE HASHES FROM BEHAVIOR @ HOSTLISTS
    hostslist = read_hashes_from_file('behavior-hostslist.txt')
    rule = ''
    for idx, host in enumerate(hostslist):
        rule += 'behavior: ' + host
        if idx != len(hostslist) - 1:
            rule += ' or '
    samples = make_search( '(' + rule + ')' + executable_types, positives, dates, output_folder, filebasename = 'behavior: behavior-hostslist and executables ' + quarter + ' ' + positives)
    print len(samples)

    # ------- RETRIEVE HASHES FROM SNORT 46237 45417
    samples = make_search('snort: 45417 or snort: 46237 or snort: 46238', positives, dates, output_folder, filebasename = 'snort: 45417 or snort: 46237 or snort: 46238 ' + quarter + ' ' + positives)
    print len(samples)
    #return

    # ------- RETRIEVE HASHES FROM SNORT miner
    samples = make_search('snort: miner', positives, dates, output_folder, filebasename = 'snort: miner ' + quarter + ' ' + positives)
    print len(samples)
    #return

    # ------- RETRIEVE HASHES FROM TRAFFIC TO HOSTLISTS
    hostslist = read_hashes_from_file('behavior-hostslist.txt')
    ipslist = read_hashes_from_file('behavior-ip-only.txt')
    rule = ''
    for idx, host in enumerate(hostslist):
        rule += 'traffic: ' + host
        if idx != len(hostslist) - 1:
            rule += ' or '
    samples = make_search( '(' + rule + ')' + executable_types, positives, quarter, output_folder, filebasename = 'traffic: behavior-hostslist and executables ' + quarter + ' ' + positives)
    print len(samples)

    for ip in ipslist:
        rule = 'traffic: ' + ip
        samples = make_search( '(' + rule + ')' + executable_types, positives, quarter, output_folder, filebasename = 'traffic: ' + str(ip) + ' and executables ' + quarter + ' ' + positives)
        print len(samples)

    # ------- RETRIEVE BEHAVIORS FROM ... stratum+tcp
    samples = make_search('(behavior: stratum+tcp)' + executable_types, positives, dates, output_folder, filebasename = 'behavior: stratum+tcp ' + quarter + ' ' + positives)
    print len(samples)


    # ------- RETRIEVE HASHES FROM ENGINES
    samples = make_search('(engines:miner or engines:coinminer or engines:bitcoin or engines:btcMine)' + executable_types, positives, dates, output_folder, filebasename = 'engines and executables ' + quarter + ' ' + positives)
    print len(samples)
    #return


def count_samples():

    samples = set()

    path_searches_dir = '../../data/VirusTotal/searches'
    for filename in os.listdir(path_searches_dir):
        if not 'executables' in filename:
            continue # Skip JS for the time being
        if filename.endswith('json'):
            pathfile = os.path.join(path_searches_dir, filename)
            LIST_HASHES.append(pathfile)

    # ------- RETRIEVE RESOURCE FROM LIST... in inverse order
    for resource in reversed(LIST_HASHES):
        print '[i] Querying %d from %s' % (len(read_hashes_from_file(resource)), resource)
        hash_samples = read_hashes_from_file(resource)
        samples.update(hash_samples)

    print 'unique samples', len(samples)

def get_reports_parents(report_folder, whitelist=None):
    for report in os.listdir(report_folder):
        if report.endswith('report'):
            json_report = pickle.load( open( os.path.join(report_folder, report), "rb" ))
            #print pprint.pprint(json_report)
            if 'sha256' in json_report:
                if whitelist:
                    if not json_report['sha256'] in whitelist:
                        continue
                if 'additional_info' in json_report and 'compressed_parents' in json_report['additional_info']:
                    hash_samples = json_report['additional_info']['compressed_parents']
                    retrieve_intelligence_many(hash_samples, report=True, behaviour=False, network=False, binary=False, output_folder=OUTPUT_FOLDER)

#TODO: download execution_parents


def get_reports_parents_by_hash(report_folder, samples):
    for sample in samples:
        report = sample + '.report'
        json_report = pickle.load( open( os.path.join(report_folder, report), "rb" ))
        #print pprint.pprint(json_report)
        if 'sha256' in json_report:
            if 'additional_info' in json_report and 'compressed_parents' in json_report['additional_info']:
                hash_samples = json_report['additional_info']['compressed_parents']
                retrieve_intelligence_many(hash_samples, report=True, behaviour=False, network=False, binary=False, output_folder=OUTPUT_FOLDER)

#TODO: download execution_parents

def test():

    hash_sample = '3e9fd38a440138ec35b4eb6d4ed9643ad86e76a6f559656186f14dafd35e9d4b'
    params = {'apikey': API_KEY, 'resource': hash_sample, 'allinfo': 'true'}
    response = requests.get('https://www.virustotal.com/vtapi/v2/file/report', params=params)
    print '--------', response
    if response.status_code == 200:
        report = response.json()
        import pprint
        pprint.pprint(report)

    sys.exit()


def debug():

    # ------- RETRIEVE SAMPLES THAT WE MISS
    hash_samples = read_hashes_from_file('../../data/overlap-paloAlto-wemiss.txt')
    retrieve_intelligence_many(hash_samples, report=True, behaviour=False, network=True, binary=True, output_folder=OUTPUT_FOLDER)

    sys.exit()


if __name__ == "__main__" :

    #vTotal = virustotal.VirusTotal(API_KEY)
    #vTotal.get(hash)

    if not os.path.exists(OUTPUT_FOLDER):
        os.makedirs(OUTPUT_FOLDER)

    # ------- RETRIEVE REPORT
    #retrieve_intelligence('7ea98d5abb75eba43d3a20a03bc6adeded55831ac46d5be48bb097d584a24d78', report=True, behaviour=False, network=False)


    previous_samples = []
    previous_samples = read_hashes_from_file('miners_md5_hashes.txt')

    # ------- RETRIEVE RESOURCE FROM LIST... in inverse order
    for resource in reversed(LIST_HASHES):
        hash_samples = list(reversed(read_hashes_from_file(resource)))
        print '[i] Querying %d from %s' % (len(hash_samples), resource)
        retrieve_intelligence_many(hash_samples, report=True, behaviour=False, network=False, binary=False, output_folder=OUTPUT_FOLDER, previous_samples=previous_samples)
        get_reports_parents_by_hash(os.path.join(OUTPUT_FOLDER, 'reports'), hash_samples)
