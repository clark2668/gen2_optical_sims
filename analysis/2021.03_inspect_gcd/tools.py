from icecube import icetray, dataclasses
import matplotlib.pyplot as plt
import numpy as np

def inspect_G_frame(frame, save_plot=False):
	geo = frame['I3Geometry'].omgeo

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
	om_depths -= z_surface

	print("Min depth {}".format(np.min(om_depths)))
	print("Max depth {}".format(np.max(om_depths)))

	if save_plot:

		# top down
		fig, axs = plt.subplots(1,1,figsize=(20,10))
		axs.plot(om_strings, om_depths, 'o', markersize=3)
		axs.set_xlabel('String Number')
		axs.set_ylabel('Depth')
		axs.grid()
		axs.set_ylim([-2800, -1200])
		plt.tight_layout()
		fig.savefig('om_map.png')

		del fig, axs

		fig, axs = plt.subplots(1,1,figsize=(10,10))
		axs.plot(om_x[:86], om_y[:86], 'o', markersize=4, label='IceCube')
		axs.plot(om_x[86:], om_y[86:], 's', markersize=4, label='Gen2')
		axs.set_xlabel('X [m]')
		axs.set_ylabel('Y [m]')
		axs.set_aspect('equal')
		axs.legend()
		axs.grid()
		# axs.set_ylim([-2800, -1200])
		plt.tight_layout()
		fig.savefig('top_down.png')

