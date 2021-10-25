

import argparse, sys
from I3Tray import I3Tray
from icecube import icetray, dataio, dataclasses, hdfwriter
from tools import perturb_strings

config_filename = 'uncertainties_1.pkl'

parser = argparse.ArgumentParser()
parser.add_argument("-i","--infile",type=str,help="Input GCD File",required=True,dest="infile")
parser.add_argument("-o","--outfile", type=str, help="Output GCD File", required=True, dest="outfile")
args = parser.parse_args()

tray = I3Tray()
tray.context['I3FileStager'] = dataio.get_stagers()

tray.Add("I3Reader","read", 
	FilenameList = [args.infile]
    )

tray.AddSegment(perturb_strings, 
	config_file=config_filename
    )

tray.Add("I3Writer","writer",
	filename = args.outfile,
	streams = list(map(icetray.I3Frame.Stream, "GCD")),
	)

tray.Execute()