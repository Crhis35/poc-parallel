import time
import timeit
import random
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import ProcessPoolExecutor


def io_heavy_function(dummy_input: int):
    ''' mimic IO heavy task (e.g. download webpage) using time.sleep
    '''
    tot = random.randint(0, 10000)
    time.sleep(0.1)
    return tot % 10


def cpu_heavy_function(dummy_input: int):
    ''' mimic CPU heavy task (e.g. scientific calculation) using random.randint
    '''
    # sum = 0 #Takes much time
    # for i in range(20_000_000):
    #     sum += i
    # return sum
    tot = sum([random.randint(0, 10) for i in range(110000)])
    return tot % 10


def eval_parallel(parallel_method: str, function_type: str, n_workers: int):
    ''' evaluate multi-thread or multi-process performance '''
    # whether use multi thread or multi process
    parallel_method_dict = {
        'multithread': ThreadPoolExecutor,
        'multiprocessor': ProcessPoolExecutor
    }
    # whether the function is io-heavy or cpu-heavy
    function_type_dict = {
        'io_heavy': io_heavy_function,
        'cpu_heavy': cpu_heavy_function
    }
    the_method = parallel_method_dict[parallel_method]
    the_function = function_type_dict[function_type]

    # run the function for 100 times (~10 seconds), and use n_workers to parallel
    n_item = 100
    with the_method(n_workers) as executor:
        results = executor.map(the_function, range(n_item))
    return sum([x for x in results])


if __name__ == "__main__":

    # initiate with all the parallel computing method and function types
    method_function_list = [
        ("multithread", "io_heavy"),
        ("multithread", "cpu_heavy"),
        ("multiprocessor", "io_heavy"),
        ("multiprocessor", "cpu_heavy")]

    # how many times the eval_parallel is calculated to provide an accurate measure
    n_eval = 5
    n_worker_list = [1, 2, 4, 8, 16, 34, 64]
    result_df_list = []

    # run the given parallel methods & functions sequentially
    for the_method, the_function in method_function_list:
        time_list = [timeit.timeit(
            'eval_parallel("{0}", "{1}", {2})'.format(
                the_method, the_function, n_worker),
            number=n_eval, globals=globals()) / n_eval for n_worker in n_worker_list]
        print(
            ' -- completed evaluate: {0}, {1} -- '.format(the_method, the_function))
        result_df_list.append(pd.DataFrame({
            'method': the_method,
            'function': the_function,
            'n_workers': n_worker_list,
            'time_spent': time_list}))
    result_df = pd.concat(result_df_list)
    print(result_df)
    result_df.plot.bar(x='n_workers',)

    result_df['type'] = result_df['method'] + ':' + result_df['function']
    sns.barplot(x='n_workers', y='time_spent', data=result_df, hue='type',)
    plt.show()
