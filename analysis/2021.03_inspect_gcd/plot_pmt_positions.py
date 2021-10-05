import numpy as np
import matplotlib
from matplotlib import pyplot as plt

version = 'v3.2'

pos = np.genfromtxt("mdom_positions_{}.csv".format(version), names=True)
ori = np.genfromtxt("mdom_orientations_{}.csv".format(version), names=True)

_, i = np.unique(pos['z'], return_index=True)
pos = pos[i]
ori = ori[i]

pmt_radius = 0.051

if version=='v3.2':
    mod_radius = 0.178
    glass_thickness = 0.014
if version=='v3.2.2':
    mod_radius = 0.190
    glass_thickness = 0.014


def get(pos, orientation, r=pmt_radius):
    # find the perpendicular to the orientation
    x, y, z = pos['x'], pos['y'], pos['z']
    
    radius = np.sqrt(x**2+y**2)
    zen = np.radians(orientation['theta']+90)
    
    dx = np.array([-np.sin(zen), np.sin(zen)]) * r
    dz = np.array([-np.cos(zen), np.cos(zen)]) * r
    
    return (-radius-dx, z+dz), (radius+dx, z+dz)


fig, ax = plt.subplots(figsize=(5,5))

module = plt.Circle((0, 0), mod_radius, color='cyan', )
glass = plt.Circle((0, 0), mod_radius-glass_thickness, color='w')

ax.add_patch(module)
ax.add_patch(glass)

for i in range(len(pos)):
    left, right = get(pos[i], ori[i])
    ax.plot(*left,
            linewidth=2,
            color='k')
    ax.plot(*right,
            linewidth=2,
            color='k')


ax.set_xlim([-0.3, 0.3])
ax.set_ylim([-0.3, 0.3])
# ax.set_xlim(-1.5*mod_radius, 1.5*mod_radius)
# ax.set_ylim(-1.5*mod_radius, 1.5*mod_radius)

ax.grid(alpha=0.25)
ax.set_aspect('equal')
ax.set_xlabel("X (m)", fontsize=14)
ax.set_ylabel("Z (m)", fontsize=14)
ax.set_title("{}".format(version))
plt.tight_layout()
fig.savefig('mdom_{}.png'.format(version), dpi=300)