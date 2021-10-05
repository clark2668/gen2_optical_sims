import matplotlib.pyplot as plt
import numpy as np
from numpy import genfromtxt

positions = np.genfromtxt("gel_atten.csv",delimiter=' ',skip_header=3,names=['wlen','abs'])

fig, ax = plt.subplots(figsize=(7,5))
ax.plot(positions['wlen'], positions['abs'], linewidth=3)
ax.set_xlabel('Wavelength [nm]', fontsize=15)
ax.set_ylabel('Absorption Length [m]', fontsize=15)
ax.tick_params(axis='both', labelsize=15)
plt.tight_layout()
fig.savefig('absorption.png')