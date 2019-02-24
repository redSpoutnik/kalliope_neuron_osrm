import unittest

from kalliope.core.NeuronModule import MissingParameterException, InvalidParameterException
from routing_machine import Routing_machine


class TestRouting_machine(unittest.TestCase):

    def setUp(self):
        self.latitude1 = 39
        self.longitude1 = 39
        self.latitude2 = 40
        self.longitude2 = 40
        self.invalid_alternatives = 1.7
        self.invalid_alternatives2 = -1
        self.invalid_alternatives3 = "5"

    def testNoParameters(self):
        with self.assertRaises(MissingParameterException):
            Routing_machine(**{})

    def testNoAction(self):
        with self.assertRaises(MissingParameterException):
            Routing_machine(**{
                "latitude1": self.latitude1,
                "longitude1": self.longitude1,
                "latitude2": self.latitude2,
                "longitude2": self.longitude2
            })

    def testMissingLatitude1(self):
        with self.assertRaises(MissingParameterException):
            Routing_machine(**{
                "distance": True,
                "longitude1": self.longitude1,
                "latitude2": self.latitude2,
                "longitude2": self.longitude2
            })

    def testMissingLongitude1(self):
        with self.assertRaises(MissingParameterException):
            Routing_machine(**{
                "distance": True,
                "latitude1": self.latitude1,
                "latitude2": self.latitude2,
                "longitude2": self.longitude2
            })

    def testMissingLatitude2(self):
        with self.assertRaises(MissingParameterException):
            Routing_machine(**{
                "distance": True,
                "latitude1": self.latitude1,
                "longitude1": self.longitude1,
                "longitude2": self.longitude2
            })

    def testMissingLongitude2(self):
        with self.assertRaises(MissingParameterException):
            Routing_machine(**{
                "distance": True,
                "latitude1": self.latitude1,
                "longitude1": self.longitude1,
                "latitude2": self.latitude2
            })

    def testInvalidLimit(self):
        with self.assertRaises(InvalidParameterException):
            Routing_machine(**{
                "distance": True,
                "latitude1": self.latitude1,
                "longitude1": self.longitude1,
                "latitude2": self.latitude2,
                "longitude2": self.longitude2,
                "alternatives": self.invalid_alternatives
            })

    def testInvalidLimit2(self):
        with self.assertRaises(InvalidParameterException):
            Routing_machine(**{
                "distance": True,
                "latitude1": self.latitude1,
                "longitude1": self.longitude1,
                "latitude2": self.latitude2,
                "longitude2": self.longitude2,
                "alternatives": self.invalid_alternatives2
            })

    def testInvalidLimit3(self):
        with self.assertRaises(InvalidParameterException):
            Routing_machine(**{
                "distance": True,
                "latitude1": self.latitude1,
                "longitude1": self.longitude1,
                "latitude2": self.latitude2,
                "longitude2": self.longitude2,
                "alternatives": self.invalid_alternatives3
            })


if __name__ == '__main__':
    unittest.main()