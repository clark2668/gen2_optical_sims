from icecube import icetray, dataio, dataclasses, phys_services
from I3Tray import I3Tray
import tools

gen2path = '/data/wipac/HEE/geometries/Sunflower/'

import argparse
parser = argparse.ArgumentParser() 
parser.add_argument("-gcd",type=str,help="full path to gcd file", 
	required=False, dest='gcd', 
	default=gen2path+'IceCubeHEX_Sunflower_240m_v3_ExtendedDepthRange.GCD.i3.bz2')
args = parser.parse_args()

tray = I3Tray()
tray.AddModule("I3Reader", filename=args.gcd)

tray.AddModule(tools.inspect_G_frame, "inpsect_G",
	Streams=[icetray.I3Frame.Geometry]
	)

tray.Execute()