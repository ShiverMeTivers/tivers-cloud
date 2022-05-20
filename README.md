# Overview
The objective of this script to forward specific logs from an Elastic instance into an Azure Log Analytic workspace. The script utilizes the Data Collector API to push the data into a specifc workspace.

## Why
An individual may need to transfer logs from their existing SIEM solution to Azure. In the event that certificates can't be genreated and added to ensure that Logstash functions, this script provides a simple way to transfer logs. An individual provides the script the date of the last transfer and ensures the reveleant queries are stored in `elastic_q.py`. The script then will proceed to query the Elastic instance and chunk the logs into smaller reuests to avoid Azure ingestion limits of 30MB per post request.


## Run
The provided file will require you to change the default config strings either over the cli or within the file.Else the `debug.txt` file will contain failed request entries. This was tested on Ubuntu 21.10 and python3.9
```
2022-05-20 03:16:08,513 -- connection failed to establish HTTPSConnectionPool(host='xxxxxxx.ods.opinsights.azure.us', port=443): Max retries exceeded with url: /api/logs?api-version=2016-04-01 (Caused by NewConnectionError('<urllib3.connection.HTTPSConnection object at 0x7f314c1f1b50>: Failed to establish a new connection: [Errno -2] Name or service not known')) {'content-type': 'application/json', 'Authorization': 'SharedKey XXXXXXX:EH/fCcWw/RbSg8yo1o1bSlUtavLBHoVfHsqP3rGBscI=', 'Log-Type': 'WebMonitorTest5', 'x-ms-date': 'Fri, 20 May 2022 03:16:08 GMT', 'time-generated-field': '@timestamp'} -- post_data
```
Below is a default run without any of the cli flags in use and excerpt of `debug.txt`. 
```
python3 refactor.py 

cat debug.txt 
2022-05-20 03:15:55,678 -- initial search returned 13 logs -- initial_search
2022-05-20 03:15:56,116 -- the payload size 6.550061 -- chunking_check
2022-05-20 03:15:56,116 -- search_after chunk -- search_after
2022-05-20 03:15:56,122 -- extract recent logs returned -- extract_recent_logs
2022-05-20 03:15:56,123 --  entries-per-bin: 3333, logs per bin: 3,  total logs: 10000 -- create_chunks
```
 
## CLI Flags
The command line flags allow an user to overwrite the default values stored in the `dataclass Config object`.
```
  -h will return an overview of all the flags

  -skey SHARED_KEY, --shared-key SHARED_KEY
                        the shared key/credential for accessing the Log analytics workspace
  -id WORKSPACE_ID, --workspace-id WORKSPACE_ID
                        The workspace id of the log analytics workspace.
  -qcred ELASTIC_CRED, --elastic-cred ELASTIC_CRED
                        The elastic credentials to query for logs. formtat is username:xxxxxxxx
  -ctab CUSTOM_TABLE, --custom-table CUSTOM_TABLE
                        The name of the custom table to create/push to in Log Analytics
  -path PATH            Give an absolute path to the directory to write debug output

  -timestamp TIMESTAMP  The last time the script was used. This will cause the script to gather most logs from current date till the provided timestamp. Format: 2022-05-02T03:58:51.000Z_global)
 
  -divisor DIVISOR_SIZE, --divisor-size DIVISOR_SIZE
                        The unit used when displaying the amount of bytes receieved.
  -binamt BIN_AMOUNT, --bin-amount BIN_AMOUNT
                        The amount of chunks to generate if the max-size is reached.
  -maxsize MAX_POSTSIZE, --max-postsize MAX_POSTSIZE
                        The max amount of data that can be sent in a single request to Azure.
```
## TODO
   Add a failed queue and retry request  
   Generalize for elastic queries  
   Imrove the logging messages and levels
   Add unit-tests

## References
[Azure Monitor limits](https://docs.microsoft.com/en-us/azure/azure-monitor/service-limits)  
[The basic Microsoft Script](https://docs.microsoft.com/en-us/azure/azure-monitor/logs/data-collector-api)  


