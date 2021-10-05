from icecube import icetray, dataclasses
import matplotlib.pyplot as plt
from matplotlib import gridspec
import numpy as np

def inspect_G_frame(frame, save_plot=False,
	separate_plots=False,
	title_mod=None):
	geo = frame['I3Geometry'].omgeo
	cal = frame['I3Calibration']

	om_strings = []
	om_depths = []

	om_strings_topdown = []
	om_x = []
	om_y = []

	finished = []

	for omkey, omgeo in geo:
		if omgeo.position.z > 1000:
			continue
		om_strings.append(omkey.string)
		om_depths.append(omgeo.position.z)
		eff = -10
		if omkey in cal.dom_cal:
			eff = cal.dom_cal[omkey].relative_dom_eff
		# print('Omkey {}, type {}, loc {:.4}, eff {}'.format(omkey, 
		# 	omgeo.omtype, omgeo.position, eff))
		print('{}, {:.4f}'.format(omkey.om, 
			omgeo.position.z))

		if omkey.om ==1:
			if omkey.string not in finished:
				finished.append(omkey.string)
				om_x.append(omgeo.position.x)
				om_y.append(omgeo.position.y)

	om_strings = np.asarray(om_strings)
	om_depths = np.asarray(om_depths)

	mask = om_strings > 90
	om_strings[mask] -= 1000
	om_strings[mask] += 100

	z_surface = dataclasses.I3Constants.SurfaceElev - dataclasses.I3Constants.OriginElev
	print('Surface Depth {}'.format(z_surface))
	om_depths -= z_surface

	print("Min depth {}".format(np.min(om_depths)))
	print("Max depth {}".format(np.max(om_depths)))

	if save_plot and not separate_plots:

		# setup the axes
		fig = plt.figure(figsize=(30,10))
		gs = gridspec.GridSpec(1,2,width_ratios=[1,2])
		ax1 = plt.subplot(gs[1])
		ax0 = plt.subplot(gs[0])

		# top down
		ax0.plot(om_x[:86], om_y[:86], 'o', markersize=4, label='IceCube')
		ax0.plot(om_x[86:], om_y[86:], 's', markersize=4, label='Gen2')
		ax0.set_xlabel('X [m]', size=15)
		ax0.set_ylabel('Y [m]', size=15)
		ax0.set_aspect('equal')
		ax0.tick_params(axis='both', labelsize=15)
		ax0.legend(fontsize=15)
		ax0.set_title('Top Down View', fontsize=15)
		ax0.grid()

		# side view
		ax1.plot(om_strings[:5160], om_depths[:5160], 'o', markersize=3)
		ax1.plot(om_strings[5160:], om_depths[5160:], 's', markersize=3)
		ax1.set_xlabel('String Number', size=15)
		ax1.set_ylabel('Depth', size=15)
		ax1.set_xticklabels(labels=['', '0', '50', '1000', '1150', '1200'])
		ax1.tick_params(axis='both', labelsize=15)
		ax1.set_ylim([-2800, -1200])
		ax1.set_title('Side View', fontsize=15)
		ax1.grid()

		# save plot
		plt.tight_layout()
		fig.savefig('layout_{}.png'.format(title_mod), dpi=300)
	
	if save_plot and separate_plots:
		fig = plt.figure(figsize=(5,5))
		ax = fig.add_subplot(111)
		ax.plot(om_x[:86], om_y[:86], 'o', markersize=4, label='IceCube')
		ax.plot(om_x[86:], om_y[86:], 's', markersize=6, label='Gen2')
		ax.set_xlabel('X [m]', size=15)
		ax.set_ylabel('Y [m]', size=15)
		ax.set_aspect('equal')
		ax.tick_params(axis='both', labelsize=15)
		ax.legend(fontsize=12)
		ax.grid()
		plt.tight_layout()
		fig.savefig('layout_topdown_{}.png'.format(title_mod), dpi=300)

		del fig, ax

		fig = plt.figure(figsize=(10 ,5))
		ax = fig.add_subplot(111)
		ax.plot(om_strings[:5160], om_depths[:5160], 'o', markersize=1)
		ax.plot(om_strings[5160:], om_depths[5160:], 's', markersize=1)
		ax.set_xlabel('String Number', size=15)
		ax.set_ylabel('Depth', size=15)
		ax.set_xticklabels(labels=['', '0', '50', '1000', '1150', '1200'])
		ax.tick_params(axis='both', labelsize=15)
		ax.set_ylim([-2800, -1200])
		ax.grid()
		plt.tight_layout()
		fig.savefig('layout_side_{}.png'.format(title_mod), dpi=300)
