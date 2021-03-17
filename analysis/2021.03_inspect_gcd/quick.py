import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

fig, axs = plt.subplots(1,1,figsize=(20,10))
axs.plot([1,2], [1,2])
fig.savefig('om_map.png')
