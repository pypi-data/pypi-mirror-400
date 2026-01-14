from .nonrel_cloud import NonrelScalar, NonrelVector
from .rel_vec_cloud import RelVector
from .rel_sca_cloud import RelScalar
from .matched_waveform import MatchedWaveform 
from .full_evo_waveform import FullEvoWaveform 

class UltralightBoson(object):
    def __init__(self, spin=1, model="relativistic", nonrel_freq_shift=False):
        if (not (spin==0 or spin==1)):
            raise ValueError("Spin value %d not supported" % spin)
        if (model=="non-relativistic"):
            if (spin==0):
                self._cloud_model = NonrelScalar() 
            elif (spin==1):
                self._cloud_model = NonrelVector()
        elif (model=="relativistic"):
            if (spin==0):
                self._cloud_model = RelScalar(nonrel_freq_shift=nonrel_freq_shift)
            elif (spin==1):
                self._cloud_model = RelVector(nonrel_freq_shift=nonrel_freq_shift)
        else:
            raise ValueError("Model %s not supported" % model)
    def make_waveform(self, Mbh, abh, mu, units="physical", evo_type="matched"):
        if (evo_type=="matched"): 
            return MatchedWaveform(mu, Mbh, abh, self._cloud_model, units=units)
        elif (evo_type=="full"):
            return FullEvoWaveform(mu, Mbh, abh, self._cloud_model, units=units)
        else:
            raise ValueError("evo_type %s not supported" % evo_type)

