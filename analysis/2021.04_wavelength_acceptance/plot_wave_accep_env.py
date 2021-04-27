import numpy as np
import matplotlib.pyplot as plt


data_v3 = np.genfromtxt('acceptance_envelope_mismatch_{}.csv'.format('v3'), delimiter=',',
	skip_header=1, names=['wlen', 'envelope', 'ic', 'pdom'])
data_v3['wlen']/=1e-9

data_v31 = np.genfromtxt('acceptance_envelope_mismatch_{}.csv'.format('v3.2'), delimiter=',',
	skip_header=1, names=['wlen', 'envelope', 'ic', 'pdom'])
data_v31['wlen']/=1e-9

fig, ax = plt.subplots(1,2,figsize=(14,5))


ax[0].plot(data_v3['wlen'], data_v3['envelope'], 'o-', label='MakePhotonsMultiSensor Envelope')
ax[0].plot(data_v3['wlen'], data_v3['ic'], 'o-', label='MakePEFromPhotons IceCube')
ax[0].plot(data_v3['wlen'], data_v3['pdom'], 'o-', label='MakePEFromPhotons PDOM')
ax[0].set_title('V3 GCD')
ax[0].set_xlabel('Wavelength [nm]')
ax[0].set_ylabel('Acceptance')
ax[0].set_ylim([-0.01, 0.3])
ax[0].legend()
ax[0].grid()

ax[1].plot(data_v31['wlen'], data_v31['envelope'], 'o-', label='MakePhotonsMultiSensor Envelope')
ax[1].plot(data_v31['wlen'], data_v31['ic'], 'o-', label='MakePEFromPhotons IceCube')
ax[1].plot(data_v31['wlen'], data_v31['pdom'], 'o-', label='MakePEFromPhotons PDOM')
ax[1].set_title('V3.2 GCD')
ax[1].set_xlabel('Wavelength [nm]')
ax[1].set_ylabel('Acceptance')
ax[1].set_ylim([-0.01, 0.3])
ax[1].legend()
ax[1].grid()

plt.tight_layout()
fig.savefig('plot_mismatch.png', dpi=300)
