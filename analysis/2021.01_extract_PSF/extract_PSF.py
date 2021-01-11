import matplotlib.pyplot as plt
import tables
import pandas as pd
import numpy as np
from toolz import memoize
from gen2_analysis import plotting

import photospline
from scipy import optimize
from autograd.misc.flatten import flatten_func
import autograd
import autograd.numpy as n
import os
import h5py

# f = h5py.File('redo_000000.GEN2.hdf5', 'r')
# print(f.keys())

@memoize
def load_dataset(hdf_fname):
	dfs = {}
	# read each table into a DataFrame
	with tables.open_file(hdf_fname) as hdf:
		for tab in 'MCMuon', 'MuonEffectiveArea', 'SplineMPEMuEXDifferential', 'LineFit', 'SplineMPE_recommendedFitParams', 'SplineMPE_recommendedDirectHitsC':
			dfs[tab] = pd.DataFrame(hdf.get_node('/'+tab).read_where('exists==1')).set_index(['Run', 'Event', 'SubEvent', 'SubEventStream'])
	# apply event selection
	mask = (dfs['LineFit']['speed'] < 0.6)&\
		(dfs['SplineMPE_recommendedFitParams']['rlogl'] < 8.5)&\
		(dfs['SplineMPE_recommendedDirectHitsC']['n_dir_doms'] > 6)&\
		(dfs['SplineMPE_recommendedDirectHitsC']['dir_track_length'] > 120)
	# angular reconstruction error
	def cartesian_components(df):
		theta = df['zenith']
		phi = df['azimuth']
		return -np.sin(theta)*np.cos(phi), -np.sin(theta)*np.sin(phi), -np.cos(theta)
	def opening_angle(df1, df2):
		x1, y1, z1 = cartesian_components(df1)
		x2, y2, z2 = cartesian_components(df2)
		return np.arccos(x1*x2+y1*y2+z1*z2)
	# pack relevant quantities into a single DataFrame
	dats = pd.DataFrame(
		{
			'opening_angle':
				np.degrees(
					  opening_angle(
						  dfs['MCMuon'].loc[mask],
						  dfs['SplineMPEMuEXDifferential'].loc[mask]
					  )
				),
			'aeff':  dfs['MuonEffectiveArea']['value'].loc[mask],
			'energy': dfs['MCMuon']['energy'].loc[mask],
			'cos_zenith': np.cos(dfs['MCMuon']['zenith'].loc[mask]),
		}
	)
	return dats


dats = load_dataset('save_all_orig_reco.GEN2.hdf5')

# just see what we're working with in terms of statistics
print(dats.describe())

# to paramterize PSF, need 3D histogram in log10(energy), cos(zenith), and angular error
bins = [np.linspace(3, 8, 21), np.linspace(-1, 1, 41), np.linspace(0, 90**(1./2), 101)**2]
counts = np.histogramdd(np.vstack((np.log10(dats['energy']), dats['cos_zenith'], dats['opening_angle'])).T, bins=bins)[0]

fig, ax = plt.subplots(1,1, figsize=(8,5))

# plot some slices
ei = 5
for ci in (0, 10, 15, 30, 39):
	y = counts[ei,ci,:].cumsum()
	ax.plot(*plotting.stepped_path(bins[2], y/y[-1]), label='({:.2f}, {:.2f}]'.format(*bins[1][ci:ci+2]))
	ax.set_xlim([0,4])
	ax.set_xlabel(r'Angular error $\Psi_{\max}$ (degree)')
	ax.set_ylabel(r'$P(\Psi < \Psi_{\max})$')
	ax.legend(title=r'$\cos(\theta_{\rm zenith})$')
	ax.set_title(
		r'$E_{{\mu}} \in \rm [{}, {})$'.format(
			*([plotting.format_energy(r"{%.1f \,}", e) for e in 10**bins[0][ei:ei+2]])
		)
	)
fig.savefig('angular error.png')
plt.close(fig)
del fig, ax

def slicemultiply(A,B,p):
	sa = A.shape
	sb = B.shape

	newaxes = list(range(p,B.ndim)) + list(range(0,p))

	B = B.transpose(newaxes)
	# use of autograd numpy wrappers to propagate gradients through this operation
	nonp = n.prod([B.shape[i] for i in range(1,B.ndim)])
	B = n.reshape(B,(B.shape[0],nonp))

	C = n.dot(A.transpose(), B)
	C = n.reshape(C,[A.shape[1]] + [sb[i] for i in newaxes[1:]])

	# Now invert the permutation we did to B on C
	invaxes = newaxes[:]
	for i in range(0,len(newaxes)): invaxes[newaxes[i]] = i
	C = C.transpose(invaxes)

	return C

def splinebasis(coords, knots, order):
	bspline = np.vectorize(photospline.bspline, excluded=(0, 3))
	nsplines = [len(knots[i])-order[i]-1 for i in range(len(knots))]
	return [bspline(knots[i], np.asarray(coords[i])[None,:], np.arange(nsplines[i])[:,None], order[i]) for i in range(len(knots))]

def grideval(basis, coefficients):
	result = coefficients
	for i in range(result.ndim):
		result = slicemultiply(basis[i], result, i)
	return result

def make_penalty(penorder, knots, order):
	"""
	Construct a weighted sum of N-th order penalty matrix for spline coefficients
	"""
	def divdiff(knots, order, m, i):
		# Calculate divided difference coefficients
		# in order to estimate derivatives.

		if m == 0:
			return np.asarray([1.])

		num = np.append(0,divdiff(knots,order,m-1,i+1)) - np.append(divdiff(knots,order,m-1,i),0)
		dem = (knots[i+order+1] - knots[i+m])/(order-(m-1))
		return num/dem

	def penalty_matrix(penorder, knots, splineorder):
		nspl = len(knots)-splineorder-1
		D = np.zeros((nspl,nspl),dtype=float)
		for i in range(0, nspl-penorder):
			D[i][i:i+penorder+1] = divdiff(knots,splineorder,penorder,i)

		return D

	def calcP(nsplines, knots, dim, order, porders):
		nspl = nsplines[dim]
		knots = knots[dim]

		D = np.zeros((nspl,nspl))
		for porder,coeff in porders.items():
			if coeff == 0: continue
			D1 = penalty_matrix(porder, knots, order)
			D += np.sqrt(coeff)*D1

		def prodterm(i):
			if (i == dim):
				return D
			else:
				return np.eye(nsplines[i],dtype=float)

		a = prodterm(0)
		i = 1
		while i < len(nsplines):
			b = prodterm(i)
			a = np.kron(a,b)
			i = i+1
		return a
	ndim = len(knots)
	nsplines = [len(knots[i])-order[i]-1 for i in range(ndim)]
	penalty = calcP(nsplines,knots,0,order[0],penorder[0])
	for i in range(1,ndim):
		penalty = penalty + calcP(nsplines,knots,i,order[i],penorder[i])
	return np.asarray(penalty)

def king_cdf(x, sigma, gamma):
	"""
	Cumulative version of the King function, used to parameterize the PSF in XMM and Fermi
	
	See: http://fermi.gsfc.nasa.gov/ssc/data/analysis/documentation/Cicerone/Cicerone_LAT_IRFs/IRF_PSF.html
	"""
	s2 = sigma**2
	x2 = x**2
	return (1.-1./gamma)/(2*(gamma-1.)*s2)*(2*gamma*s2 - (2*gamma*s2 + x2)*(x2/(2*gamma*s2) + 1)**-gamma)

def fit_psf(bins, counts, nknots=(7,10), smooth=1e1):
	"""
	Find splines that describe a tabulated point spread function    
	"""

	def pad_knots(knots, order=2):
		"""
		Pad knots out for full support at the boundaries
		"""
		pre = knots[0] - (knots[1]-knots[0])*np.arange(order, 0, -1)
		post = knots[-1] + (knots[-1]-knots[-2])*np.arange(1, order+1)
		return np.concatenate((pre, knots, post))

	order = [2,2]
	knots = [pad_knots(np.linspace(bins[i][0], bins[i][-1], nknots[i]), order[i]) for i in range(2)]
	centers = [(e[1:]+e[:-1])/2 for e in bins]
	basis = splinebasis(centers, knots, order)
	
	def cdf(x, sigma, gamma):
		s2 = sigma**2
		x2 = x**2
		return (1.-1./gamma)/(2*(gamma-1.)*s2)*(2*gamma*s2 - (2*gamma*s2 + x2)*(x2/(2*gamma*s2) + 1)**-gamma)
	
	def model(args, edges, N):
		sigma, gamma = args
		
		sigma = 10.**sigma[...,None]
		gamma = (10.**gamma[...,None]) + 1.
		return N[...,None]*(king_cdf(edges[1:][None,None,...], sigma, gamma) - king_cdf(edges[:-1][None,None,...], sigma, gamma))
	
	penalties = [make_penalty(p,knots,order) for p in [({2:10*smooth}, {2:smooth/50},), ({2:smooth}, {2:smooth},) ]]
	
	def penalty_term(coefficients):
		return n.sum(((n.dot(p, c.flatten())**2).sum() for p,c in zip(penalties, coefficients)))
	
	# total number of events in each energy/zenith bin
	N = counts.sum(axis=2)
	
	def llh(coefficients):
		args = [grideval(basis, c) for c in coefficients]
		# add a tiny term to prevent the expectation from being identically zero
		lam = model(args, bins[2], N) + np.finfo(float).tiny
		ts = -2*(counts*n.log(lam) - lam) #- gammaln(x+1))
		return n.sum(ts) + penalty_term(coefficients)
	
	coefficients = [np.zeros([b.shape[0] for b in basis])]*2

	flat_llh, unflatten, coefficients = flatten_func(llh, coefficients)
	
	def callback(xk):
		if callback.i % 100 == 0:
			print callback.i, flat_llh(xk)
		callback.i += 1
	callback.i = 0
	args, fval, res = optimize.fmin_l_bfgs_b(flat_llh, coefficients, autograd.elementwise_grad(flat_llh), factr=1e7, callback=callback)

	coefficients = unflatten(args)
	return [
		{
			'coefficients': c,
			'order': order,
			'knots': knots
		}
		for c in coefficients
	]

print("About to fit PSFs")
splines = fit_psf(bins, counts, smooth=1)

# and now make plots
x = np.linspace(-1, 1, 101)
fig, axes = plt.subplots(2,1, sharex=True)
for i in range(2):
	spl = splines[i]
	for loge in 3, 4, 5, 6:
		basis = splinebasis([[loge], x], spl['knots'], spl['order'])
		axes.flat[i].plot(x, grideval(basis, spl['coefficients']).T, label='$10^{{{:.0f}}}$'.format(loge))
axes.flat[1].set_xlabel(r'$\cos\theta_{\rm zenith}$')
axes.flat[1].set_ylabel(r'$\log_{10}(\gamma-1)$')
axes.flat[0].set_ylabel(r'$\log_{10}\sigma$')
axes.flat[0].legend(title=r'$E_{\mu}$ (GeV)', ncol=2)
fig.savefig('fit_params.png')
plt.close(fig)
del fig, axes

# evaluate the parameterized CDF
centers = [(e[1:]+e[:-1])/2 for e in bins[:-1]]
sigma, gamma_m1 = [grideval(splinebasis(centers, spl['knots'], spl['order']), spl['coefficients']) for spl in splines]
psi = np.linspace(0, 10, 101)
psf_vals = king_cdf(psi[None,...], 10**sigma[...,None], 10**(gamma_m1[...,None])+1)

fig, ax = plt.subplots(1,1, figsize=(8,5))
# compare the evaluated CDF to the source histogram
ei = 5
for ci in (0, 10, 20, 30, 39):
	y = counts[ei,ci,:].cumsum()
	line = ax.plot(*plotting.stepped_path(bins[2], y/y[-1]), label='({:.2f}, {:.2f}]'.format(*bins[1][ci:ci+2]))[0]
	ax.plot(psi, psf_vals[ei,ci], color=line.get_color())
	ax.set_xlim([0,4])
	ax.set_xlabel(r'Angular error $\Psi_{\max}$ (degree)')
	ax.set_ylabel(r'$P(\Psi < \Psi_{\max})$')
	ax.legend(title=r'$\cos(\theta_{\rm zenith})$')
	ax.set_title(
		r'$E_{{\mu}} \in \rm [{}, {})$'.format(
			*([plotting.format_energy(r"{%.1f \,}", e) for e in 10**bins[0][ei:ei+2]])
		)
	)
fig.savefig('angular_error_with_fits.png')
plt.close(fig)
del fig, ax

# write to fit file
def to_splinetable(spline_spec):
	# construct an empty SplineTable, the bad way
	data, weights = photospline.ndsparse.from_data(np.eye(2), weights=np.eye(2))
	template = photospline.glam_fit(data, weights, [[0,1],[0,1]], spline_spec['knots'], spline_spec['order'], [1e6]*2, [0]*2)
	# now, abuse the array protocol to get a writable view into the coefficient array
	class transplant(object):
		def __init__(self, donor):
			self.__array_interface__ = dict(donor.__array_interface__)
			self.__array_interface__['data'] = (self.__array_interface__['data'][0], False)
	np.array(transplant(template.coefficients), copy=False)[:] = spline_spec['coefficients']
	return template

print("Writing fits to file...")
from gen2_analysis.angular_resolution import SplineKingPointSpreadFunction
for label, spl in zip(('sigma', 'gamma'), splines):
	to_splinetable(spl).write('kingpsf.{}.fits'.format(label))
psf = SplineKingPointSpreadFunction(os.getcwd()+'/kingpsf')

# finally, check the difference between what we saved and what we loaded
# through the gen2 framework
fig, ax = plt.subplots(1,1, figsize=(8,5))
ei = 5
for ci in (0, 10, 20, 30, 39):
	y = counts[ei,ci,:].cumsum()
	from_fit = psf_vals[ei,ci]
	from_function = psf(np.radians(psi), 10**centers[0][ei], centers[1][ci])
	ax.plot(psi, from_fit-from_function, label='({:.2f}, {:.2f}]'.format(*bins[1][ci:ci+2]))
	ax.set_xlim(0,4)
	ax.set_xlabel(r'Angular error $\Psi_{\max}$ (degree)')
	ax.set_ylabel(r'difference (fit-functor)')
	ax.legend(title=r'$\cos(\theta_{\rm zenith})$')
	ax.set_title(
	r'$E_{{\mu}} \in \rm [{}, {})$'.format(
		*([plotting.format_energy(r"{%.1f \,}", e) for e in 10**bins[0][ei:ei+2]])
	)
)
fig.savefig('compare_orig_to_framework.png')
	