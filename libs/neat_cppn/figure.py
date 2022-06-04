import os
import csv
import numpy as np
import pandas as pd

import matplotlib.pyplot as plt


def make_species(expt_path):

    history_file = os.path.join(expt_path, 'history_pop.csv')

    data = pd.read_csv(history_file)

    max_generation = data['generation'].max()
    generation_pop_size = dict(data['generation'].value_counts())

    species_data = {}
    for key in data['species'].unique():
        sp_data = data.query(f'species=={key}')

        created = sp_data['generation'].min()
        extinct = sp_data['generation'].max()+1

        first_genome_parent = sp_data['parent1'].iloc[0]
        if first_genome_parent==-1:
            ancestor = -1
        else:
            ancestor = data['species'].iloc[(data['id']==first_genome_parent).idxmax()]

        pop_history = dict(sp_data['generation'].value_counts())
        pop_history = np.array([pop_history.get(gen, 0)/generation_pop_size[gen] for gen in range(max_generation+1)])

        species_data[key] = {
            'created': created,
            'extinct': extinct,
            'ancestor': ancestor,
            'pop_history': pop_history,
        }


    order = []
    stack = [-1]
    while len(stack)>0:
        k = stack.pop(0)
        for key,species in species_data.items():
            if species['ancestor']==k:
                stack.insert(0, key)
        order.append(k)
    order = order[1:]


    fig, ax = plt.subplots()
    colors = plt.rcParams['axes.prop_cycle'].by_key()['color']


    base_y = {order[0]: 0}
    for i in range(len(order)):

        key = order[i]
        ancestor = species_data[key]['ancestor']
        created = species_data[key]['created']
        extinct = species_data[key]['extinct']
        gen = np.arange(created, extinct)
        pop = species_data[key]['pop_history']

        if i>0:
            base_y[key] = base_y[prev_key] + max(0.2, np.max(np.where((prev_pop>0) & (pop>0), prev_pop, 0))+0.1)

        upper = base_y[key] + pop[created:extinct]
        bottom = np.full(len(gen), base_y[key])

        ax.plot(gen, bottom, color=colors[i%10], alpha=0.8)
        ax.plot(gen, upper, color=colors[i%10], alpha=0.2)
        ax.fill_between(gen, bottom, upper, alpha=0.5, color=colors[i%10])

        if ancestor!=-1:
            ax.plot([created]*2, [base_y[ancestor], base_y[key]], color='k', ls=':')

        prev_key = key
        prev_created = created
        prev_extinct = extinct
        prev_pop = pop

    fig_height = base_y[prev_key] + np.max(prev_pop)+0.1

    fig.set_figheight(fig_height)
    fig.set_figwidth(max_generation/30)
    fig.set_figwidth(15)

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)

    ax.set_xlim([-max_generation*0.05, max_generation*1.05])
    ax.set_yticks([])

    ax.set_xlabel('generation')
    ax.set_ylabel('species')

    filename = os.path.join(expt_path, 'species.jpg')
    plt.savefig(filename, bbox_inches='tight')
    plt.close()
    # plt.show()
