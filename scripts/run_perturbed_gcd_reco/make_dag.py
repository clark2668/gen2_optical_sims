# requires python 3! (sorry, I like f-strings...)

design = 'Sunflower_240m'
dataset = 11900
mod='sigma3'

source_dir = "/data/wipac/HEE/simulation/level2/no-domsim/"
output_dir = "/data/user/brianclark/Gen2_optical/gcd_errors/recos/{}".format(mod)
gcd_file = "/data/user/brianclark/Gen2_optical/gcd_errors/gcds/gcd_{}.i3.bz2".format(mod)

dag_file_name = 'dagman_reco_'+mod+'.dag'
instructions = ""
instructions += 'CONFIG config.dagman\n\n'

with open(dag_file_name, 'w') as f:
	f.write(instructions)

for i in range(1000):

	instructions = ""
	instructions += f'JOB job_{i} job.sub \n'
	instructions += f'VARS job_{i} gcdfile="{gcd_file}" indir="{source_dir}" outdir="{output_dir}" design="{design}" dataset="{dataset}" part="{i:06}" mod="{mod}"\n\n'

	with open(dag_file_name, 'a') as f:
		f.write(instructions)
