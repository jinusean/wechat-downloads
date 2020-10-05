def asdf():
    print('123')

from multiprocessing import Process
import multiprocessing

if __name__ == '__main__':
    multiprocessing.freeze_support()
    p = Process(target=asdf)
    p.start()
    p.join()
    print('done')