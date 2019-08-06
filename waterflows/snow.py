class States:

    def __init__(self, fw = 0, lw = 0):
        self.fw = fw
        self.lw = lw

    def total_water(self):
        return self.fw + self.lw

class Params:

    def __init__(self):
        self.tx = 0            # Precipitation phase threshold temperature
        self.cx = 5            # Degreeday factor
        self.ts = 0            # Melt onset threshold temperature
        self.cfr = 0.1         # Refreeze factor
        self.lwmax = 0.1       # Maximum waterholding capacity
        self.step_in_days = 1  # Time step length in days
        
class Inputs:

    def __init__(self, temp, prec):
        self.temp = temp
        self.prec = prec


class SnowModel:

    def __init__(self, states, params, inputs):
        self.states = states
        self.params = params
        self.inputs = inputs


    def split_precipitation(self):
        if self.inputs.temp < self.params.tx:
            psolid, pliquid = self.inputs.prec, 0
        else:
            psolid, pliquid = 0, self.inputs.prec
        return psolid, pliquid


    def compute_potmelt(self):
        if self.inputs.temp - self.params.ts > 0:
            pot_melt = self.params.cx * self.params.step_in_days * (self.inputs.temp - self.params.ts)
        else:
            pot_melt = 0
        return pot_melt


    def compute_potrefreeze(self):
        if self.inputs.temp - self.params.ts > 0:
            refreeze = 0
        else:
            refreeze = -self.params.cfr * self.params.cx * self.params.step_in_days * (self.inputs.temp - self.params.ts)
        return refreeze


    def limit_fluxes(self, flux_value, available_water):
        return min(available_water, flux_value)
        
    
    def update_states(self, psolid, pliquid, act_melt, act_refreeze):
        self.states.fw += psolid + act_refreeze - act_melt
        self.states.lw += pliquid + act_melt - act_refreeze

        if (self.states.lw > self.states.fw * self.params.lwmax):
            outflow = self.states.lw - self.states.fw * self.params.lwmax
            self.states.lw = self.states.fw * self.params.lwmax
        else:
            outflow = 0.0

        return outflow


    def step(self):
        
        pliquid, psolid = self.split_precipitation()

        melt = self.compute_potmelt()

        refreeze = self.compute_potrefreeze()

        melt = self.limit_fluxes(melt, self.states.fw)

        refreeze = self.limit_fluxes(refreeze, self.states.lw)
        
        outflow = self.update_states(psolid, pliquid, melt, refreeze)

        return outflow




