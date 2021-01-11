import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-i","--infile",type=str,help="Input File",required=True,dest="infile")
parser.add_argument("-p","--out-prefix",type=str,help="Prefix for output files",required=True,dest="outprefix")
args = parser.parse_args()

from I3Tray import I3Tray
from icecube import icetray, dataio, dataclasses, hdfwriter, spline_reco

tray = I3Tray()
tray.Add("I3Reader", "read", FileNameList = [args.infile])

hdf_keys = [
	'I3EventHeader',
	'I3MCWeightDict',
	'NuGPrimary',
	'MostEnergeticMuon',
	'MCMuon',
	'MuonEffectiveArea',
	'LineFit',
	'SPEFitSingle',
	'SPEFit8',
	'MuEXAngular4',
	'HighNoiseMPE',
	'MPEFit4',
	'SplineMPE_default',
	'SplineMPEMuEXDifferential',
	'SplineMPE_recommended',
	'SplineMPE_recommendedFitParams'
]

sub_event_streams = ["IC86_SMT8", "GEN2"]
for ses in sub_event_streams:

	tray.AddSegment(hdfwriter.I3HDFWriter, 'hdf_{0}'.format(ses),
		Output=args.outprefix + ".{0}.hdf5".format(ses),
		CompressionLevel=9,
		Keys=hdf_keys,
		SubEventStreams=[ses]
		)

tray.Execute()


