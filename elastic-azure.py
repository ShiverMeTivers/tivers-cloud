import json
import requests
import datetime
import hashlib
import hmac
import base64

##### ##### ##### ##### ##### ##### 
##### Azure Push Variables Start
##### ##### ##### ##### ##### ##### 

# Update the customer ID to your Log Analytics workspace ID
customer_id = 'fcee8395-b70e-4691-a6ad-febedb9b9368'

# For the shared key, use either the primary or the secondary Connected Sources client authentication key   
shared_key = "3naHYH0+P6x7isSIjh2+jacPWcqV/lsIEUVmfQV5fwGoF+lWlzPKTjtBGNh1dLjzRQci4+yxChUlutsuP0rv7A=="

# The log type is the name of the event that is being submitted
log_type = 'WebMonitorTest5'

#Set the Time stamp to use on ingestion
timestampfield = '@timestamp'

##### ##### ##### ##### ##### ##### 
##### Elastic Pull Variables Start
##### ##### ##### ##### ##### ##### 
#IP address of Elastichsearch API
url = 'localhost:9200/'

#The specific command given to the API
query = 'test-index/_search/?pretty'

#The query used by elastichsearch query API
body = '''
{
  "size": 10000,
  "_source": false,
  "query": {
    "match": {
      "log.syslog.facility.name": "security/authorization"
    }
  },
  "fields": [
    "message",
	"@timestamp",
	"host.hostname",
	"host.ip",
	"process.name",
	"process.pid"
	]
}
'''
#Username and Password Auth
auth = 'elastic:ckHJq*5nGSP6V212N_EU'
#temp log directory
tmp_log_dir = '/tmp/'
#
tmp_log_name = 'tmp.log'

##### ##### ##### ##### 
##### Elastich Pull Functions
##### ##### ##### ##### 

def get_logs(url,query,auth):
#Create HTTP URI
    question = 'https://' + auth + '@' + url + query
    #Create JSON Object for HTTP Data
    data = json.loads(body)
    #print(question)

    answer = requests.get(question, json=data , verify=False)
    #answer_json=json.loads(answer['hits']['hits']).
    #print(answer.text)
    ##answer_json=json.dumps(answer.text)
    return answer.text

def save_logs(logs, tmp_log_dir, tmp_log_name):
    log_file = open(tmp_log_dir + tmp_log_name, 'w')
    #json.dump(logs, log_file)
    log_file.write(logs)
    log_file.close()
    return 

##### ##### ##### ##### 
##### Azure Push Functions
##### ##### ##### ##### 

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
def post_data(customer_id, shared_key, log_type,tmp_log_dir, tmp_log_name):
    
    #Maximum Jank - Holman
    # Open json text file and read as str obj to variable
    log_file = open(tmp_log_dir + tmp_log_name, 'r')
    log_file_data = log_file.read()
    #parse json text as dict and remove unneeded dictionary entries
    py_logs = json.loads(log_file_data)
    post_data1 = json.dumps(py_logs['hits']['hits'])
    #close file handle and pontificate on what the fuck 
    post_data = json.loads(post_data1)
    log_file.close()

    method = 'POST'
    content_type = 'application/json'
    resource = '/api/logs'
    rfc1123date = datetime.datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')
    content_length = len(post_data1)
    signature = build_signature(customer_id, shared_key, rfc1123date, content_length, method, content_type, resource)
    uri = 'https://' + customer_id + '.ods.opinsights.azure.us' + resource + '?api-version=2016-04-01'
    
    #Aded time-generated-field. Data without time is useless.
    #May need tweaking.
    headers = {
        'content-type': content_type,
        'Authorization': signature,
        'Log-Type': log_type,
        'x-ms-date': rfc1123date,
        'time-generated-field': timestampfield
    }

    response = requests.post(uri,data=post_data1, headers=headers)
    if (response.status_code >= 200 and response.status_code <= 299):
        print('Accepted')
    else:
        print("Response code: {}".format(response.status_code))
    

logs = get_logs(url, query, auth)

save_logs(logs, tmp_log_dir, tmp_log_name)

post_data(customer_id, shared_key, log_type,tmp_log_dir, tmp_log_name)
