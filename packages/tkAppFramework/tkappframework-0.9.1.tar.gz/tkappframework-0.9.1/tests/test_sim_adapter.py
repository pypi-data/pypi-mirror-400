"""
This module provides unit tests for the SimulatorAdapter class.
"""


# Standard
import unittest

# Local
from tkAppFramework.sim_adapter import SimulatorAdapter


class Test_SimulatorAdapter(unittest.TestCase):
    def test_init_set_get_simulator(self):
        # Here our dummy test simulator can be literaly anything. Here a float.
        test_sim = float(19.0)
        # Test __init__ and @property getter
        adapt = SimulatorAdapter(sim=test_sim, logger_name='test_simulator_adapter_logger')
        self.assertEqual(id(adapt.simulator), id(test_sim))
        # Test @property setter
        test_sim = float(99.0)
        adapt.simulator = test_sim
        self.assertEqual(id(adapt.simulator), id(test_sim))

    def test_run(self):
        adapt = SimulatorAdapter(logger_name='test_simulator_adapter_logger')
        self.assertRaises(NotImplementedError, adapt.run)

    def test_load_and_run(self):
        adapt = SimulatorAdapter(logger_name='test_simulator_adapter_logger')
        self.assertRaises(NotImplementedError, adapt.load_and_run)


if __name__ == '__main__':
    unittest.main()
