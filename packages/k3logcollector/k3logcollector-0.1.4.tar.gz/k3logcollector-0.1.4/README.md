# k3logcollector

[![Action-CI](https://github.com/pykit3/k3logcollector/actions/workflows/python-package.yml/badge.svg)](https://github.com/pykit3/k3logcollector/actions/workflows/python-package.yml)
[![Documentation Status](https://readthedocs.org/projects/k3logcollector/badge/?version=stable)](https://k3logcollector.readthedocs.io/en/stable/?badge=stable)
[![Package](https://img.shields.io/pypi/pyversions/k3logcollector)](https://pypi.org/project/k3logcollector)

Scan log files on local machine, collector all interested logs, and send to somewhere for display.

k3logcollector is a component of [pykit3] project: a python3 toolkit set.


#   Name

logcollector

Scan log files on local machine, collector all interested logs, and send
to somewhere for display.

#   Description

We may want to see all error logs on all machines, so we need to collector
logs, and save it in somewhere. This module is used to collector logs on one
machine.

Normally, same error info will be loged repeatedly, we do not want
to save duplicated log info, so logs produced by same source file at
same line number in one second will be combined.

#   Conf

configuration for log files. It is a dict, the key is the log name, the value
is the configuration for the log.

## file_path

the path of the log file.

## is_first_line

is a callback function.
The argument to this function is a line in log file, if the line is the
first line of a log, then return `True`, otherwise return `False`.

## get_level

is a callback function.
The argument to this function is the complete log string, which may contains
multiple lines. It should return the level of the log, which is a string.

## parse

is a callback function.
The argument to this function is the complete log string, which may contains
multiple lines. It should return a dict contains following fields.

-   log_ts:
    the timestamp of this log, such as `1523936052`, is a integer.

-   level:
    the level of this log, such as 'info'.

-   source_file:
    the source file in which the log was produced.

-   line_number:
    the number of the line at which the log was produced.

## level

is a list, used to specify the interested log levels.




# Install

```
pip install k3logcollector
```

# Synopsis

```python

import k3logcollector


def send_log(log_entry):
    print("send the log entry to database or other place.")


def is_first_line(line):
    print("return True if the line is the first line of a log,")
    print("otherwise return False.")


def get_level(log_str):
    print("return the level of the log.")


def parse(log_str):
    print("parse the log.")


conf = {
    'front_error_log': {
        'file_path': 'path/to/log/file/xxx.error.log',
        'level': ['warn', 'error'],
        'is_first_line': is_first_line,
        'get_level': get_level,
        'parse': parse,
    },
}

kwargs = {
    'node_id': '123abc',
    'node_ip': '1.2.3.4',
    'send_log': send_log,
    'conf': conf,
}

k3logcollector.run(**kwargs)

```

#   Author

Zhang Yanpo (张炎泼) <drdr.xp@gmail.com>

#   Copyright and License

The MIT License (MIT)

Copyright (c) 2015 Zhang Yanpo (张炎泼) <drdr.xp@gmail.com>


[pykit3]: https://github.com/pykit3