import json
from tkinter import E
import numpy as np
import matplotlib.pyplot as plt

plt.ioff()


def load_population(path):
    with open(path, 'r') as f:
        population = json.load(f)
    return population

params = [
	(0.5, 0.005),
	(0.75, 0.01),
	(0.75,0.005),
	(1.0, 0.005),
	(1.0, 0.01),
]

alls = []
epochs = 101
for param in params:
	mut_prob = []

	fit = []
	print('mutation_level/prob_mut_' + str(param[0]) + '_gauss_sd_' + str(param[1]))
	for it in range(epochs):
		mut_prob.append([[], [], [], [], []])
		fit.append([])
		for run in range(1,31):
			try:
				folder = 'mutation_level/prob_mut_' + str(param[0]) + '_gauss_sd_' + str(param[1]) + '/5.0/0.5/run_' + str(run) + '/iteration_' + str(it) + '.json'
				pop = load_population(folder)

				mut_prob[it][0].append(np.average([x['mutation_prob'][0] for x in pop]))
				mut_prob[it][1].append(np.average([x['mutation_prob'][1] for x in pop]))
				mut_prob[it][2].append(np.average([x['mutation_prob'][2] for x in pop]))
				mut_prob[it][3].append(np.average([x['mutation_prob'][3] for x in pop]))
				mut_prob[it][4].append(np.average([x['mutation_prob'][4] for x in pop]))
				
				pop_fitness = np.average([x['fitness'] for x in pop])
				fit[it].append(pop_fitness)
			except:
				print('mutation_level/prob_mut_' + str(param[0]) + '_gauss_sd_' + str(param[1]) + '/5.0/0.5/run_' + str(run) + '/iteration_' + str(it) + '.json')
				pass

	print(len(mut_prob), len(fit))

	averages = [[], [], [], [], []]
	std = [[], [], [], [], []]
	for i in range(5):
		for it in range(len(mut_prob)):
			foo = np.average(mut_prob[it][i])
			averages[i].append(foo)
			#print(averages)
			foo = np.std(mut_prob[it][i])
			std[i].append(foo)
	fig = plt.figure()
	plt.plot([x for x in range(epochs)], averages[0], label = "start")
	plt.plot([x for x in range(epochs)], averages[1], label = "expr")
	plt.plot([x for x in range(epochs)], averages[2], label = "op")
	plt.plot([x for x in range(epochs)], averages[3], label = "preop")
	plt.plot([x for x in range(epochs)], averages[4], label = "var")
	plt.title(f"mut_prob {param[0]} mut gauss {param[1]}")
	plt.legend()	
	plt.savefig(f'{param}.png')
	plt.close(fig)
	#print(f"mut_prob: {param[0]} delta_prob: {param[1]} fit: {np.average(fit)}\n{averages}\n{std}\n")
	alls.append([param[0], param[1], np.average(fit), averages, std])
alls.sort(key= lambda x: x[2])
for config in alls:
	print(f"[{config[0]},{config[1]}] {config[2]} {config[3]} {config[4]}")


