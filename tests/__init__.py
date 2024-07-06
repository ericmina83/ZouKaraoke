import unittest

from ZouKaraoke.EventBus import EventBus


class TestEventBus(unittest.TestCase):

    def test_emit(self):

        eventBus = EventBus()

        addOne = lambda x: x + 1

        eventBus.register("add_one", addOne)

        self.assertEqual(eventBus.emit("add_one", 1), 2)
