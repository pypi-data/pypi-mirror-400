#!/bin/bash

# This script monitors a directory for any newly created files that match a given regex.
# If a file matches, this script launches a 'tail -f' upon it.
# Designed for usage with strace traces specifically, this script takes extra attention with them.
# Files with '.trace' are assumed to have a PID at the end of their filename, which is used with 'tail -f --pid <PID>'

# TARGET is the directory to monitor for new files
# REGEX is the pattern to grep for on any new file

TARGET=$1
REGEX=$2

DATE="date -u +%Y-%m-%dT%H:%M:%S.%6N"

function basic_format() {
    # Uses the time from `date` as when the log appeared
    while IFS= read line; do
        echo $line | sed \
            -e "s/^/{\"date\": \"$($DATE)\", \"msg\": \"/" \
            -e 's/$/"/' \
            -e "s/$/, \"hostname\": \"$(hostname)\"/" \
            -e "s/$/, \"tailf_filename\": \"$FNAME\"/" \
            -e 's/$/}/'
    done
}

function strace_format() {
    # Parses the date in the strace log instead of using the time from `date`
    while IFS= read line; do
        echo $line | sed \
            -e 's/ /", "msg": "/' \
            -e "s/^/{\"date\": \"$(date -u +%Y-%m-%dT)/" \
            -e 's/$/"/' \
            -e "s/$/, \"hostname\": \"$(hostname)\"/" \
            -e "s/$/, \"tailf_filename\": \"$FNAME\"/" \
            -e 's/$/}/'
    done
}

echo $($DATE) $0 started

# Wait until the directory in question exists
if [ ! -d ${TARGET} ]; then
    mkdir -p ${TARGET}
fi

echo $($DATE) ${TARGET} created

# Follow any file created in that directory that matches the regex
inotifywait -m -e create --format "%f" ${TARGET} |
    while read FNAME; do
        echo $($DATE) ${FNAME}
        if echo $FNAME | grep -q -E "${REGEX}"; then
            echo $($DATE) ${TARGET}/${FNAME}
            if echo $FNAME | grep -q '.trace'; then
                tail -f ${TARGET}/${FNAME} --pid=$(echo $FNAME | rev | cut -d '.' -f '1' | rev) | strace_format &
            else
                tail -f ${TARGET}/${FNAME} | basic_format &
            fi
        fi
    done
