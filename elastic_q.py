## store elastic queries


query_repo = {
"processes":
{
  "size": 10000,
  "_source": False,
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
        "process.pid",
        "_id"]
,"sort":[{
"@timestamp":"desc"
        }
]},
"process_search_a":{ 
"size": 10000,
"_source": False,
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
        "process.pid",
        "_id"],
  "search_after": [1652215168000],
  "sort": [
       {"@timestamp":"desc"}
    ],
  }
}

