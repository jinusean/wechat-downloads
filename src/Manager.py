from lib.Singleton import Singleton
import logging

class Manager(metaclass=Singleton):
    _app = None
    _watchers = None
    def __init__(self, app):
        self._app = app
        self._watchers = []
    @property
    def app(self):
        return self._app

    @property
    def watchers(self):
        return self._watchers

    def add(self, obj, dir):
        obj_id = id(obj)
        cls_name = obj.__class__.__name__

        self.watchers.append((cls_name, obj_id, dir))
        logging.getLogger(cls_name).info('Start: ' + dir)

    def remove(self, obj, dir):
        obj_id = id(obj)
        cls_name = obj.__class__.__name__

        self.watchers.remove((cls_name, obj_id, dir))
        logging.getLogger(cls_name).info('Stop: ' + dir)

    def get_dirs_by_cls(self, cls_name):
        return [dir for (cls, obj_id, dir) in self.watchers if cls_name == cls]


