from functools import partial
from multiprocessing import Pool, cpu_count

from tqdm import tqdm


def process_parallel(data_list, worker_func, num_processes=None, cpu_capacity_default=.85, initializer=None, kargs=None):
    """
    Processes a list in parallel with a progress bar.

    Args:
        data_list (list): The data to process.
        worker_func (function): The function to apply to each item.
        num_processes (int): Number of workers (defaults to CPU count).

    Returns:
        list: The collected results from the worker function.
    """
    if num_processes is None:
        num_processes = int(cpu_count() * cpu_capacity_default)

    results = []

    iterable_func = partial(worker_func, **kargs)

    # Using 'with' ensures the Pool is closed and joined automatically
    with Pool(processes=num_processes, initializer=initializer) as p:
        # imap returns results in the order of the input list
        with tqdm(total=len(data_list), desc="Processing") as pbar:
            for result in p.imap_unordered(iterable_func, data_list):
                results.append(result)
                pbar.update()

    return results
