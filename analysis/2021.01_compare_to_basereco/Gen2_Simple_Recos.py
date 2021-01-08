#!/bin/sh /cvmfs/icecube.opensciencegrid.org/py2-v3.1.1/icetray-start
#METAPROJECT combo/V00-00-03

# (current STTools is needed to prevent a memory blowup)

import argparse
parser = argparse.ArgumentParser()
parser.add_argument("-g","--gcd-file",type=str,help="GCD-File",required=True,dest="gcd")
parser.add_argument("-p","--out-prefix",type=str,help="Prefix for output files",required=True,dest="outprefix")
parser.add_argument("-i","--infile",type=str,help="Input File",required=True,dest="infile")
parser.add_argument("-n","--fitprefix",type=str,default="",help="prefix for fit names")
parser.add_argument("--no-spline-mpe",dest="with_spline_mpe",action="store_false",default=True,help="don't run SplineMPE")
parser.add_argument("-m","--pulse-map",type=str,default="SRTCleanedInIcePulses",help="Name of pulse map from which to reconstruct.  Default is %(default)s", dest="pulse")

args = parser.parse_args()


##############CONFIGURATION STUFF###########################

PulsesForReco = args.pulse
sub_event_streams = ["IC86_SMT8", "GEN2"]

############################################################
from I3Tray import I3Tray
from icecube import icetray, dataio, dataclasses, hdfwriter

tray = I3Tray()
tray.context['I3FileStager'] = dataio.get_stagers()
tray.Add("I3Reader","read", FilenameList = [args.gcd] + [args.infile])

from segments.BaseReco import BaseReco

keys = tray.Add(BaseReco, PulsesForReco=PulsesForReco, SplineMPE=args.with_spline_mpe, FitPrefix=args.fitprefix)

hdf_keys = keys + [
    'I3EventHeader',
    'I3MCWeightDict',
    'NuGPrimary',
    'MostEnergeticMuon',
    'MCMuon',
]

for ses in sub_event_streams:

    tray.AddSegment(hdfwriter.I3HDFWriter, 'hdf_{0}'.format(ses),
        Output=args.outprefix + ".{0}.hdf5".format(ses),
        CompressionLevel=9,
        Keys=hdf_keys,
        SubEventStreams=[ses])

tray.Add("I3Writer","writer",
         filename = args.outprefix+".i3.bz2",
         streams = list(map(icetray.I3Frame.Stream, "SQP")),
        )
tray.Execute()
