import numpy as np

seed = 1000
from numpy.random import PCG64, SeedSequence
ss = SeedSequence(seed)
bit_generator = PCG64(ss)
rng = np.random.default_rng(bit_generator)

sigma = 3 # meters

uncertainties = {}
dRs = []
for i in range(10000):
    # dR = rng.normal(loc=0., scale=sigma)
    # dRs.append(dR**2)
    # dPhi = rng.uniform(0, 2*np.pi)
    # dPhis.append(dPhi)
    dx = rng.normal(loc=0., scale=sigma)
    dy = rng.normal(loc=0., scale=sigma)
    uncertainties[i] = [dx, dy]
    dRs.append(np.sqrt(dx**2 + dy**2))

import matplotlib.pyplot as plt
count, bins, ignored = plt.hist(dRs, 30, density=True)
# plt.plot(bins, 1/(sigma * np.sqrt(2 * np.pi)) * np.exp( - (bins - 0.)**2 / (2 * sigma**2) ),
    # linewidth=2, color='r')
plt.plot([sigma,sigma],[0,1])
plt.xlim([0,10])
plt.savefig('dist.png')

# import matplotlib.pyplot as plt
# count, bins, ignored = plt.hist(dPhis, 30, density=True)
# plt.savefig('dist.png')

import pickle
outfile = 'uncertainties_{}.pkl'.format(sigma)
with open(outfile, "wb") as fout:
    pickle.dump(uncertainties, fout, protocol=4)

