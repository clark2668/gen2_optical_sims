import numpy as np
import matplotlib.pyplot as plt

from icecube import icetray, dataclasses, clsim, photonics_service, simclasses
from icecube.dataclasses import I3OMGeo
import icecube.gen2_sim.segments.clsim as gen2_clsim
from icecube.mDOM_WOM_simulation.traysegments import degg

domRadius=0.16510*icetray.I3Units.m
mDOM_radius = 0.1780 * icetray.I3Units.m #FIXME is this correct

acc_icecube = clsim.GetIceCubeDOMAcceptance(domRadius=0.16510*icetray.I3Units.m,
	efficiency=1.)
acc_icecube_hqe = clsim.GetIceCubeDOMAcceptance(domRadius=0.16510*icetray.I3Units.m,
	efficiency=1., highQE=True)
acc_mdom = gen2_clsim.construct_mDOM_wavelength_acceptance()
acc_degg = degg.GetDEggAcceptance()

# sensors = [I3OMGeo.OMType.IceCube, I3OMGeo.OMType.PDOM, I3OMGeo.OMType.mDOM, I3OMGeo.OMType.DEgg]
sensors = [I3OMGeo.OMType.mDOM]
acc_envelope = gen2_clsim.GetWavelengthAcceptanceEnvelope(sensors, 1., 2.2)

acc_envelope_icecube = gen2_clsim.construct_supremum([acc_icecube, acc_icecube_hqe], [1,1])

steplen = acc_icecube.GetWavelengthStepping()
minwlen = acc_icecube.GetMinWlen()
maxwlen = acc_icecube.GetMaxWlen()
wlen = np.arange(minwlen, maxwlen+steplen, steplen)

values_icecube = []
values_icecube_hqe = []C
values_mdom = []
values_degg = []
envelope = []
envelope_icecube = []
for w in wlen:
	values_icecube.append(acc_icecube.GetValue(w))
	values_icecube_hqe.append(acc_icecube_hqe.GetValue(w))
	values_mdom.append(acc_mdom.GetValue(w))
	values_degg.append(acc_degg.GetValue(w))
	envelope.append(acc_envelope.GetValue(w))
	envelope_icecube.append(acc_envelope_icecube.GetValue(w))

wlen/=1e-9

# make plots

fig, ax = plt.subplots(1,1,figsize=(7,5))
thewidth=2
# ax.plot(wlen, values_icecube, label='IceCube', linewidth=thewidth)
# ax.plot(wlen, values_icecube_hqe, label='PDOM = IceCube HQE', linewidth=thewidth)
# ax.plot(wlen, values_mdom, label='mDOM', linewidth=thewidth)
# ax.plot(wlen, values_degg, label='D-Egg', linewidth=thewidth)
ax.plot(wlen, envelope, 'k', label='Envelope')
# ax.plot(wlen, envelope_icecube, 'k--', label='Envelope')
# ax.set_title('V3 GCD')
ax.set_xlabel('Wavelength [nm]')
ax.set_ylabel(r'Acceptance [m$^2$]')
ax.set_ylim([-0.01, 0.6])
ax.legend()
ax.grid()
plt.tight_layout()
fig.savefig('envelopes.png', dpi=300)
