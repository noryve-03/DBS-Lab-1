"""
Task 1: Department Salary Statistics

Plot the median, average, and standard deviation of instructor salaries by department. 
If a department has only one instructor, then the standard deviation should be 0.

- The plot should have the department names on the x-axis and the salary on the y-axis.
    - The median salary should be plotted as a bar chart.
    - The average salary should be plotted as a line chart (overlaying the bars).
    - The standard deviation should be plotted as a vertical lines stemming from the line chart.
    - Save the plot as a png file called task1.png.
- The results should be written to a csv file called task1.csv.
    - The header should be `dept,median,avg,stddev`
- The results should populate the `salary_statistics` table.

Author: Rami Pellumbi - SP24
"""

# feel free to add any imports you need here that do not require a package
# outside of requirements.txt or the standard library

from database_connection import DatabaseConnection
from helpers import write_results_to_csv
import matplotlib.pyplot as plt 
import numpy as np 


def create_salary_statistics_if_not_exists():
    """
    Create the salary_statistics table if it does not exist.
    """
    with DatabaseConnection() as conn:
        cursor = conn
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS salary_statistics (
                dept_name VARCHAR(20),
                median_salary NUMERIC(8, 2),
                average_salary NUMERIC(8, 2),
                std_dev_salary NUMERIC(8, 2),
                PRIMARY KEY (dept_name),
                FOREIGN KEY (dept_name) REFERENCES department(dept_name)
                ON DELETE SET NULL
            )
        """)

def task1():
    """
    Implement this function to complete task 1.
    """
    create_salary_statistics_if_not_exists()
    with DatabaseConnection() as db: 
        cursor = db
        cursor.execute("SELECT dept_name, salary FROM instructor")
        data = cursor.fetchall()

    # Organize data by department
    salaries_by_dept = {}
    for dept_name, salary in data:
        if dept_name not in salaries_by_dept:
            salaries_by_dept[dept_name] = []
        salaries_by_dept[dept_name].append(salary)
    
    # Calculate statistics
    stats = {}
    for dept, salaries in salaries_by_dept.items():
        median_salary = np.median(salaries)
        average_salary = np.mean(salaries)
        std_dev_salary = np.std(salaries, ddof=1) if len(salaries) > 1 else 0
        stats[dept] = (int(median_salary), int(average_salary), int(std_dev_salary))
    
    # Plotting
    departments = list(stats.keys())
    median_salaries = [stat[0] for stat in stats.values()]
    average_salaries = [stat[1] for stat in stats.values()]
    std_devs = [stat[2] for stat in stats.values()]
    
    fig, ax = plt.subplots()
    ax.bar(departments, median_salaries, label='Median Salary')
    ax.plot(departments, average_salaries, label='Average Salary', color='orange')
    
    # Add standard deviation lines
    for i, std_dev in enumerate(std_devs):
        ax.vlines(departments[i], average_salaries[i] - std_dev, average_salaries[i] + std_dev, color='red', label='Std Dev' if i == 0 else "")
    
    # Add labels and legend
    ax.set_xlabel('Department')
    ax.set_ylabel('Salary')
    ax.legend()
    
    # Save the plot
    plt.savefig('task1.png')
    
    # Write results to CSV
    # write_results_to_csv('task1.csv', ['dept', 'median', 'avg', 'stddev'], stats.items())
    write_results_to_csv(['dept', 'median', 'avg', 'stddev'],[[dept, *values] for dept, values in stats.items()] , 'task1.csv')
    # print(list([[dept, *values] for dept, values in stats.items()]))
    # Populate the salary_statistics table
    with DatabaseConnection() as db: 
        cursor = db
        for dept, (median, avg, stddev) in stats.items():
            # print(dept, "\n")
            # Insert into the DB, while making sure we avoid collisions
            cursor.execute("""
                INSERT INTO salary_statistics (dept_name, median_salary, average_salary, std_dev_salary)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (dept_name) DO UPDATE SET
                median_salary = EXCLUDED.median_salary,
                average_salary = EXCLUDED.average_salary,
                std_dev_salary = EXCLUDED.std_dev_salary
            """, (dept, median, avg, stddev))
    
if __name__ == '__main__':
    task1()
