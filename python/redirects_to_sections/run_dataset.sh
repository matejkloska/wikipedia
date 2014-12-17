#!/bin/bash

function log {
    now="$(date +'%d.%m.%Y %H:%M:%S')"
    printf "[%s] %s\n" "$now" "$1"
}

start_time=`date +%s`

ROOT=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
SRC_DIR="$ROOT/src"
S_JAR=$1
INPUT_XML=`realpath $2`

# dirs
OUTPUT_DIR="$ROOT/output_dataset"

# hadoop settings
INPUT_SIZE_MIN="mapreduce.input.fileinputformat.split.minsize=512000000"
INPUT_SIZE_MAX="mapreduce.input.fileinputformat.split.maxsize=512000000"

# workers
MAPPER="python $SRC_DIR/dataset_stats_mapper.py"
REDUCER="python $SRC_DIR/dataset_stats_reducer.py"

log "Process started"

log "Purging output dir"
rm -r $OUTPUT_DIR

log "Running links hadoop job"
hadoop jar $S_JAR -D $INPUT_SIZE_MAX -D $INPUT_SIZE_MIN -D mapreduce.job.reduces=10 -mapper "$MAPPER" -reducer "$REDUCER" -input "file:///$INPUT_XML" -output "file:///$OUTPUT_DIR"
log "Hadoop links job done"

log "Process finished"

end_time=`date +%s`
log "Execution time: `expr $end_time - $start_time` s."