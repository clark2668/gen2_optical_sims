import matplotlib.pyplot as plt
import numpy as np
from numpy import genfromtxt

positions = np.genfromtxt("positions.csv",delimiter=' ',skip_header=1,names=['pmt','x','y','z'])
print(positions['x'])

fig, ax = plt.subplots() # note we must use plt.subplots, not plt.subplot
for i in range(24):
	circ = plt.Circle((positions['x'][i], positions['z'][i]), 0.051, fill=False)
	ax.add_patch(circ)
circ = plt.Circle((0,0), 0.178, fill=False, color='C2')
ax.add_patch(circ)
circ = plt.Circle((0,0), 0.167, fill=False, color='C2')
ax.add_patch(circ)
ax.set_xlim([-0.5, 0.5])
ax.set_ylim([-0.5, 0.5])
ax.set_aspect('equal')
fig.savefig('plot.png')