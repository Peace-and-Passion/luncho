import logging
import resource
import main

def post_worker_init(worker):
    logging.info('gunicorn_config.py post_worker_init')
    main.main(use_test_data=False)

    # https://github.com/benoitc/gunicorn/issues/1299
    #resource.setrlimit(resource.RLIMIT_AS, (419400000, 419400000)) #byte 400Mi (soft, hard)
    # resource.setrlimit(resource.RLIMIT_AS, (100, 100)) #byte 400Mi (soft, hard)
    # resource.setrlimit(resource.RLIMIT_CPU, (1, 1)) #byte 400Mi (soft, hard)
    # print("XXX")
    # print(getattr(resource.getrusage(resource.RLIMIT_AS),'ru_ixrss'))
    # print(getattr(resource.getrusage(resource.RUSAGE_SELF),'ru_ixrss'))

def on_starting(_server):
    # remove logging for /health
    logger = logging.getLogger("gunicorn.access")
    def myfilter(record: logging.LogRecord):
        line: str = record.args.get('r', '')
        if record.levelno == logging.INFO and record.args and line.startswith('GET /health'): #type: ignore
            return 0
        return 1
    logger.addFilter(myfilter)
