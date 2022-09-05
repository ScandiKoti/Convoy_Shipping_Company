import pandas as pd
import sqlite3
import csv
from sqlite3 import Error


def xlsx_csv(file_name):
    if file_name[-5:] == '.xlsx':
        vehicles_df = pd.read_excel(file_name, sheet_name='Vehicles', dtype=str)
        file_name = file_name.replace('.xlsx', '.csv')
        vehicles_df.to_csv(file_name, index=False, header=True, encoding='utf-8')
        if vehicles_df.shape[0] == 1:
            print(f'{vehicles_df.shape[0]} line was imported to {file_name}')
        else:
            print(f'{vehicles_df.shape[0]} lines were imported to {file_name}')
    check_file(file_name)


def check_file(file_name):
    count = 0
    with open(file_name, 'r') as file:
        text = [file.readline()]
        for row in file:
            list_data = row.strip().split(',')
            cleanup_row = [''.join([i for i in j if i.isdigit()]) for j in list_data]
            count += sum([list_data[j] != cleanup_row[j] for j in range(len(list_data))])
            text.append(','.join(cleanup_row) + '\n')
    if file_name[-13:] == '[CHECKED].csv':
        file_name = file_name[:-13]
    else:
        file_name = file_name.split('.')[0]
        if count == 1:
            print('{} cell was corrected in {}[CHECKED].csv'.format(count, file_name))
        else:
            print('{} cells were corrected in {}[CHECKED].csv'.format(count, file_name))
    with open(f'{file_name}[CHECKED].csv', 'w') as file:
        for row in text:
            file.write(row)
    create_connection(file_name)


def create_connection(file_name):
    db_filename = f'{file_name}.s3db'
    conn = None
    try:
        conn = sqlite3.connect(db_filename)
    except Error as e:
        print(e)
    if conn is not None:
        create_table(conn, file_name, db_filename)
    else:
        print("Error! cannot create the database connection.")


def create_table(conn, file_name, db_filename):
    db_table = 'convoy'
    c = conn.cursor()
    c.execute(f'drop table if exists {db_table};')
    with open(f'{file_name}[CHECKED].csv', 'r') as w_file:
        count = 0
        file_reader = csv.reader(w_file, delimiter=',', lineterminator='\n')
        for line in file_reader:
            if count == 0:
                headers = tuple(line)
                c.execute(f'create table if not exists {db_table}({headers[0]} int primary key,'
                          f' {headers[1]} int not null, {headers[2]} int not null, {headers[3]} int not null);')
                count = 1
            else:
                values = tuple(line)
                c.execute(f'insert into convoy{headers} values{values};')
                count += 1
        print(f'{count - 1} record{"s were" if count != 2 else " was"} inserted into {db_filename}')
    if conn:
        conn.commit()
        conn.close()


def main():
    inp_file_name = input('Input file name\n')
    xlsx_csv(inp_file_name)


if __name__ == '__main__':
    main()
