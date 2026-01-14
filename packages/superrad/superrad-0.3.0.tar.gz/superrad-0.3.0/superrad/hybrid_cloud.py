from .cloud_model import CloudModel 

class HybridCloudModel(CloudModel):
    """
    Hybridize two cloud models.  Cloud_model_1 is used when valid based on
    azimuthal number, otherwise cloud_model_2 is used.
    """
    def __init__(self, cloud_model_1, cloud_model_2):
        self._cloud_model_1 = cloud_model_1
        self._cloud_model_2 = cloud_model_2
        if (self._cloud_model_1.boson_spin()!=
            self._cloud_model_2.boson_spin()):
            raise ValueError("Boson spins do not match")
    def boson_spin(self):
        return self._cloud_model_1.boson_spin() 
    def max_azi_num(self):
        return max(self._cloud_model_1.max_azi_num(),self._cloud_model_2.max_azi_num()) 
    def max_spin(self):
        #Not currently switching on BH spin
        return min(self._cloud_model_1.max_spin(),self._cloud_model_2.max_spin())
    def omega_real(self, m, alpha, abh, Mcloud):
        if (m<=self._cloud_model_1.max_azi_num()):
            return self._cloud_model_1.omega_real(m, alpha, abh, Mcloud)
        else:
            return self._cloud_model_2.omega_real(m, alpha, abh, Mcloud)
    def domegar_dmc(self, m, alpha, abh, Mcloud):
        if (m<=self._cloud_model_1.max_azi_num()):
            return self._cloud_model_1.domegar_dmc(m, alpha, abh, Mcloud)
        else:
            return self._cloud_model_2.domegar_dmc(m, alpha, abh, Mcloud)
    def omega_imag(self, m, alpha, abh):
        if (m<=self._cloud_model_1.max_azi_num()):
            return self._cloud_model_1.omega_imag(m, alpha, abh)
        else:
            return self._cloud_model_2.omega_imag(m, alpha, abh)
    def power_gw(self, m, alpha, abh):
        if (m<=self._cloud_model_1.max_azi_num()):
            return self._cloud_model_1.power_gw(m, alpha, abh)
        else:
            return self._cloud_model_2.power_gw(m, alpha, abh)
    def strain_sph_harm(self, m, alpha, abh):
        if (m<=self._cloud_model_1.max_azi_num()):
            return self._cloud_model_1.strain_sph_harm(m, alpha, abh)
        else:
            return self._cloud_model_2.strain_sph_harm(m, alpha, abh)
