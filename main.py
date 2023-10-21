import copy
import time
import matplotlib.pyplot as plt
import numpy as np
import random

durata_sim = 100000000000
scheduling_data = []
scheduling_agv = []
# domanda prodotto 1 e 2
demand = [1,1,1,1,1,1,1,1,1,1]
orig_demand=tuple(demand)
# vettore che contiene i prodotti associati alle operazioni, 2 prodotti, 5 operazioni
prodotti_job = [[1,2,3],[4,5,6],[7,8],[9,10,11,12],[13,14,15],[16,17,18],[19,20,21],[22,23],[24,25,26,27],[28,29,30,31,32]]

tot_prodotti = 0
for prod in demand:
    tot_prodotti = prod + tot_prodotti

# vettore che contiene lo stato delle macchine, 0 se nulla, id prodotto se contiene un prodotto
stato_macchine = [0, 0, 0,0,0,0,0,0,0,0]
t_operazione = [0, 0, 0,0,0,0,0,0,0,0]
n_macchine = len(stato_macchine)

ordine_macchine=list(range(len(stato_macchine)))

# matrice macchina - operazioni che si possono svolgere
macchine_operazioni = [[1,3,4,5,7,9,11,12,13,15,18,21,23,26,27,30,31],[1,3,4,5,7,9,11,12,13,15,18,21,23,26,27,30,31],[1,3,4,7,9,11,12,13,15,18,21,23,26,27,30,31],[16,17,19,20,22,24,25,28,29],[16,17,19,20,22,24,25,28,29],[16,17,19,20,22,24,25,28,29],[1,3,4,7,9,11,12,13,15,18,21,23,26,27,30,31],[5],[2,6,8,10,14,32],[2,6,8,10,14,32]]
# matrice macchina - tempo di processo per la relativa operazione
t_process = [[20,20,14,17,33,12.5,17,23.5,22,28,22,17,17.5,6,11.5,11,23.5],[22,22,11.5,22,37,11.5,19.5,17,20,31,11,18,23,6.5,13.5,11.5,17],[43,33.5,23,44,12,33,23,18.5,41,11,33,33,9,19,28,32],[16.5,28,11.5,17,21.5,11,16.5,12,16.5],[27,22.5,21.5,18,27,20,23,12.5,12],[32,34,32,22.5,32.5,25,22.5,23,27],[48,31,17,43.5,28,34,22,28,45,38,34,44,13,17.5,33.5,44],[33],[23,23,22.5,17,23,25],[16.5,27.5,18,18,24,23]]

#Energy consumption on
machine_energy=[20,15,6,12,10,5.5,7.5,3,5.5,10]
agv_energy=3 #kW/h
auxiliary_energy=10 #kW/h

# agv state [id prodotto che porta, distanza che deve percorrere (diminuisce a ogni minuto)]
# si attiva agv state quando
agv_state=[0,0]
agv_time= [0,0]
#distanza macchina-macchina e buffer-macchine [buffer, m1 , m2..]
dist=[[0,0,0,0,0,0,0,0,0,0,0],
      [0,0,2.54,2.84,3.22,1.67,1.87,2.89,2.75,2.37,2.22],
      [0,2.54,0,2.19,2.3,2.54,2.82,2,2.84,2.7,2.39],
      [0,2.84,2.19,0,2.66,2.52,2.34,2.2,2.85,2.04,2.34],
      [0,3.22,2.3,2.67,0,2.34,2.34,2.75,2.84,2.34,3.3],
      [0,1.67,2.54,2.52,2.34,0,1.72,1.7,2.84,3,3.2],
      [0,1.87,2.82,2.34,2.34,1.72,0,2.37,2.34,2.47,2.5],
      [0,2.88,2,2.2,2.75,1.7,2.37,0,2.5,2.7,2.67],
      [0,2.75,2.83,2.85,2.83,2.83,2.33,2.5,0,2.35,2],
      [0,2.37,2.7,2.04,2.34,3,2.47,2.7,2.35,0,2.55],
      [0,2.22,2.39,2.34,3.3,3.2,2.5,2.67,2,2.55,0]]

# dizionario con i prodotti in corso
prod_diz = []
orig_prod_diz=[]
prod_finiti = []
salvataggio_prod_diz=[]
##
# INIZIALIZZAZIONE LISTA PRODOTTI
# [id prodotto, tipo prodotto, prima operazione, macchina iniziale tutte zero all'inizio (buffer), macchina finale]
start_time = time.time()
##
g=0
k=1

while(g < len(demand)):
    while(demand[g]>0):
        prod_diz.append([[]])
        orig_prod_diz.append([[]])
        prod_diz[k-1]=[k,g,prodotti_job[g][0],0,0]
        orig_prod_diz[k-1]=[k,g,prodotti_job[g][0],0,0]
        demand[g]=demand[g]-1
        k+=1
    g+=1
random.shuffle(prod_diz)
##
# FUNZIONI
##

# aggiorna operazione se la macchina ne ha una in corso
def aggiorna_operazione(i,prod_dizio):
    if (t_operazione[i] > 0):
        t_operazione[i] -= 0.01
    else:
        for prodotti in prod_dizio:
            if prodotti[0]==stato_macchine[i] and prodotti[0] not in agv_state:
                prodotti[2] += 1
                type_prod = prodotti[1]
                if (prodotti[2] > prodotti_job[type_prod][-1]):
                    prod_finiti.append(prodotti[1])
                    prod_id_to_remove=prodotti[0]
                    prod_dizio = [prodotti for prodotti in prod_dizio if prodotti[0] != prod_id_to_remove]
        stato_macchine[i] = 0
    return prod_dizio

def aggiorna_spostamento(agv):
    if (agv_time[agv] > 0):
        agv_time[agv] -= 0.01
    else:
        for prodotti in prod_diz:
            if prodotti[0] ==agv_state[agv]:
                prodotti[3]=prodotti[4]
        agv_state[agv]=0


# cerca operazione se la macchina è libera
## VERIFICARE CHE SE IL PEZZO NON DEVE CAMBIARE MACCHINA NON ABBIA PROBLEMI
def cerca_operazione(mac, t_in):
    for prodotti in prod_diz:
        if prodotti[0] not in stato_macchine and prodotti[0] not in agv_state and 0 in agv_state:
            if prodotti[2] in macchine_operazioni[mac]:
                stato_macchine[mac] = prodotti[0]
                store = prodotti[3]
                for index, agv in enumerate(agv_state):
                    if agv ==0:
                        agv_state[index] = prodotti[0]
                        prodotti[4] = mac + 1
                        agv_time[index] = dist[prodotti[3]][prodotti[4]]
                        if (agv_time[index] == 0):
                            agv_state[index] = 0
                            prodotti[3] = prodotti[4]
                        if (agv_time[index] != 0):
                            scheduling_agv.append([index,t_in,agv_time[index],prodotti[0],prodotti[3],prodotti[4]])
                        break
                ###
                t_operazione[mac] = t_process[mac][macchine_operazioni[mac].index(prodotti[2])]+dist[store][prodotti[4]]
                scheduling_data.append([mac, t_in+dist[store][prodotti[4]], t_process[mac][macchine_operazioni[mac].index(prodotti[2])],
                                        prodotti_job[prodotti[1]].index(prodotti[2]), prodotti[0]])
                break
    return 0


# disegna gantt chart
def draw_gantt_chart(data, make,data_agv):
    fig, ax = plt.subplots(figsize=(len(data) * 1, 5))  # Adjust figsize as needed
    # colori
    unique_product_ids = set([product[4] for product in data])
    colors = plt.cm.tab20(np.linspace(0, 1, len(unique_product_ids)))

    product_colors = {}  # Dictionary to store product ID-color mapping

    for product, color in zip(unique_product_ids, colors):
        product_colors[product] = color

    for i, (machine_id, t_in, duration, operation_id, prod_id) in enumerate(data):
        ax.barh(machine_id + 1, duration, left=t_in, height=0.4, label=machine_id, color=product_colors[prod_id],
                edgecolor='black')
        ax.text(t_in + duration / 2, machine_id + 1, str(prod_id) + "," + str(operation_id + 1), ha='center',
                va='center', color='white', fontsize=5)

    for i, (agv_id,t_inizio,durata,prodotto,mac_pre,mac_post) in enumerate(data_agv):
        ax.barh(n_macchine+1+agv_id, durata, left=t_inizio, height=0.4, label=agv_id, color='orange',
                edgecolor='black')
        ax.text(t_inizio+durata / 2, n_macchine+1+agv_id, str(prodotto)+str(mac_pre)+str(mac_post), ha='center',
                va='center', color='white', fontsize=5)

    ax.set_xlabel('Time')
    ax.set_title('Job Shop Scheduling Gantt Chart')
    ax.set_xlim(0, make)
    plt.grid(axis='x', linestyle='--', alpha=0.6)

    plt.show()

##
# SIMULAZIONE
##

gen = 0
tot_gen = 1000
max_global_search=900
no_impr = 0
max_no_impr = 90
best_makespan = 0
history = []
best_makespans = []
all_makespans = []
previous_ordine_macchine=[list(range(len(stato_macchine)))]
while (gen < tot_gen):
    gen += 1
    i = 0
    while (i < durata_sim):
        # interrompe simulazione se sono finiti gli ordini
        if(gen>max_global_search and round(i,3)==i_swap):
            index1 = random.randint(0, len(prod_diz) - 1)
            index2 = random.randint(0, len(prod_diz) - 1)
            while index1 == index2:
                if(len(prod_diz)<2):
                    break
                index2 = random.randint(0, len(prod_diz) - 1)
            prod_diz[index1], prod_diz[index2] = prod_diz[index2], prod_diz[index1]
        if (len(prod_finiti) == tot_prodotti):
            break
        # guarda stato macchine e aggiorna o aggiunge operazione
        mi = 0
        while (mi < n_macchine):
            if (stato_macchine[mi] != 0):
                prod_diz = aggiorna_operazione(mi, prod_diz)
            mi += 1
        agv = 0
        while (agv < len(agv_state)):
            if (agv_state[agv] != 0):
                aggiorna_spostamento(agv)
            agv += 1

        for mac in ordine_macchine:
            if (stato_macchine[mac] == 0):
                cerca_operazione(mac, i)
        i += 0.01

    # energy calculation
    tot_agv_energy = 0
    for mission in scheduling_agv:
        tot_agv_energy=agv_energy*mission[2]/60+tot_agv_energy
    tot_prod_energy = 0
    for mission in scheduling_data:
        tot_prod_energy = machine_energy[mission[0]] * mission[2] / 60 + tot_prod_energy
    tot_energy=tot_agv_energy+tot_prod_energy+auxiliary_energy*i/60
    history.append([scheduling_data, i - 1, scheduling_agv, tot_energy])

    # Calculate and store the best makespan at this generation
    if (gen == 1):
        best_makespan = i - 1
        best_tot_energy=tot_energy
        best_machine_order= ordine_macchine
        best_prod_diz=copy.deepcopy(orig_prod_diz)
        store_prod_diz = copy.deepcopy(orig_prod_diz)
        gen_migliore=1

    # shuffle elementi e ristabilire tutti
    demand = list(orig_demand)
    prod_diz = [list(prod) for prod in orig_prod_diz]# Deep copy the original prod_diz
    prod_finiti = []

    if i - 1 <= best_makespan:
        if i-1!=best_makespan:
            best_makespan = i - 1
            best_tot_energy=tot_energy
            no_impr = 0
            gen_migliore = gen
            best_machine_order = copy.deepcopy(ordine_macchine)
            best_prod_diz = copy.deepcopy(store_prod_diz)
        else:
            if(tot_energy < best_tot_energy):
                best_makespan = i - 1
                best_tot_energy = tot_energy
                no_impr = 0
                gen_migliore = gen
                best_machine_order = copy.deepcopy(ordine_macchine)
                best_prod_diz = copy.deepcopy(store_prod_diz)
    else:
        no_impr += 1

    if (gen < max_global_search):
        random.shuffle(prod_diz)
        store_prod_diz=copy.deepcopy(prod_diz)
    else:
        ordine_macchine=copy.deepcopy(best_machine_order)
        prod_diz=copy.deepcopy(best_prod_diz)
        # Swap the elements at the two random indices.
        # at a certain time i < best durata
        i_swap=random.randint(1,int(best_makespan)*100)/100


    if (no_impr > max_no_impr and gen<max_global_search):
        random.shuffle(ordine_macchine)
        x=True
        max_it=100
        bi=0
        while(x==True):
            if ordine_macchine in previous_ordine_macchine and bi < max_it:
                random.shuffle(ordine_macchine)
                bi+=1
            else:
                x=False
            if ordine_macchine in previous_ordine_macchine and bi == max_it:
                max_global_search=gen
                print(gen)
                print(ordine_macchine)
        ordine=copy.deepcopy(ordine_macchine)
        previous_ordine_macchine.append(ordine)
        no_impr = 0

    scheduling_data = []
    scheduling_agv = []
    best_makespans.append(best_makespan)
    all_makespans.append(history[-1][1])

    plt.clf()
    plt.plot(range(1, len(best_makespans) + 1), best_makespans, marker='o', linestyle='-')
    plt.plot(range(1, len(all_makespans) + 1), all_makespans, marker='o', linestyle='', label='Makespan')
    plt.xlabel('Generation')
    plt.ylabel('Best Makespan')
    plt.title('Best Makespan Over Generations')
    plt.grid(True)
    plt.pause(0.01)

#end simulation
end_time = time.time()
# Collect data for plotting
front_makespan = [item[1] for item in history]
front_energy = [item[3] for item in history]

best_scheduling = history[gen_migliore-1][0]
best_durata=history[gen_migliore-1][1]
best_scheduling_agv=history[gen_migliore-1][2]
print("Best Makespan: ",best_durata)
print("Time Simulation: ",end_time-start_time)
# Plot the Pareto frontier
plt.figure()
plt.scatter(front_makespan, front_energy, color='b', label='Pareto Frontier')
plt.xlabel('Makespan')
plt.ylabel('Total Energy Consumption')
plt.title('Pareto Frontier: Makespan vs Total Energy Consumption')
plt.legend()
plt.show()

# disegnare gant chart migliore soluzione
# disegnare gant chart
draw_gantt_chart(best_scheduling, best_durata+2,best_scheduling_agv)
