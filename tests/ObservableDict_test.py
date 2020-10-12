from unittest import TestCase
from observables import ObservableDict


class ObservableDictTest(TestCase):
    def setUp(self):
        self.dict = dict(a='a', b=1, d=[1,2,3], dict=dict(a='a'))
        self.observable_dict = ObservableDict(self.dict)

    def test__getitem__(self):
        for key, value in self.dict.items():
            if key == 'dict':
                # dicts become observable dicts
                continue
            self.assertEqual(value, self.observable_dict[key])
        self.assertIsInstance(self.observable_dict['dict'], ObservableDict)


