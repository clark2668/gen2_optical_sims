import numpy as np
import matplotlib
from matplotlib import pyplot as plt

pos = np.genfromtxt("mdom_positions.csv", names=True)
ori = np.genfromtxt("mdom_orientations.csv", names=True)

_, i = np.unique(pos['z'], return_index=True)
pos = pos[i]
ori = ori[i]

pmt_radius = 0.051
mod_radius = 0.178
glass_thickness = 0.014

def get(pos, orientation, r=pmt_radius):
    # find the perpendicular to the orientation
    x, y, z = pos['x'], pos['y'], pos['z']
    
    radius = np.sqrt(x**2+y**2)
    zen = np.radians(orientation['zendeg']+90)
    
    dx = np.array([-np.sin(zen), np.sin(zen)]) * r
    dz = np.array([-np.cos(zen), np.cos(zen)]) * r
    
    return (-radius-dx, z+dz), (radius+dx, z+dz)


fig, ax = plt.subplots(figsize=(10,10))

module = plt.Circle((0, 0), mod_radius, color='cyan', )
glass = plt.Circle((0, 0), mod_radius-glass_thickness, color='w')

ax.add_patch(module)
ax.add_patch(glass)

for i in range(len(pos)):
    left, right = get(pos[i], ori[i])
    ax.plot(*left,
            linewidth=4,
            color='k')
    ax.plot(*right,
            linewidth=4,
            color='k')


ax.set_xlim(-1.5*mod_radius, 1.5*mod_radius)
ax.set_ylim(-1.5*mod_radius, 1.5*mod_radius)

ax.grid(alpha=0.25)
ax.set_xlabel("X (m)", fontsize=14)
ax.set_ylabel("Z (m)", fontsize=14)
fig.savefig('mlarson.png')