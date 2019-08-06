from unittest import TestCase

from waterflows.snow import SnowModel

class TestSnowModel(TestCase):

    def test_split_precipitation(self):

        model = SnowModel()

        res = model.split_precipitation(10.0, -5.0, 0.0)
        self.assertTupleEqual(res, (10, 0))

        res = model.split_precipitation(10.0, 5.0, 0.0)
        self.assertTupleEqual(res, (0, 10))

    def test_compute_potmelt(self):

        model = SnowModel()

        pot_melt = model.compute_potmelt(10.0, 5.0, 0.0, 1.0)
        self.assertEqual(pot_melt, 50.0)

        pot_melt = model.compute_potmelt(-10.0, 5.0, 0.0, 1.0)
        self.assertEqual(pot_melt, 0.0)

    def test_compute_compute_potrefreeze(self):

        model = SnowModel()

        pot_refreeze = model.compute_potrefreeze(10.0, 5.0, 0.1, 0.0, 1.0)
        self.assertAlmostEqual(pot_refreeze, 0.0, 5)

        pot_refreeze = model.compute_potrefreeze(-10.0, 5.0, 0.1, 0.0, 1.0)
        self.assertAlmostEqual(pot_refreeze, 5.0, 5)

    def test_limit_fluxes(self):

        model = SnowModel()

        act_flux = model.limit_fluxes(50, 100)
        self.assertAlmostEqual(act_flux, 50, 5)

        act_flux = model.limit_fluxes(50, 30)
        self.assertAlmostEqual(act_flux, 30, 5)


    def test_update_states(self):

        # Outflow = 0

        model = SnowModel()

        model.fw, model.lw = 90.0, 5.0
        psolid, pliquid, act_melt, act_refreeze = 10.0, 5.0, 5.0, 5.0
        lwmax = 0.1

        outflow = model.update_states(psolid, pliquid, act_melt, act_refreeze, lwmax)

        self.assertAlmostEqual(model.fw, 100.0, 8)
        self.assertAlmostEqual(model.lw, 10.0, 8)
        self.assertAlmostEqual(outflow, 0.0, 8)

        # Outflow = 10

        model.fw, model.lw = 90.0, 15.0
        psolid, pliquid, act_melt, act_refreeze = 10.0, 5.0, 5.0, 5.0
        lwmax = 0.1

        outflow = model.update_states(psolid, pliquid, act_melt, act_refreeze, lwmax)

        self.assertAlmostEqual(model.fw, 100.0, 8)
        self.assertAlmostEqual(model.lw, 10.0, 8)
        self.assertAlmostEqual(outflow, 10.0, 8)



