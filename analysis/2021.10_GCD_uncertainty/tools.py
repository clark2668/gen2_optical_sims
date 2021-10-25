from icecube import icetray, dataclasses
import copy
import pickle
import os

class PerturbStrings(icetray.I3Module):
    '''
    A module to perturb the x-y positions of strings in the GCD file
    '''

    def __init__(self, context):
        icetray.I3Module.__init__(self, context)

        self.AddParameter('config_file',
            'Pickle File of perturbations',
            None)
        
        self.AddParameter('perturbations',
            'Dictionary of strings to perturbations',
            None)

    def Configure(self):

        self.config_file = self.GetParameter('config_file')
        if self.config_file is None:
            icetray.logging.log_fatal('No list of perturbations is specified')
        
        exists = os.path.exists(self.config_file)
        if not exists:
            icetray.logging.log_fatal('The specified configuration ({}) does not exist.'.format(self.config_file))

        uncertainties = {}
        with open(self.config_file, 'rb') as f:
            errors = pickle.load(f)
        if errors is not None:
            for i, err in errors.items():
                uncertainties[i+1001] = err

        self.perturbations = uncertainties
        icetray.logging.log_info('Perturbations: {}'.format(self.perturbations))

    def perturb(self, frame):
        if not 'I3Geometry' in frame:
            icetray.logging.log_fatal('There is no I3Geometry available. Abort!')
        geo = copy.copy(frame['I3Geometry']) # make a copy

        omgeo = geo.omgeo
        for omkey, g in omgeo:
            string = omkey[0]
            if string < 87:
                continue
            if string not in self.perturbations:
                icetray.logging.log_fatal('String {} is missing. Abort!'.format(string))
            dX = self.perturbations[string][0]
            dY = self.perturbations[string][1]
            # print("String {}, dX {}, dY {}".format(string, dX, dY))
            old_x = g.position.x
            old_y = g.position.y
            new_x = old_x + dX
            new_y = old_y + dY
            g.position.x = new_x
            g.position.y = new_y
            # print('Old {:.2f}, {:.2f}, New {:.2f}, {:.2f}'.format(old_x, old_y, g.position.x, g.position.y))

        del frame['I3Geometry'] # remove the old I3Geometry out of the frame
        frame['I3Geometry'] = geo # put the new one in place
        del geo # be *very* safe -- don't hold onto geo after adding it to the frame

    def Geometry(self, frame):
        self.perturb(frame)
        self.PushFrame(frame)


@icetray.traysegment
def perturb_strings(tray, name, config_file='uncertainties_1.pkl'):

    tray.Add(PerturbStrings, config_file=config_file)