import matplotlib.pyplot as plt
import tables
import pandas as pd
import numpy as np
from toolz import memoize
from gen2_analysis import plotting, surfaces

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
			'azimuth': dfs['MCMuon']['azimuth'].loc[mask]
		}
	)
	return dats


dats = load_dataset(the_file)

the_zeniths = dats['cos_zenith']
mask1 = the_zeniths>-0.1
mask2 = the_zeniths<0.1

the_azimuths = np.rad2deg(dats['azimuth'].to_numpy())
the_errors = dats['opening_angle'].to_numpy()
the_energies = np.log10(dats['energy'])
mask3 = the_energies > 5
mask = mask1 & mask2 & mask3

azimuths = np.linspace(0, 360, 31)
bins = np.digitize(the_azimuths[mask], azimuths)
rmss = np.zeros(30)
evts = np.zeros(30)
binned_errors = [ [] for i in range(30) ]
for azi, err, bin in zip(the_azimuths[mask], the_errors[mask], bins):
	rmss[bin-1] += err
	evts[bin-1] += 1
	binned_errors[bin-1].append(err)

binned_errors = np.asarray(binned_errors)
medians = np.zeros(30)
for i in range(30):
	medians[i] = np.median(binned_errors[i])
print(medians)

# for azi, counts, med in zip(azimuths[:-1], evts, medians ):
# 	print("Azi {}, Counts {}, Median {:.3f}".format(azi, counts, med))

# binned_errors = np.array(binned_errors)
# print(binned_errors)
# binned_errors = np.median(binned_errors, axis=0)
# print(binned_errors)

# for i, err in enumerate(rmss):
# 	rmss[i]/=evts[i]
# 	print(evts[i])

# print(len(rmss))
# print(len(azimuths))

fig, ax = plt.subplots(1,1, figsize=(8,5))
ax.plot(azimuths[:-1], medians, '-')
# ax.plot(azimuths[:-1], rmss, 'o')
ax.set_ylabel(r'Median Opening Angle')
ax.set_xlabel(r'Azimuth (deg)')
ax.set_title(r'$-0.1 < \cos(\theta) < 0.1$, $E_{\mu}>100$ TeV')
# # ax.hist(the_errors, bins=60,alpha=0.5)
# ax.hlines(0.3, 0, 350, linestyles='--')
ax.set_ylim([0.1,0.5])
fig.savefig('err_vs_azi_{}.png'.format(the_geom), dpi=200)
