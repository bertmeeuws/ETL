import sys

sys.path.insert(0, "./producers")

from producers import megekko

print(megekko.scrape("gtx 1650"))
