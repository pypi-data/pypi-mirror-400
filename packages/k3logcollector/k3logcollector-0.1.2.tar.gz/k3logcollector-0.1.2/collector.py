import logging
import queue
import threading
import time
from datetime import datetime

import k3thread
from k3logcollector import cache_flusher
from k3logcollector import scanner
from k3logcollector import sender

logger = logging.getLogger(__name__)


def run(**kwargs):
    # Following is all the valid keyword arguments.
    # -   `node_ip`:
    # the ip of this machine. Required.
    #
    # -   `send_log`:
    # a callback function, the argument to this function is the log entry,
    # which contains following fields. Required.
    #
    # -   level:
    # the level of the log.
    #
    # -   log_ts:
    # the timestamp of the log.
    #
    # -   content:
    # the full content of the log.
    #
    # -   log_name:
    # the name of the log, specified in configuration.
    #
    # -   log_file:
    # the file name of the log file.
    #
    # -   source_file:
    # the source file in which the log was produced.
    #
    # -   line_number:
    # the number of the line at which the log was produced.
    #
    # -   node_id:
    # the id of the machine on which the log was produced.
    #
    # -   node_ip:
    # the ip of the machine on which the log was produced.
    #
    # -   count:
    # how many times this log repeated.
    #
    # -   `conf`:
    # the configuration of all log files to scan. Required.
    context = {
        "node_id": kwargs["node_id"],
        "node_ip": kwargs["node_ip"],
        "send_log": kwargs["send_log"],
        "conf": kwargs["conf"],
        "cache_lock": threading.RLock(),
        "cache": {},
        "stat": {},
        "queue": queue.Queue(1024 * 10),
    }

    # strptime not thread safe, need to call it manually before
    # initiating any thread
    datetime.strptime("2011-04-05", "%Y-%m-%d")

    for log_name in list(context["conf"].keys()):
        context["cache"][log_name] = {}
        context["stat"][log_name] = {}

        k3thread.daemon(scanner.scan, args=(context, log_name))

    k3thread.daemon(cache_flusher.run, args=(context,))

    k3thread.daemon(sender.run, args=(context,))

    while True:
        # actually it is not an error log, but normally we only report
        # error log, and we want to report this log even it is not
        # an error log.
        logger.error("stat: %s" % context["stat"])

        time.sleep(100)
