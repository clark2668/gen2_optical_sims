import h5py
import argparse
import numpy as np
import numpy
import matplotlib.pyplot as plt
import matplotlib.colors as colors


# options = ['240', 'sigma1', 'sigma2', 'sigma3']
options = ['240', '1', '2', '3']
colors = ['C0', 'C1', 'C2', 'C3']
sizer=15


fig = plt.figure(figsize=(7,7))    
ax = fig.add_subplot(111)

for i, opt in enumerate(options):

	label = None
	if opt is '240':
		label = 'Median, Perfect Geo'
		filename = 'plots/{}_opening_angle_vs_e.pnz.npz'.format(opt)
	else:
		label = r'Median, $\sigma$={}'.format(opt)
		filename = 'plots/sigma{}_opening_angle_vs_e.pnz.npz'.format(opt)
	
	file = np.load(filename)

	x = file['x']
	y_med = file['y_med']
	y_hi = file['y_hi']

	ax.plot(x, y_med, color=colors[i], linestyle='-', label=label)
	ax.plot(x, y_hi, color=colors[i], linestyle='-.', label='68% contour')

ax.set_ylabel(r'All-Sky Averaged Spline MPE Opening Angle', fontsize=sizer)
ax.set_xlabel(r'True Muon Energy log$_{10}$(GeV)', fontsize=sizer)
ax.tick_params(labelsize=sizer)
ax.set_ylim([0,1.2])
ax.legend()
plt.tight_layout()
fig.savefig('plots/comparison.png', 
        edgecolor='none', bbox_inches='tight', dpi=300)