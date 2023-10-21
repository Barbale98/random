import matplotlib.pyplot as plt
import numpy as np
import random

durata_sim = 1000000
scheduling_data = []
# domanda prodotto 1 e 2
demand = [40,40,40,40,40]
orig_demand=tuple(demand)
# vettore che contiene i prodotti associati alle operazioni, 2 prodotti, 5 operazioni
prodotti_job = [[1, 2,3,4,5,6,7,8], [9,10,11,12,13,14,15,16],[17,18,19,20],[21,22],[23]]

tot_prodotti = 0
for prod in demand:
    tot_prodotti = prod + tot_prodotti

# vettore che contiene lo stato delle macchine, 0 se nulla, id prodotto se contiene un prodotto
stato_macchine = [0, 0, 0, 0, 0,0,0,0,0,0,0,0,0,0]
t_operazione = [0, 0, 0, 0, 0,0,0,0,0,0,0,0,0,0]
n_macchine = len(stato_macchine)
ordine_macchine=[0,1,2,3,4,5,6,7,8,9,10,11,12,13]
# matrice macchina - operazioni che si possono svolgere
macchine_operazioni = [[1,9,17,21],[1,9,17,21],[1,9,17,21,7,15,19],[1,9,17,21,3,11],[2,10],[4,12,18,22],[4,12,18,22],[5,13,23],[5,13,23],[5,13,23],[6,14],[7,15,19],[8,16,20],[8,16,20]]
# matrice macchina - tempo di processo per la relativa operazione
t_process = [[60,60,60,60],[79,79,79,79],[90,90,90,90,36,36,36],[90,90,90,90,36,36],[85,85],[80,80,80,80],[70,70,70,70],[60,60,60],[40,40,40],[20,20,20],[40,40],[40,40,40],[100,100,100],[70,70,70]]

# dizionario con i prodotti in corso
prod_diz = []
orig_prod_diz=[]
prod_finiti = []

##
# INIZIALIZZAZIONE LISTA PRODOTTI
##
g=0
k=1

while(g < len(demand)):
    while(demand[g]>0):
        prod_diz.append([[]])
        orig_prod_diz.append([[]])
        prod_diz[k-1]=[k,g,prodotti_job[g][0]]
        orig_prod_diz[k-1]=[k,g,prodotti_job[g][0]]
        demand[g]=demand[g]-1
        k+=1
    g+=1

##
# FUNZIONI
##

# aggiorna operazione se la macchina ne ha una in corso
def aggiorna_operazione(i, t_in, prod_diz):
    if (t_operazione[i] > 0):
        t_operazione[i] -= 1
    if (t_operazione[i] == 0):
        for prodotti in prod_diz:
            if prodotti[0]==stato_macchine[i]:
                prodotti[2] += 1
                type_prod = prodotti[1]
                if (prodotti[2] > prodotti_job[type_prod][-1]):
                    prod_finiti.append(prodotti[1])
                    prod_id_to_remove=prodotti[0]
                    prod_diz = [prodotti for prodotti in prod_diz if prodotti[0] != prod_id_to_remove]
        stato_macchine[i] = 0
    return prod_diz


# cerca operazione se la macchina è libera
def cerca_operazione(i, t_in):
    # qui servirebbe una funzione che ordina prod_diz
    for prodotti in prod_diz:
        if prodotti[0] not in stato_macchine:
            if prodotti[2] in macchine_operazioni[i]:
                stato_macchine[i] = prodotti[0]
                t_operazione[i] = t_process[i][macchine_operazioni[i].index(prodotti[2])]
                scheduling_data.append([i, t_in, t_process[i][macchine_operazioni[i].index(prodotti[2])],
                                        prodotti_job[prodotti[1]].index(prodotti[2]), prodotti[0]])
                break
    return 0


# disegna gantt chart
def draw_gantt_chart(data, make):
    fig, ax = plt.subplots(figsize=(len(data) * 1, 5))  # Adjust figsize as needed
    # colori
    unique_product_ids = set([product[4] for product in data])
    colors = plt.cm.tab20(np.linspace(0, 1, len(unique_product_ids)))

    product_colors = {}  # Dictionary to store product ID-color mapping

    for product, color in zip(unique_product_ids, colors):
        product_colors[product] = color

    # dovrei avere un colore per ogni prodotto
    for i, (machine_id, t_in, duration, operation_id, prod_id) in enumerate(data):
        ax.barh(machine_id + 1, duration, left=t_in, height=0.4, label=machine_id, color=product_colors[prod_id],
                edgecolor='black')
        ax.text(t_in + duration / 2, machine_id + 1, str(prod_id) + "," + str(operation_id + 1), ha='center',
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
no_impr=0
max_no_impr=50
best_makespan=0
gen_migliore=1
history = []
best_makespans = []
all_makespans=[]

while (gen < tot_gen):
    gen += 1
    i = 0
    while (i < durata_sim):
        # interrompe simulazione se sono finiti gli ordini
        if (len(prod_finiti) == tot_prodotti):
            break
        # guarda stato macchine e aggiorna o aggiunge operazione
        m = 0
        while (m < n_macchine):
            if (stato_macchine[m] != 0):
                prod_diz=aggiorna_operazione(m, i,prod_diz)
            m += 1
        m = 0
        for mac in ordine_macchine:
            if (stato_macchine[mac] == 0):
                cerca_operazione(mac, i)
        i += 1
    # aggiungere individuo allo storico
    history.append([scheduling_data, i-1])
    #shuffle elementi e ristabilire tutti
    demand=list(orig_demand)
    prod_diz = [list(prod) for prod in orig_prod_diz]  # Deep copy the original prod_diz
    prod_finiti=[]
    random.shuffle(prod_diz)
    scheduling_data=[]

    # Calculate and store the best makespan at this generation
    if(gen==1):
        best_makespan=i-1
    if i-1<best_makespan:
        best_makespan = i-1
        no_impr=0
        gen_migliore=gen
    else: no_impr+=1
    if(no_impr>max_no_impr):
        random.shuffle(ordine_macchine)
        print(ordine_macchine)
        print(gen)
        no_impr=0
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


# Plot the best makespan over generations
plt.plot(range(1, len(best_makespans) + 1), best_makespans, marker='o', linestyle='-')
plt.plot(range(1, len(all_makespans) + 1), all_makespans, marker='o', linestyle='', label='Makespan')
plt.xlabel('Generation')
plt.ylabel('Best Makespan')
plt.title('Best Makespan Over Generations')
plt.grid(True)
plt.show()

# disegnare gant chart migliore soluzione

best_scheduling = history[gen_migliore-1][0]
best_durata=history[gen_migliore-1][1]
print(best_durata)
# disegnare gant chart
draw_gantt_chart(best_scheduling, best_durata+1)
