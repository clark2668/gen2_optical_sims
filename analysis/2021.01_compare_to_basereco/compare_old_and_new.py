import h5py
import matplotlib.pyplot as plt
import numpy as np

# f_org = h5py.File('./from_orig_reco/11900_MUONGUN_.000000_Sunflower_240m_recos.GEN2.hdf5', 'r')
f_org = h5py.File('rebook_000000_.GEN2.hdf5','r')
f_new = h5py.File('redo_00000_.GEN2.hdf5', 'r')


# reco_object = 'LineFit'
reco_object = 'SplineMPEMuEXDifferential'

reco_dict = {'zenith': 9, 'azimuth': 10}
reco_thing = 'azimuth'

print("Len org {} ".format(len(f_org[reco_object])))
print("Len new {} ".format(len(f_new[reco_object])))

original = []
new = []
diff = []

# loop over new
for ev in range(len(f_new[reco_object])):
	new_val = f_new[reco_object][ev][reco_dict[reco_thing]]
	org_val = f_org[reco_object][ev][reco_dict[reco_thing]]

	if not np.isnan(new_val) and not np.isnan(org_val):

		original.append(org_val)
		new.append(new_val)
		difference = org_val-new_val
		diff.append(difference)
		print(f'ev {ev}, {reco_object} - {reco_thing}: orig {org_val:.4f}, new {new_val:4f}, diff {difference:.4f}')

fig, axs = plt.subplots(1,2,figsize=(10,5))
fig.suptitle(f'{reco_object} -- {reco_thing}'.format(reco_object))

axs[0].plot(original, new, 'o', alpha=0.5)
axs[0].set_xlabel('Base Reco Azimuth [rad]')
axs[0].set_ylabel('New Azmuth [rad]')
axs[0].plot([0,2*np.pi],[0,2*np.pi],'--')

axs[1].hist(diff, bins=500, alpha=0.5)
axs[1].set_xlabel(r'$\Delta$ azimuth (original - new) [rad]')
axs[1].set_ylabel('Events')
axs[1].set_xlim([-0.2, 0.2])

plt.tight_layout(rect=[0, 0.03, 1, 0.95])
fig.savefig(f'compare_{reco_object}_{reco_thing}.png'.format(reco_object))



# ### try reading another way
# import tables
# import pandas as pd

# hdf_fname = '/data/wipac/HEE/simulation/level2/no-domsim/11900/Sunflower_240m/BaseReco/11900_MUONGUN_.000000_Sunflower_240m_recos.GEN2.hdf5'
# # hdf_fname = 'redo_00000_.GEN2.hdf5'

# dfs = {}
# with tables.open_file(hdf_fname) as hdf:
# 	for tab in 'LineFit', 'SplineMPEMuEXDifferential':
# 		dfs[tab] = pd.DataFrame(hdf.get_node('/'+tab).read_where('exists==1')).set_index(['Run', 'Event', 'SubEvent', 'SubEventStream'])