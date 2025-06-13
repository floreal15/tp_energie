import os
import time
import statistics
from src.scheduling.instance.instance import Instance
from src.scheduling.optim.constructive import Greedy, NonDeterminist
from src.scheduling.optim.local_search import FirstNeighborLocalSearch, BestNeighborLocalSearch
from src.scheduling.optim.neighborhoods import MyNeighborhood1

DATA_DIR = 'data'
N_RUNS = 10  # nombre d'exécutions pour les algos non-déterministes

def get_instance_folders(data_dir):
    return [os.path.join(data_dir, d) for d in os.listdir(data_dir)
            if os.path.isdir(os.path.join(data_dir, d))]

def run_greedy(inst):
    try:
        start = time.time()
        sol = Greedy().run(inst)
        elapsed = time.time() - start
        return sol.objective, elapsed
    except Exception as e:
        return 'failed', 'failed'

def run_first_local(inst):
    best_obj = None
    best_time = None
    for _ in range(N_RUNS):
        try:
            start = time.time()
            sol = FirstNeighborLocalSearch().run(inst, NonDeterminist, MyNeighborhood1)
            elapsed = time.time() - start
            if best_obj is None or sol.objective < best_obj:
                best_obj = sol.objective
                best_time = elapsed
        except Exception as e:
            continue
    if best_obj is None:
        return 'failed', 'failed'
    return best_obj, best_time

def run_best_local(inst):
    best_obj = None
    best_time = None
    for _ in range(N_RUNS):
        try:
            start = time.time()
            sol = BestNeighborLocalSearch().run(inst, NonDeterminist)
            elapsed = time.time() - start
            if best_obj is None or sol.objective < best_obj:
                best_obj = sol.objective
                best_time = elapsed
        except Exception as e:
            continue
    if best_obj is None:
        return 'failed', 'failed'
    return best_obj, best_time

def main():
    folders = sorted(get_instance_folders(DATA_DIR))
    results = []
    nb_fail_greedy = 0
    nb_fail_first_local = 0
    nb_fail_best_local = 0
    for folder in folders:
        print("folder :" + str(folder))
        try:
            inst = Instance.from_file(folder)
        except Exception as e:
            print(f"Erreur lors du chargement de l'instance {folder}: {e}")
            continue
        greedy_obj, greedy_time = run_greedy(inst)
        if greedy_obj == 'failed':
            nb_fail_greedy += 1
        first_local_obj, first_local_time = run_first_local(inst)
        if first_local_obj == 'failed':
            nb_fail_first_local += 1
        best_local_obj, best_local_time = run_best_local(inst)
        if best_local_obj == 'failed':
            nb_fail_best_local += 1
        results.append({
            'instance': os.path.basename(folder),
            'greedy_obj': greedy_obj,
            'greedy_time': greedy_time,
            'first_local_obj': first_local_obj,
            'first_local_time': first_local_time,
            'best_local_obj': best_local_obj,
            'best_local_time': best_local_time,
        })
    # Statistiques globales (on ne garde que les réussites)
    greedy_times = [r['greedy_time'] for r in results if r['greedy_time'] != 'failed']
    first_local_times = [r['first_local_time'] for r in results if r['first_local_time'] != 'failed']
    best_local_times = [r['best_local_time'] for r in results if r['best_local_time'] != 'failed']
    greedy_objs = [r['greedy_obj'] for r in results if r['greedy_obj'] != 'failed']
    first_local_objs = [r['first_local_obj'] for r in results if r['first_local_obj'] != 'failed']
    best_local_objs = [r['best_local_obj'] for r in results if r['best_local_obj'] != 'failed']
    # Comptage des meilleurs (seulement sur les instances où tous ont réussi)
    greedy_best = 0
    first_local_best = 0
    best_local_best = 0
    for r in results:
        if 'failed' in (r['greedy_obj'], r['first_local_obj'], r['best_local_obj']):
            continue
        min_obj = min(r['greedy_obj'], r['first_local_obj'], r['best_local_obj'])
        if r['greedy_obj'] == min_obj:
            greedy_best += 1
        if r['first_local_obj'] == min_obj:
            first_local_best += 1
        if r['best_local_obj'] == min_obj:
            best_local_best += 1
    # Rapport
    print("\n===== Rapport de comparaison des heuristiques =====\n")
    print(f"Nombre d'instances testées : {len(results)}\n")
    print("Temps moyen (en secondes) :")
    print(f"  Greedy : {statistics.mean(greedy_times):.4f}" if greedy_times else "  Greedy : échec sur toutes les instances")
    print(f"  Recherche locale 1 (premier voisin améliorant) : {statistics.mean(first_local_times):.4f}" if first_local_times else "  Recherche locale 1 : échec sur toutes les instances")
    print(f"  Recherche locale 2 (meilleur voisin sur deux voisinages) : {statistics.mean(best_local_times):.4f}" if best_local_times else "  Recherche locale 2 : échec sur toutes les instances")
    print("\nObjectif moyen :")
    print(f"  Greedy : {statistics.mean(greedy_objs):.2f}" if greedy_objs else "  Greedy : échec sur toutes les instances")
    print(f"  Recherche locale 1 : {statistics.mean(first_local_objs):.2f}" if first_local_objs else "  Recherche locale 1 : échec sur toutes les instances")
    print(f"  Recherche locale 2 : {statistics.mean(best_local_objs):.2f}" if best_local_objs else "  Recherche locale 2 : échec sur toutes les instances")
    print("\nNombre de fois où chaque algorithme est le meilleur (objectif minimal, uniquement sur les instances où tous ont réussi) :")
    print(f"  Greedy : {greedy_best}")
    print(f"  Recherche locale 1 : {first_local_best}")
    print(f"  Recherche locale 2 : {best_local_best}")
    print("\nNombre d'échecs :")
    print(f"  Greedy : {nb_fail_greedy}")
    print(f"  Recherche locale 1 : {nb_fail_first_local}")
    print(f"  Recherche locale 2 : {nb_fail_best_local}")
    print("\nRemarques :")
    print("- Les recherches locales sont lancées 10 fois par instance, seul le meilleur résultat est conservé.")
    print("- Un objectif plus bas est meilleur.")
    print("- Les temps incluent uniquement le calcul de la solution, pas le chargement de l'instance.")
    print("- Les résultats peuvent varier légèrement d'une exécution à l'autre à cause de la non-déterminisme.")
    print("- Les échecs (exceptions) ne sont pas pris en compte dans les moyennes.")

if __name__ == '__main__':
    main()
