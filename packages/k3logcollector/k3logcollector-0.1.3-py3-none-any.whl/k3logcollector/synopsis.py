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
    "front_error_log": {
        "file_path": "path/to/log/file/xxx.error.log",
        "level": ["warn", "error"],
        "is_first_line": is_first_line,
        "get_level": get_level,
        "parse": parse,
    },
}

kwargs = {
    "node_id": "123abc",
    "node_ip": "1.2.3.4",
    "send_log": send_log,
    "conf": conf,
}

k3logcollector.run(**kwargs)
