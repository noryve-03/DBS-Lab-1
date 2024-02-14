"""
A suite of helper functions for the lab.

Author: Rami Pellumbi - SP24
"""

def write_results_to_csv(header: list, results: list, filename: str = 'results.csv'):
    """
    Write the results to a csv file.

    Args:
        results (list): a list of tuples, where each tuple is a row in the csv
        filename (str): the name of the file to write to
    """
    for result in results:
        if len(header) != len(result):
            raise ValueError('The number of columns in the header must match the number of columns in each row')

    with open(filename, 'w', encoding='utf-8') as f:
        f.write(','.join(header) + '\n')
        for row in results:
            f.write(','.join(map(str, row)) + '\n')