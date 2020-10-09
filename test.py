# from threading import Thread, Event
# import time
# from src.observables import ObservableDict
#
# def thread_fn(event, config):
#     print('Starting thread:', config['a'])
#     while not event.wait(1):
#         print('waiting...:', config['a'])
#         continue
#     print('Thread stopped')
#
# def main():
#     event = Event()
#
#     config = dict(a='a')
#     config = ObservableDict(config)
#     thread = Thread(target=thread_fn, args=(event,config))
#     thread.start()
#     config['a'] = 'b'
#     time.sleep(3)
#     event.set()
#     thread.join()
#
#
# main()
#


from dotenv import load_dotenv
import os

load_dotenv()

print(os.environ.get('asdf'))
