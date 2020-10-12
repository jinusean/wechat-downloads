import time
from datetime import datetime
from pathlib import Path

path = '/Users/suah/Library/Containers/com.tencent.xinWeChat/Data/Library/Application Support/com.tencent.xinWeChat/2.0b4.0.9/793882e700a3e1cc5a272b7250085985/Message/MessageTemp/7830407957a874fa5bbe67a10f14cebe/Video'
path = Path(path)

stat = path.stat()
last = stat.st_mtime
print(datetime.fromtimestamp(last))