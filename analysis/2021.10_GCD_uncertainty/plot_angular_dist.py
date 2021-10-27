import matplotlib.pyplot as plt
import tables
import pandas as pd
import numpy as np
from toolz import memoize
from gen2_analysis import plotting, surfaces
import matplotlib.colors as colors
import utils_plot


import photospline
from scipy import optimize
from autograd.misc.flatten import flatten_func
import autograd
import autograd.numpy as n
import os
import h5py

import argparse
parser = argparse.ArgumentParser() 
parser.add_argument("-n",type=str,help="geom name, e.g. hcr", required=False, dest='geom', default='standard')
parser.add_argument("-p",type=bool,help="make plots?", required=False, dest='do_plots', default=False)
args = parser.parse_args()
the_geom = args.geom
the_file = 'data_sunflower_{}.hdf5'.format(the_geom)
print("the file {}".format(the_file))

@memoize
def load_dataset(hdf_fname):
	dfs = {}
	# read each table into a DataFrame
	with tables.open_file(hdf_fname) as hdf:
		for tab in 'MCMuon', 'MuonEffectiveArea', 'SplineMPEMuEXDifferential', 'LineFit', 'SplineMPE_recommendedFitParams', 'SplineMPE_recommendedDirectHitsC':
			dfs[tab] = pd.DataFrame(hdf.get_node('/'+tab).read_where('exists==1')).set_index(['Run', 'Event', 'SubEvent', 'SubEventStream'])
	# apply event selection
	mask = (dfs['LineFit']['speed'] < 0.6)&\
		(dfs['SplineMPE_recommendedFitParams']['rlogl'] < 8.5)&\
		(dfs['SplineMPE_recommendedDirectHitsC']['n_dir_doms'] > 6)&\
		(dfs['SplineMPE_recommendedDirectHitsC']['dir_track_length'] > 120)
	# angular reconstruction error
	def cartesian_components(df):
		theta = df['zenith']
		phi = df['azimuth']
		return -np.sin(theta)*np.cos(phi), -np.sin(theta)*np.sin(phi), -np.cos(theta)
	def opening_angle(df1, df2):
		x1, y1, z1 = cartesian_components(df1)
		x2, y2, z2 = cartesian_components(df2)
		return np.arccos(x1*x2+y1*y2+z1*z2)
	# pack relevant quantities into a single DataFrame
	dats = pd.DataFrame(
		{
			'opening_angle':
				np.degrees(
					  opening_angle(
						  dfs['MCMuon'].loc[mask],
						  dfs['SplineMPEMuEXDifferential'].loc[mask]
					  )
				),
			'aeff':  dfs['MuonEffectiveArea']['value'].loc[mask],
			'energy': dfs['MCMuon']['energy'].loc[mask],
			'cos_zenith': np.cos(dfs['MCMuon']['zenith'].loc[mask]),
		}
	)
	return dats

cmap=plt.cm.viridis
sizer=15
kwargs = {'cmap': cmap, 
            'norm' : colors.LogNorm(), 
            'cmin': 1,
            # 'weights' : weights
            }


dats = load_dataset(the_file)

# just see what we're working with in terms of statistics
print(dats.describe())
# dats['energy']
# dats['cos_zenith']
# dats['opening_angle']


###################################
# energy distribution
###################################
bins_e = np.linspace(3,9,40)
fig = plt.figure(figsize=(4,4))
ax = fig.add_subplot(111)
ax.hist(np.log10(dats['energy']), bins=bins_e, alpha=0.5)
ax.set_xlabel(r'True Muon Energy log$_{10}$(GeV)')
ax.set_ylabel(r'Events')
ax.set_yscale('log')
# ax.set_title('{}'.format(dataset))
plt.tight_layout()
fig.savefig('plots/energy_dist.png', 
        edgecolor='none', bbox_inches='tight', dpi=300)
del fig, ax




###################################
# opening angle vs energy
###################################
fig = plt.figure(figsize=(7,7))    
ax = fig.add_subplot(111)
counts, xedges, yedges, im = ax.hist2d(
        np.log10(dats['energy']),
        dats['opening_angle'],
        bins=[bins_e, np.linspace(0,5,50)],
        **kwargs
        )
cbar = plt.colorbar(im, ax=ax)
x, y_med, y_lo, y_hi = utils_plot.find_contours_2D(
    x_values=np.log10(dats['energy']),
    y_values=dats['opening_angle'],
    xbins=xedges,
    c1=0, c2=68,
    )
ax.plot(x, y_med, 'r-', label='Median')
ax.plot(x, y_hi, 'r-.', label='68% contour')
cbar.set_label('Events', fontsize=sizer)
ax.set_ylabel(r'Spline MPE Opening Angle', fontsize=sizer)
ax.set_xlabel(r'Energy log$_{10}$(GeV)', fontsize=sizer)
ax.tick_params(labelsize=sizer)
ax.legend()

plt.tight_layout()
fig.savefig('plots/{}_opening_angle_vs_e_2d.png'.format(the_geom), 
        edgecolor='none', bbox_inches='tight', dpi=300)
# del fig, ax, ax2

np.savez('plots/{}_opening_angle_vs_e.pnz'.format(the_geom), 
	x=x, y_med=y_med, y_hi = y_hi)



