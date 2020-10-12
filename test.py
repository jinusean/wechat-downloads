import time
from src.utils import iter_files

path = '/Users/suah/Library/Containers/com.tencent.xinWeChat/Data/Library/Application Support/com.tencent.xinWeChat/2.0b4.0.9/793882e700a3e1cc5a272b7250085985/Message/MessageTemp'



files = list(map(lambda x: x.stat().st_mtime, iter_files(path)))
for i in range(len(files) - 1):
    print(files[i] > files[i + 1])
