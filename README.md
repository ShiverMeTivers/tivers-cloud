# Overview
The objective of this script to forward specific logs from an Elastic instance into an Azure Log Analytic workspace. The script utilizes the Data Collector API to push the data into a specifc workspace.

## Why
An individual may need to transfer logs from their existing SIEM solution to Azure. In the event that certificates can't be genreated and added to ensure that Logstash functions, this script provides a simple way to transfer logs.An individual provides the script the date of the last transfer and ensures the reveleant queries are stored in `elastic_q.py`. The script then will proceed to query the Elastic instance and chunk the logs into smaller reuests to avoid Azure ingestion limits of 30MB per post request.

 
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
   Add additional Flags to set the bin_amount and the max message size  
   Add a failed queue and retry request  
   Generalize for elastic queries  

## References
[Azure Monitor limits](https://docs.microsoft.com/en-us/azure/azure-monitor/service-limits)  
[The basic Microsoft Script](https://docs.microsoft.com/en-us/azure/azure-monitor/logs/data-collector-api)  


