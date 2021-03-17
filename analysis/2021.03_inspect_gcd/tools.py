from icecube import icetray, dataclasses
import matplotlib.pyplot as plt
import numpy as np

def inspect_G_frame(frame, save_plot=False):
	geo = frame['I3Geometry'].omgeo

	om_strings = []
	om_depths = []

	for omkey, omgeo in geo:
		if omgeo.position.z > 1000:
			continue
		om_strings.append(omkey.string)
		om_depths.append(omgeo.position.z)

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
		# np.savez('dom_loc.npz', om_strings=om_strings, om_depths=om_depths)	
		fig, axs = plt.subplots(1,1,figsize=(20,10))
		axs.plot(om_strings, om_depths, 'o', markersize=3)
		axs.set_xlabel('String Number')
		axs.set_ylabel('Depth')
		axs.grid()
		axs.set_ylim([-2800, -1200])
		plt.tight_layout()
		fig.savefig('om_map.png')

