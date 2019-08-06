from unittest import TestCase

from waterflows.snow import States, Inputs, Params, SnowModel

class TestSnowModel(TestCase):

    def test_split_precipitation(self):

        model = SnowModel(States(), Params(), Inputs(-5, 10))

        res = model.split_precipitation()
        self.assertTupleEqual(res, (10, 0))

        model = SnowModel(States(), Params(), Inputs(5 ,10))

        res = model.split_precipitation()
        self.assertTupleEqual(res, (0, 10))


    def test_compute_potmelt(self):

        model = SnowModel(States(), Params(), Inputs(10, 5))

        pot_melt = model.compute_potmelt()
        self.assertEqual(pot_melt, 50.0)

        model = SnowModel(States(), Params(), Inputs(-10, 5))

        pot_melt = model.compute_potmelt()
        self.assertEqual(pot_melt, 0.0)


    def test_compute_compute_potrefreeze(self):

        model = SnowModel(States(), Params(), Inputs(10, 5))

        pot_refreeze = model.compute_potrefreeze()
        self.assertAlmostEqual(pot_refreeze, 0.0, 5)

        model = SnowModel(States(), Params(), Inputs(-10, 5))

        pot_refreeze = model.compute_potrefreeze()
        self.assertAlmostEqual(pot_refreeze, 5.0, 5)


    def test_limit_fluxes(self):

        model = SnowModel(States(), Params(), Inputs(10, 5))

        act_flux = model.limit_fluxes(50, 100)
        self.assertAlmostEqual(act_flux, 50, 5)

        act_flux = model.limit_fluxes(50, 30)
        self.assertAlmostEqual(act_flux, 30, 5)


    def test_update_states(self):

        # Outflow = 0

        states = States()
        params = Params()
        inputs = Inputs(10, 5)
       
        states.fw, states.lw = 90.0, 5.0
        psolid, pliquid, act_melt, act_refreeze = 10.0, 5.0, 5.0, 5.0

        model = SnowModel(states, params, inputs)

        outflow = model.update_states(psolid, pliquid, act_melt, act_refreeze)

        self.assertAlmostEqual(model.states.fw, 100.0, 8)
        self.assertAlmostEqual(model.states.lw, 10.0, 8)
        self.assertAlmostEqual(outflow, 0.0, 8)

        # Outflow = 10

        states.fw, states.lw = 90.0, 15.0
        psolid, pliquid, act_melt, act_refreeze = 10.0, 5.0, 5.0, 5.0

        model = SnowModel(states, params, inputs)

        outflow = model.update_states(psolid, pliquid, act_melt, act_refreeze)

        self.assertAlmostEqual(model.states.fw, 100.0, 8)
        self.assertAlmostEqual(model.states.lw, 10.0, 8)
        self.assertAlmostEqual(outflow, 10.0, 8)



    def test_step(self):

        params = Params()

        prec, temp, fw, lw = 10, 10, 0, 0

        states = States(fw, lw)
        inputs = Inputs(temp, prec)

        model = SnowModel(states, params, inputs)

        total_water_before = prec + model.states.total_water()

        outflow = model.step()

        total_water_after = outflow + model.states.total_water()

        self.assertAlmostEqual(total_water_before, total_water_after, 8)



