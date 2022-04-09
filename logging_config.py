

dict_config = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "base": {
            "format": "%(levelname)s | %(asctime)s | %(funcName)s() | %(lineno)d | %(message)s"
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            # "level": "DEBUG",
            "level": "WARNING",
            "formatter": "base"
        },
        "file": {
            "class": "logging.FileHandler",
            "level": "WARNING",
            "formatter": "base",
            "filename": "logfile.txt",
            "mode": "a"
        }
    },
    "loggers": {
        "check": {
            "level": "DEBUG",
            "handlers": ["file", "console"],
            # "propagate": False,
        }
    },

    # "filters": {},
    # "root": {} # == "": {}
}