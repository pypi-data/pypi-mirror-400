import time

class Logger:
    @staticmethod
    def error(log_type: str, err: str):
        t = time.localtime()
        timestamp = "{:04}-{:02}-{:02} {:02}:{:02}:{:02}".format(t[0], t[1], t[2], t[3], t[4], t[5])
        print("[{}] [{}] - ERROR - {}".format(timestamp, log_type, err))

    @staticmethod
    def log(log_type: str, msg: str):
        t = time.localtime()
        timestamp = "{:04}-{:02}-{:02} {:02}:{:02}:{:02}".format(t[0], t[1], t[2], t[3], t[4], t[5])
        print("[{}] [{}] - {}".format(timestamp, log_type, msg))
