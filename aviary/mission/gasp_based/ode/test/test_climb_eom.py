import unittest
import os

import numpy as np
import openmdao.api as om
from openmdao.utils.assert_utils import (assert_check_partials,
                                         assert_near_equal)

from aviary.mission.gasp_based.ode.climb_eom import ClimbRates
from aviary.utils.test_utils.IO_test_util import assert_match_spec, skipIfMissingXDSM
from aviary.variable_info.variables import Dynamic


class ClimbTestCase(unittest.TestCase):
    """
    These tests compare the output of the climb EOM to the output from GASP. There are some discrepancies.
    These discrepancies were considered to be small enough, given that the difference in calculation methods between the two codes is significant.
    """

    def setUp(self):

        self.prob = om.Problem()
        self.prob.model.add_subsystem("group", ClimbRates(num_nodes=2), promotes=["*"])

        self.prob.model.set_input_defaults("TAS", np.array([459, 459]), units="kn")
        self.prob.model.set_input_defaults(
            Dynamic.Mission.THRUST_TOTAL, np.array([10473, 10473]), units="lbf"
        )
        self.prob.model.set_input_defaults(
            Dynamic.Mission.DRAG, np.array([9091.517, 9091.517]), units="lbf"
        )
        self.prob.model.set_input_defaults(
            Dynamic.Mission.MASS, np.array([171481, 171481]), units="lbm"
        )

        self.prob.setup(check=False, force_alloc_complex=True)

    def test_case1(self):

        tol = 1e-6
        self.prob.run_model()

        assert_near_equal(
            self.prob[Dynamic.Mission.ALTITUDE_RATE], np.array(
                [6.24116612, 6.24116612]), tol
        )  # note: values from GASP are: np.array([5.9667, 5.9667])
        assert_near_equal(
            self.prob[Dynamic.Mission.DISTANCE_RATE], np.array(
                [774.679584, 774.679584]), tol
            # note: these values are finite differenced and lose accuracy. Fd values are: np.array([799.489, 799.489])
        )
        assert_near_equal(
            self.prob["required_lift"],
            np.array([171475.43516703, 171475.43516703]),
            tol,
        )  # note: values from GASP are: np.array([170316.2, 170316.2])
        assert_near_equal(
            self.prob[Dynamic.Mission.FLIGHT_PATH_ANGLE], np.array(
                [0.00805627, 0.00805627]), tol
        )  # note: values from GASP are:np.array([.0076794487, .0076794487])

        partial_data = self.prob.check_partials(out_stream=None, method="cs")
        assert_check_partials(partial_data, atol=1e-12, rtol=1e-12)

    @skipIfMissingXDSM('climb_specs/eom.json')
    def test_climb_spec(self):

        subsystem = self.prob.model

        assert_match_spec(subsystem, "climb_specs/eom.json")


if __name__ == "__main__":
    unittest.main()
