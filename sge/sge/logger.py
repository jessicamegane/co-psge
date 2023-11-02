import numpy as np
from sge.parameters import params
import json
import os


def evolution_progress(generation, pop):
    fitness_samples = [i['fitness'] for i in pop]
    data = '%4d\t%.6e\t%.6e\t%.6e' % (generation, np.min(fitness_samples), np.nanmean(fitness_samples), np.nanstd(fitness_samples))
    if params['VERBOSE']:
        print(data)
    save_progress_to_file(data)
    if generation % params['SAVE_STEP'] == 0:
        save_step(generation, pop)

def save_progress_to_file(data):
    with open('%s/run_%d/progress_report.csv' % (params['EXPERIMENT_NAME'], params['RUN']), 'a') as f:
        f.write(data + '\n')


def save_step(generation, population):
    to_save = []
    for i in population:
        if params['ADAPTIVE_MUTATION']:
            to_save.append({"genotype": i['genotype'],"fitness": i['fitness'], "pcfg": i["pcfg"].tolist(), "mutation_prob": i["mutation_prob"]})
        else:
            to_save.append({"genotype": i['genotype'],"fitness": i['fitness'], "pcfg": i["pcfg"].tolist()})

    open('%s/run_%d/iteration_%d.json' % (params['EXPERIMENT_NAME'], params['RUN'], generation), 'a').write(json.dumps(to_save))


def save_parameters():
    params_lower = dict((k.lower(), v) for k, v in params.items())
    c = json.dumps(params_lower)
    open('%s/run_%d/parameters.json' % (params['EXPERIMENT_NAME'], params['RUN']), 'a').write(c)


def prepare_dumps():
    try:
        os.makedirs('%s/run_%d' % (params['EXPERIMENT_NAME'], params['RUN']))
    except FileExistsError as e:
        pass
    save_parameters()