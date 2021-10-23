import matplotlib.pyplot as plt
import numpy as np
from numpy import genfromtxt

positions = np.genfromtxt("gel_atten.csv",delimiter=' ',skip_header=3,names=['wlen','abs'])

fig, ax = plt.subplots() # note we must use plt.subplots, not plt.subplot
ax.plot(positions['wlen'], positions['abs'])
fig.savefig('absorption.png')