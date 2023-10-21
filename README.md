# Flexible Job Shop Scheduling with AGV constraint
Multi objective Flexible Job Shop Scheduling with transportation constraint considering Makespan and Energy consumption with Random search greedy algorithm.

Two vectors define the precedence rule for assigning each operation to a specific machine:
Job sequences: prod_diz
Machine order: ordine_macchine

There's no local optimal decision making.
Just randomly exploring different solutions and selecting the best one based on makespan.
Then the Pareto frontline of two objectives is plotted for all found solutions and the best scheduling can be chosen.

Many improvements are possible. First of all trying dispatching rules such as Shortest processing time. 

Local search is also implemented at the end of the generated solutions. Where instead of shuffling the entire job sequence only two pairs are shuffled in order to find a local optimal solution from the best solution found in the global search.
