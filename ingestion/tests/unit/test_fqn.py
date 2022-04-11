from unittest import TestCase
from metadata.utils.fqn import *


class Fqn(TestCase):
    def test_split(self):
        fqn = "foo.bar"
        xs = split(fqn)
        expected_xs = ["foo", "bar"]
        self.assertEqual(xs, expected_xs)
        self.assertEqual(build(*xs), fqn)
