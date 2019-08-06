class SnowModel:

    def __init__(self):
        self.fw = 0
        self.lw = 0


    def split_precipitation(self, prec, temp, tx):
        if temp < tx:
            psolid, pliquid = prec, 0
        else:
            psolid, pliquid = 0, prec
        return psolid, pliquid


    def compute_potmelt(self, temp, cx, ts, step_in_days):
        if (temp - ts > 0):
            pot_melt = cx * step_in_days * (temp - ts)
        else:
            pot_melt = 0
        return pot_melt


    def compute_potrefreeze(self, temp, cx, cfr, ts, step_in_days):
        if temp - ts > 0:
            refreeze = 0
        else:
            refreeze = -cfr * cx * step_in_days * (temp - ts)
        return refreeze


    def limit_fluxes(self, flux_value, available_water):
        return min(available_water, flux_value)
        
    
    def update_states(self, psolid, pliquid, act_melt, act_refreeze, lwmax):
        self.fw += psolid + act_refreeze - act_melt
        self.lw += pliquid + act_melt - act_refreeze

        if (self.lw > self.fw * lwmax):
            outflow = self.lw - self.fw * lwmax
            self.lw = self.fw * lwmax
        else:
            outflow = 0.0

        return outflow


    def step(self, prec_mm_h, temp):
        pass



