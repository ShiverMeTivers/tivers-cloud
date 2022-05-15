import json
import requests
import datetime
import hashlib
import hmac
import base64
import argparse 
import logging  
from dataclasses import dataclass
from pprint import pprint
from elastic_q import query_repo 


@dataclass
class Configs:
    tmp_log_name : str
# Update the customer ID to your Log Analytics workspace ID
    customer_id  :str ='fcee8395-b70e-4691-a6ad-febedb9b9368'
# For the shared key, use either the primary or the secondary Connected Sources client authentication key   
    shared_key : str ="3naHYH0+P6x7isSIjh2+jacPWcqV/lsIEUVmfQV5fwGoF+lWlzPKTjtBGNh1dLjzRQci4+yxChUlutsuP0rv7A=="
# The log type is the name of the event that is being submitted
    custom_table_name : str ='WebMonitorTest5'
#Set the Time stamp to use on ingestion
    timestampfield : str = '@timestamp'
#IP address of Elastichsearch API
    url: str = '10.3.0.4:9200/'
#The specific command given to the API
    query: str = 'test-index/_search/?pretty'
#Username and Password Auth
    auth: str = 'elastic:ckHJq*5nGSP6V212N_EU'
    #temp log directory
    tmp_log_dir : str = '/tmp/'
#max log_size 28M 
    max_size: int = 3_000_000#28_000_000
#how many chunks to create if the request is too large
    bin_amt: int = 3
    # the date which you last ingested logs 
    last_sync_date : str = "2022-05-07T12:58:51.000Z"
    divisor: int = 1_000_000 # 1M

logging.basicConfig(filename="debug.txt",level=logging.DEBUG,encoding='utf-8',format="%(asctime)s -- %(message)s -- %(funcName)s")
logging.getLogger('urllib3').setLevel(logging.CRITICAL)


def extract_recent_logs(log_data :dict,configs):
    # need another if statement for order : strong assumption of sorted 
    filtered_data = {}
    do_consume = True
    pprint(configs)
    for index,log_hit in enumerate(log_data['hits']['hits']):
        if compare_timestamps(configs.last_sync_date, log_hit['fields'][configs.timestampfield][0]) is True:
            filtered_data[index] = log_hit['fields']
            filtered_data[index]['sort'] = log_hit['sort']
            filtered_data['sort'] = log_hit['sort']

        else:
            do_consume = False
            break 
    log_amt = len(log_data['hits']['hits'])
    filtered_data['log_amt'] = log_amt
    filtered_data['other_field_cnt'] = 3  #hard coding for alpha
    logging.debug(f"extract recent logs returned")
    pprint(filtered_data[0])
    return filtered_data, do_consume        


def compare_timestamps(baseline_time , cmp_time):
    #assuming we are utilizing the ISO standard if cmp_time is smaller
    # then it is an older value than the baseline 
    if cmp_time < baseline_time:
        return False
    else:
        return True

def extract_sort_index(data : dict,sort_flag=True):
	# TODO  need to update if chunks are passed and each chunk has the proceeding sort index value 
    if sort_flag is True:
        return data[0]['sort'][0]
    else:
        return data[-1]['sort'][0]

def chunking_check(content_len,configs):
    # check if the request is over a specified size. 
    logging.debug(f"the payload size {int(content_len)/1_000_000}")
    if int(content_len) > configs.max_size:
        return True
    return False     
    
def create_chunks(data, content_len, configs):
    #return a list of chunked data to avoid the size cap

    chunked_data = list()
    logs_amt = len(data)-data['other_field_cnt']
#n-1 bins will have the even amount while nth will have the remainder 
    entries_per_bin = logs_amt//configs.bin_amt
    for i in range(configs.bin_amt-1): # need to find a cleaner way to break up the list, maybe slices
        chunk = list() 
        for log_index in range(entries_per_bin*i,entries_per_bin*(i+1),1):
            data[log_index]['sort']=data['sort']
            chunk.append(data[log_index])
        chunked_data.append(chunk)            
    last_chunk = list()
    logging.debug(f" entries-per-bin: {entries_per_bin}, logs per bin: {configs.bin_amt},  total logs: {logs_amt}")
    for log_index in range(entries_per_bin*(configs.bin_amt-1),logs_amt,1):
            last_chunk.append(data[log_index])
    chunked_data.append(last_chunk)
    return chunked_data            


##Both searches need the config and chunk checks to work
#extract recent then chunk to avoid different formats of data 
def initial_search(configs):
    #use for the first search
    answer=get_logs(configs.url, configs.query, configs.auth,query=query_repo['processes'])
    data = json.loads(answer.text)
    print(int(answer.headers['content-length'])/configs.divisor)
    chunk_flag= chunking_check(answer.headers['content-length'],configs)    
    if chunk_flag is True:
        parsed_logs, _ = extract_recent_logs(data,configs)
        chunked_data = create_chunks(parsed_logs,answer.headers['content-length'],configs)
        sort_index =None
        for index, chunk in enumerate(chunked_data):
          print(len(chunk))  
          sort_index = extract_sort_index(chunk,True) # The assumption is the last log collected is the next index with asc order
##        post_data(configs.customer_id, configs.shared_key, configs.custom_table_name,parsed_logs,configs)  
        logging.debug(f"initial search hit the chunking loop {index}")
        return sort_index
    else:
        parsed_logs, _ = extract_recent_logs(data,configs)
        sort_index = extract_sort_index(parsed_logs,True) # this will be made agnostic?? if we do reverse oder this function blows up
##        post_data(configs.customer_id, configs.shared_key, configs.custom_table_name,parsed_logs,configs)  
        logging.debug(f"initial search returned {len(parsed_logs)} logs")
        return sort_index
    
def search_after(configs,sort_index: int ):
    #This function is called after the initial search and will continue to pull logs until the provided timestamp is reached
    fetch_flag = True
    consume_flgag = True
    while fetch_flag is True:          
        query_repo['process_search_a']['search_after'][0] = sort_index # this is replacing a string in the elastic_q.py 
        answer=get_logs(configs.url,configs.query, configs.auth,query=query_repo['process_search_a'])
        data = json.loads(answer.text)
        chunk_flag= chunking_check(answer.headers['content-length'],configs)    
        if chunk_flag is True:
            logging.debug("search_after chunk")
            parsed_logs, consume_flag = extract_recent_logs(data,configs)
            chunked_data = create_chunks(parsed_logs,answer.headers['content-length'],configs)
            for log_chunk in chunked_data:
                sort_index = extract_sort_index(log_chunk,True) # assumes the desc order for oldest value
                post_data(configs.customer_id, configs.shared_key, configs.custom_table_name,log_chunk,configs.timestampfield)  # a lot of globals
            if consume_flag is False:
                fetch_flag= False
                break
        else:
            try:
                sort_index,consume_flag = extract_sort_index(data)    
                logging.debug("search after ret")
                post_data(configs.customer_id, configs.shared_key, configs.custom_table_name,parsed_logs,configs.timestampfield)  # a lot of globals
            except Exception as e_http:
                logging.debug("hit the post",e_http)
                fetch_flag = False
            if consume_flag is False:
                fetch_flag= False
    return 

def get_logs(url,endpoint,auth,**kwargs):
#Create HTTP URI  use kwargs
    question = 'https://' + auth + '@' + url + endpoint
    answer = requests.get(question, json=kwargs['query'] , verify=False)
    return answer


# Build the API signature
def build_signature(customer_id, shared_key, date, content_length, method, content_type, resource):
    x_headers = 'x-ms-date:' + date
    string_to_hash = method + "\n" + str(content_length) + "\n" + content_type + "\n" + x_headers + "\n" + resource
    bytes_to_hash = bytes(string_to_hash, encoding="utf-8")  
    decoded_key = base64.b64decode(shared_key)
    encoded_hash = base64.b64encode(hmac.new(decoded_key, bytes_to_hash, digestmod=hashlib.sha256).digest()).decode()
    authorization = "SharedKey {}:{}".format(customer_id,encoded_hash)
    return authorization

# Build and send a request to the POST API
def post_data(customer_id, shared_key, custom_table_name,post_data,timestampfield):

    method = 'POST'
    content_type = 'application/json'
    resource = '/api/logs'
    rfc1123date = datetime.datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')
    content_length = len(post_data)
    signature = build_signature(customer_id, shared_key, rfc1123date, content_length, method, content_type, resource)
    uri = 'https://' + customer_id + '.ods.opinsights.azure.us' + resource + '?api-version=2016-04-01'
    
    #Aded time-generated-field. Data without time is useless.
    #May need tweaking.
    headers = {
        'content-type': content_type,
        'Authorization': signature,
        'Log-Type': custom_table_name,
        'x-ms-date': rfc1123date,
        'time-generated-field': timestampfield
    }
    try:
        response = requests.post(uri,data=json.dumps(post_data), headers=headers)
        if (response.status_code >= 200 and response.status_code <= 299):
            print('Accepted')
        else:
            print("Response code: {}".format(response.status_code))
            logging.debug(f"Non 200 code {response.status_code}, message: {response.text}")
    except requests.exceptions.ConnectionError as con_error:
        logging.error(f"connection failed to establish {con_error}")  


def create_parser():
    #this function generates the cli arugment parser to allow for quicker customization and allow future personnel to understand the purpose..
    parser = argparse.ArgumentParser(description="This script pulls logs from the given elastic instance into the Hyperscale Log Analytics workspace. The default actions of the script will use the hardcoded creds (I know!) otherwise it will use the cli vlaues.")
    parser.add_argument("-skey","--shared-key",help="the shared key/credential for accessing the Log analytics workspace",default=False)
    parser.add_argument("-id","--workspace-id",help="The workspace id of the log analytics workspace.",default=False)
    parser.add_argument("-qcred","--elastic-cred",help="The elastic credentials to query for logs. formtat is username:xxxxxxxx",default=False)
    parser.add_argument("-ctab","--custom-table",help="The name of the custom table to create/push to in Log Analytics",default=False)
    parser.add_argument("-path",help="Give an absolute path to the directory to write debug output",default=False)
    parser.add_argument("-timestamp",help="The last time the script was used. This will cause the script to gather most logs from current date till the provided timestamp. Format: 2022-05-02T03:58:51.000Z",       default=False)
    parser.add_argument("-divisor","--divisor-size", help="The unit used when displaying the amount of bytes receieved.",default=False)
    parser.add_argument("-binamt","--bin-amount", help="The amount of chunks to generate if the max-size is reached.",default=False)
    parser.add_argument("-maxsize","--max-postsize", help="The max amount of data that can be sent in a single request to Azure.",default=False)
    return parser

def check_cli_values(cli_args,config):
    # need to pass the global config object to update the fields**
    if cli_args.shared_key is not False:
        config.shared_key = cli_args.shared_key    

    elif cli_args.workspace_id is not False:
        config.customer_id = cli_args.workspace_id
    
    elif cli_args.elastic_cred is not False:
        config.auth = cli_args.elastic_cred
    
    elif cli_args.custom_table is not False:
        config.custom_table_name = cli_args.custom_table    
    
    elif cli_args.path is not False:
         config.tmp_log_dir = cli_args.path

    elif cli_args.timestamp is not False:
         print(cli_args.timestamp)
         config.last_sync_date =cli_args.timestamp 
  
    elif cli_args.divisor_size is not False:
         config.divisor =cli_args.divisor_size 
  
    elif cli_args.bin_amount is not False:
         config.bin_amt =cli_args.bin_amount
  
    elif cli_args.max_postsize is not False:
         config.max_size =cli_args.max_postsize 
  
    else:
        logging.info("Using default configs")
    return config

if __name__ == '__main__':
    config_global = Configs("Environmental variables")
    parser = create_parser()
    cli_arg=parser.parse_args()
    config_global=check_cli_values(cli_arg,config_global)
    sort_vals = initial_search(config_global)
    search_after(config_global, sort_vals)
