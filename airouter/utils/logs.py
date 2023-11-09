import logging

def get_logger(name, level=logging.DEBUG):
  # create logger
  logger = logging.getLogger(name)
  logger.setLevel(level)

  # create console handler
  ch = logging.StreamHandler()
  ch.setLevel(level)

  # create formatter
  formatter = logging.Formatter('%(levelname)s: %(name)s - %(asctime)s - %(message)s')

  # add formatter to console handler
  ch.setFormatter(formatter)

  # add console handler to logger
  logger.addHandler(ch)
  return logger
