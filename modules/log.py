import logging

##log
#logging.basicConfig(level=logging.INFO,
logging.basicConfig(level=logging.DEBUG,
                format='%(asctime)s %(levelname)-5s %(filename)s[line:%(lineno)d] %(message)s',
                filename='/letv/server/logs/auto_publish/out.log',
                filemode='a')
