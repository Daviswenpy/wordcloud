#!/bin/bash
#
# "Script to rotate Elasticsearch logs given the index pattern and number of days."
# Index names must contain date string in format YYYY.MM.DD
#
abort() {
  echo "Usage: $0 <indexpattern> <elasticsearch URL> <ts_keyword> <days to keep>"
  echo "Example: $0 cspdata https://something.somewhere.es.amazonaws.com timestamp 30"
  echo $WRONG_PARAMS
  exit 1
}

if [[ "$#" -ne 4 ]] ;
then
  WRONG_PARAMS="ERROR: I need 4 paramenters."
  abort
fi

LANG=C
echo "=== `date` ==="
echo "Arguments: " $@

oldest_ts=$(date -Iseconds --date="-$4 day")
query_delete='{ "query": { "bool": { "filter": [ { "range": { "'$3'": { "lt": "'$oldest_ts'"} } } ] } } }'

echo $query_delete

result=$(curl -s -XPOST $2/$1/_delete_by_query -H 'Content-Type: application/json' -d "$query_delete")
echo -e "$result\n"
#echo $result | jq

# POST ep_dlp-2020.08.14/_delete_by_query
# {
#   "size": 10,
#   "query": {
#     "bool": {
#       "must": [
#         {"match": {
#           "event_type": "DLP_IM_MESSAGE"
#         }}
#       ]
#     }
#   }
# }

# {
#   "query": {
#     "bool": {
#       "filter": [
#         {
#           "range": {
#             "timestamp": {
#               "lt": "2020-08-06T08:30:00+0800"
#             }
#           }
#         }
#       ]
#     }
#   }
# }

