import sqlite3 as sql
import pandas as pd

GREEN = '\033[92m'
RESET = '\033[0m'

database_scores = sql.connect('scores.sqlite')
cursor_scores = database_scores.cursor()

database_courses = sql.connect('courses.sqlite')
cursor_courses = database_courses.cursor()

create_table_query_scores = '''CREATE TABLE IF NOT EXISTS scores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    course_id INTEGER NOT NULL,
    score INTEGER NOT NULL,
    par INTEGER NOT NULL,
    course_rtg INTEGER NOT NULL,
    slope INTEGER NOT NULL,
    differential INTEGER,
    over_under INTEGER
);
'''
cursor_scores.execute(create_table_query_scores)
database_scores.commit()

create_table_query_courses = '''CREATE TABLE IF NOT EXISTS courses (
    course_id INTEGER PRIMARY KEY AUTOINCREMENT,
    course_name TEXT NOT NULL,
    course_par INTEGER NOT NULL,
    course_rating DECIMAL (3,1) NOT NULL,
    slope_rating INTEGER NOT NULL
);
'''
cursor_courses.execute(create_table_query_courses)
database_courses.commit()

def main():
    ascii_art = """
░██████╗░░█████╗░██╗░░░░░███████╗  ████████╗██████╗░░█████╗░░█████╗░██╗░░██╗███████╗██████╗░
██╔════╝░██╔══██╗██║░░░░░██╔════╝  ╚══██╔══╝██╔══██╗██╔══██╗██╔══██╗██║░██╔╝██╔════╝██╔══██╗
██║░░██╗░██║░░██║██║░░░░░█████╗░░  ░░░██║░░░██████╔╝███████║██║░░╚═╝█████═╝░█████╗░░██████╔╝
██║░░╚██╗██║░░██║██║░░░░░██╔══╝░░  ░░░██║░░░██╔══██╗██╔══██║██║░░██╗██╔═██╗░██╔══╝░░██╔══██╗
╚██████╔╝╚█████╔╝███████╗██║░░░░░  ░░░██║░░░██║░░██║██║░░██║╚█████╔╝██║░╚██╗███████╗██║░░██║
░╚═════╝░░╚════╝░╚══════╝╚═╝░░░░░  ░░░╚═╝░░░╚═╝░░╚═╝╚═╝░░╚═╝░╚════╝░╚═╝░░╚═╝╚══════╝╚═╝░░╚═╝
    """

    print(GREEN + ascii_art + RESET)

    quit_program = False
    while not quit_program:
        action = get_action()
        if action == '1':
            new_row()
        elif action == '2':
            basic_stats()
        elif action == '3':
            add_new_course()
        elif action == '4':
            # Implement the graph creation logic (not provided in the original code)
            pass
        elif action == '5':
            view_most_recent_scores()
        else:
            print('ERROR: Invalid input')

        done = input('\nWould you like to end the program? (Y/N):\n').lower()
        if done == 'n':
            quit_program = False
        else:
            quit_program = True

    print(GREEN + '\nTerminating connection to the database. Goodbye!\n' + RESET)
    database_scores.commit()
    cursor_scores.close()
    database_scores.close()

    database_courses.commit()
    cursor_courses.close()
    database_courses.close()
    exit()

def get_action():
    print('\nWhat would you like to do? (Enter # of the desired action):')
    action = input('1) Add a new round to the database\n2) View some basic stats\n3) Add a new course\n4) Create a graph to compare stats\n')
    return action

def display_courses(cursor):
    cursor.execute("SELECT course_id, course_name FROM courses;")
    courses = cursor.fetchall()

    print('\nAvailable Courses:')
    for course in courses:
        course_id, course_name = course
        print(f'{course_id}. {course_name}')

def new_row():
    while True:
        display_courses(cursor_scores)
        course_id = int(input('\nSelect a course (Enter Course ID): '))

        select_course_query = '''SELECT * FROM courses WHERE course_id = ?;'''
        cursor_scores.execute(select_course_query, (course_id,))
        course_details = cursor_scores.fetchone()

        if course_details:
            course_id, course_name, course_par, course_rating, course_slope = course_details
            score = int(input(f'What did you shoot at {course_name}? '))

            insert_query = '''INSERT INTO scores
                                (course_id, score, par, course_rtg, slope, over_under, differential)
                                VALUES
                                (?, ?, ?, ?, ?, ?, ?);'''

            cursor_scores.execute(insert_query, (course_id, score, course_par, course_rating, course_slope, score - course_par, (113 / course_slope) * (score - course_rating)))
            print(GREEN + 'Round added successfully!' + RESET)
        else:
            print(GREEN + 'Invalid course selection.' + RESET)

        another_round = input('\nDo you want to enter another round? (Y/N): ').lower()
        if another_round != 'y':
            break

def get_stats():
    avg_score = '''SELECT AVG(score) AS avg_score FROM scores'''
    avg_over_under = '''SELECT AVG(over_under) AS avg_over_under FROM scores'''
    avg_differential = '''SELECT AVG(differential) AS avg_differential FROM scores'''

    best_score = '''SELECT MIN(score) AS low_score FROM scores'''
    worst_score = '''SELECT MAX(score) AS high_score FROM scores'''
    best_over_under = '''SELECT MIN(over_under) AS low_over_under FROM scores'''
    lowest_differential = '''SELECT MIN(differential) AS lowest_differential FROM scores'''

    avg_score = pd.read_sql_query(avg_score, database_scores)
    avg_over_under = pd.read_sql_query(avg_over_under, database_scores)
    avg_differential = pd.read_sql_query(avg_differential, database_scores)

    best_score = pd.read_sql_query(best_score, database_scores)
    worst_score = pd.read_sql_query(worst_score, database_scores)
    best_over_under = pd.read_sql_query(best_over_under, database_scores)
    lowest_differential = pd.read_sql_query(lowest_differential, database_scores)

    return [[avg_score, avg_over_under, avg_differential], [best_score, worst_score, best_over_under, lowest_differential]]

def basic_stats():
    stats = get_stats()

    print('\nYour Averages:')
    print(f'   Average Score: {round(stats[0][0]["avg_score"].iloc[0], 2)}')
    print(f'   Average Over/Under: {round(stats[0][1]["avg_over_under"].iloc[0], 2)}')
    print(f'   Average Differential: {round(stats[0][2]["avg_differential"].iloc[0], 2)}')

    print('\nPersonal Bests and Additional Stats:')
    print(f'    Lowest Score: {int(stats[1][0]["low_score"].iloc[0])}')
    print(f'    Lowest Over/Under: {int(stats[1][2]["low_over_under"].iloc[0])}')
    print(f'    Lowest Differential: {round(stats[1][3]["lowest_differential"].iloc[0], 2)}')

def add_new_course():
    print('\nEnter details for the new course:')
    course_name = input('Course Name: ')
    course_par = int(input('Par: '))
    course_rating = float(input('Course Rating: '))
    slope_rating = int(input('Slope Rating: '))

    insert_course_query = '''INSERT INTO courses
                            (course_name, course_par, course_rating, slope_rating)
                            VALUES (?, ?, ?, ?);'''

    cursor_scores.execute(insert_course_query, (course_name, course_par, course_rating, slope_rating))
    database_scores.commit()

    print(GREEN + 'New course added successfully!' + RESET)

    # Refresh list of courses
    display_courses(cursor_scores)
    
def view_most_recent_scores():
    select_recent_scores_query = '''
    SELECT course_name AS 'Course', score AS 'Score', over_under AS 'Over/Under', differential AS 'Differential'
    FROM scores
    JOIN courses ON scores.course_id = courses.course_id
    ORDER BY id
    LIMIT 20;
    '''

    recent_scores = pd.read_sql_query(select_recent_scores_query, database_scores)

    if not recent_scores.empty:
        print("\nMost Recent Scores:")
        print(recent_scores)
    else:
        print("No recent scores found.")

def get_action():
    print('\nWhat would you like to do? (Enter # of the desired action):')
    action = input('1) Add a new round to the database\n2) View some basic stats\n3) Add a new course\n4) Create a graph to compare stats\n5) View most recent scores\n')
    return action

if __name__ == '__main__':
    main()
