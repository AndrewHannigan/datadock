import sys
from datadock import Dock

with open(sys.argv[1], 'r') as f:
    sql = f.read()
    dock = Dock(sql)
    dock.run()
