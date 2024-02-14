"""
Task 2: Find overlapping sections

This task involves the creation of a new table called `overlapping_sections` that
contains all pairs of sections that overlap. Join the section and time_slot tables
to get the section and time slot details for each section. For each pair of sections
that overlap, write the course ID, section ID, and time range that the sections overlap for 
to the `overlapping_sections` table.

E.g., the following two sections overlap on Monday from 10:00 to 10:15:
    CPSC-437-001, Monday, 2017, fall, 09:00-10:15
    CPSC-237-002, Monday, 2017, fall, 10:00-10:45

The above example was used for illustration purposes only and is not necessarily the 
shape of the data you will be working with.

You will also write the results to a CSV file called task2.csv.

The CSV file should look like this:
    day, course_id_1, sec_id_1, year_1, semester_1, course_id_2, sec_id_2, year_2, sem_2, overlap_time_start, overlap_time_end
      M,    CPSC-437,      001,   2017,       fall,    CPSC-237,      002,   2017,  fall,              10:00,            10:15

Author: Rami Pellumbi - SP24
"""

# feel free to add any imports you need here that do not require a package
# outside of requirements.txt or the standard library
from typing import TypedDict

from database_connection import DatabaseConnection
from helpers import write_results_to_csv

def create_overlapping_sections_table_if_not_exists():
    """
    Create the overlapping_sections table if it does not exist.
    """
    with DatabaseConnection() as conn:
        cursor = conn
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS overlapping_sections (
                day CHAR(1),
                course_id_1 VARCHAR(20),
                sec_id_1 VARCHAR(20),
                year_1 INT,
                semester_1 VARCHAR(20),
                course_id_2 VARCHAR(20),
                sec_id_2 VARCHAR(20),
                year_2 INT,
                semester_2 VARCHAR(20),
                overlap_time_start TIME,
                overlap_time_end TIME
            )
        """)

# utility type for time slots
TimeSlotInfo = TypedDict('TimeSlotInfo',
                         {'day': str,
                          'semester': str,
                          'year': int,
                          'start_hr': int,
                          'start_min': int,
                          'end_hr': int,
                          'end_min': int})

def is_overlap(slot1: TimeSlotInfo, slot2: TimeSlotInfo) -> None | tuple[str, str]:
    # Convert start and end times to minutes for easier comparison
    start1 = slot1['start_hr'] * 60 + slot1['start_min']
    end1 = slot1['end_hr'] * 60 + slot1['end_min']
    start2 = slot2['start_hr'] * 60 + slot2['start_min']
    end2 = slot2['end_hr'] * 60 + slot2['end_min']

    # Check for overlap
    latest_start = max(start1, start2)
    earliest_end = min(end1, end2)
    if latest_start < earliest_end:
        # There is an overlap
        overlap_start_hr, overlap_start_min = divmod(latest_start, 60)
        overlap_end_hr, overlap_end_min = divmod(earliest_end, 60)
        # Format the times as HH:MM
        overlap_start_time = f"{overlap_start_hr}:{overlap_start_min}"
        overlap_end_time = f"{overlap_end_hr}:{overlap_end_min}"
        return overlap_start_time, overlap_end_time
    else:
        # There is no overlap
        return None

def task2():
        """
        Implement this function to complete task 2.
        """
        create_overlapping_sections_table_if_not_exists()
        with DatabaseConnection() as db: 
            cursor = db 
            cursor.execute("""
                SELECT course_id, sec_id, semester, year, day, start_hr, start_min, end_hr, end_min
                FROM section NATURAL JOIN time_slot
            """)
            sections = cursor.fetchall()
            overlapping_sections = []
        for i, section1 in enumerate(sections):
            for section2 in sections[i+1:]:
                # Check if sections are on the same day, semester, and year
                if section1[3] == section2[3] and section1[2] == section2[2] and section1[4] == section2[4]:
                    # Create TimeSlotInfo for each section
                    slot1 = TimeSlotInfo(day=section1[4], semester=section1[2], year=section1[3],
                                         start_hr=section1[5], start_min=section1[6],
                                         end_hr=section1[7], end_min=section1[8])
                    slot2 = TimeSlotInfo(day=section2[4], semester=section2[2], year=section2[3],
                                         start_hr=section2[5], start_min=section2[6],
                                         end_hr=section2[7], end_min=section2[8])
                    # Check for time overlap using is_overlap
                    overlap = is_overlap(slot1, slot2)
                    if overlap:
                        overlapping_sections.append(
                            (section1[4], section1[0], section1[1], section1[3], section1[2],
                             section2[0], section2[1], section2[3], section2[2], overlap[0], overlap[1])
                        )

        # Write overlapping sections to the database
        with DatabaseConnection() as db: 
            cursor = db
            for overlap in overlapping_sections:
                cursor.execute("""
                    INSERT INTO overlapping_sections (
                        day, course_id_1, sec_id_1, year_1, semester_1,
                        course_id_2, sec_id_2, year_2, semester_2,
                        overlap_time_start, overlap_time_end
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, overlap)

        # Write results to CSV
        header = [
            'day', 'course_id_1', 'sec_id_1', 'year_1', 'semester_1',
            'course_id_2', 'sec_id_2', 'year_2', 'semester_2',
            'overlap_time_start', 'overlap_time_end'
        ]
        write_results_to_csv(header, overlapping_sections, 'task2.csv')


if __name__ == '__main__':
    task2()
