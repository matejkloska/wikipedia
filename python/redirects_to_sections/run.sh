#!/bin/bash

function log {
    now="$(date +'%d.%m.%Y %H:%M:%S')"
    printf "[%s] %s\n" "$now" "$1"
}

start_time=`date +%s`

# arguments
ROOT=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
SRC_DIR="$ROOT/src"
S_JAR=$1
INPUT_XML=`realpath $2`
ES_HOST="localhost"
ES_PORT="9200"
ES_INDEX="redirects-sections-index"

# dirs
MAP_LINK_OUTPUT_DIR="$ROOT/output_p1"
MAP_LINK_OUTPUT_FINAL_DIR="$ROOT/output_p2"

# workers
LINKS_MAPPER="python $SRC_DIR/links_mapper.py"
LINKS_REDUCER="python $SRC_DIR/links_reducer.py"
LINKS_MAPPER_FINAL="python $SRC_DIR/texts_mapper.py $MAP_LINK_OUTPUT_DIR"

# hadoop settings
INPUT_SIZE_MIN="mapreduce.input.fileinputformat.split.minsize=512000000"
INPUT_SIZE_MAX="mapreduce.input.fileinputformat.split.maxsize=512000000"
LINKS_REDUCERS="mapreduce.job.reduces=10"
LINKS_MAPPERS="mapreduce.job.maps=10"
TEXTS_REDUCERS="mapreduce.job.reduces=0"
TEXTS_MAPPERS="mapreduce.job.maps=10"

log "Process started"

log "Purging tmp_output"
rm -r $MAP_LINK_OUTPUT_DIR

log "Running links hadoop job"
hadoop jar $S_JAR -D $INPUT_SIZE_MIN -D $INPUT_SIZE_MAX -D $LINKS_REDUCERS -D $LINKS_MAPPERS -mapper "$LINKS_MAPPER" -reducer "$LINKS_REDUCER" -input "file://$INPUT_XML" -output "file:///$MAP_LINK_OUTPUT_DIR"
log "Hadoop links job done"

log "Purging final output"
rm -r $MAP_LINK_OUTPUT_FINAL_DIR

log "Running sections hadoop job"
hadoop jar $S_JAR -D $INPUT_SIZE_MIN -D INPUT_SIZE_MAX -D $TEXTS_REDUCERS -D $TEXTS_MAPPERS -mapper "$LINKS_MAPPER_FINAL" -input "file:///$INPUT_XML" -output "file:///$MAP_LINK_OUTPUT_FINAL_DIR"
log "Hadoop sections job done"

log "Removing ElasticSearch index"
curl -XDELETE 'http://$ES_HOST:$ES_PORT/$ES_INDEX/'
echo
log "Creating ElasticSearch index"
curl -XPUT "http://$ES_HOST:$ES_PORT/$ES_INDEX" -d'
{
  "mappings" : {
    "test-type" : {
      "properties" : {
        "source" : {
          "type" : "string",
          "search_analyzer" : "str_search_analyzer",
          "index_analyzer" : "str_index_analyzer"
        },
        "section" : {
          "type" : "string",
          "search_analyzer" : "str_search_analyzer",
          "index_analyzer" : "str_index_analyzer"
        },
        "target_page" : {
          "type" : "string",
          "search_analyzer" : "str_search_analyzer",
          "index_analyzer" : "str_index_analyzer"
        },
        "link_text" : {
          "type" : "string",
          "search_analyzer" : "str_search_analyzer",
          "index_analyzer" : "str_index_analyzer"
        }
      }
    }
  },

  "settings" : {
    "analysis" : {
      "analyzer" : {
        "str_search_analyzer" : {
          "tokenizer" : "keyword",
          "filter" : ["lowercase"]
        },

        "str_index_analyzer" : {
          "tokenizer" : "keyword",
          "filter" : ["lowercase", "substring"]
        }
      },
      "filter" : {
        "substring" : {
          "type" : "nGram",
          "min_gram" : 4,
          "max_gram"  : 20
        }
      }
    }
  }
}'
echo

python $SRC_DIR/results_dump.py $ES_HOST $ES_PORT $ES_INDEX $MAP_LINK_OUTPUT_FINAL_DIR

log "Process finished"

end_time=`date +%s`
log "Execution time: `expr $end_time - $start_time` s."