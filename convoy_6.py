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
    if file_name[-5:] == '.s3db':
        s3db_to_json(file_name)
    else:
        counter = 0
        with open(file_name, 'r') as file:
            text = [file.readline()]
            for row in file:
                list_data = row.strip().split(',')
                cleanup_row = [''.join([i for i in j if i.isdigit()]) for j in list_data]
                counter += sum([list_data[j] != cleanup_row[j] for j in range(len(list_data))])
                text.append(','.join(cleanup_row) + '\n')
        if file_name[-13:] == '[CHECKED].csv':
            file_name = file_name[:-13]
        else:
            file_name = file_name.split('.')[0]
            if counter == 1:
                print('{} cell was corrected in {}[CHECKED].csv'.format(counter, file_name))
            else:
                print('{} cells were corrected in {}[CHECKED].csv'.format(counter, file_name))
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
    create_table(conn, file_name, db_filename)


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
    conn.commit()
    fuel_score(conn, db_filename)


def fuel_score(conn, db_filename):
    conn.execute('alter table convoy add column score int not null default 0')
    conn.execute('update convoy set score = 2 where maximum_load >= 20')
    conn.execute('update convoy set score = score + 1 where fuel_consumption * 4.5 > 230')
    conn.execute('update convoy set score = score + 2 where fuel_consumption * 4.5 <= 230')
    conn.execute('update convoy set score = score + 2 where fuel_consumption * 4.5 / engine_capacity < 1')
    conn.execute('update convoy set score = score + 1 where floor(fuel_consumption * 4.5 / engine_capacity) = 1')
    conn.commit()
    s3db_to_json(db_filename)


def s3db_to_json(db_filename):
    conn = sqlite3.connect(db_filename)
    database = pd.read_sql_query("SELECT * FROM convoy", conn)
    database = database.loc[database['score'] > 3]
    database = database.filter(items=database.keys()[:-1])
    result = database.to_json(orient='records')
    result = '{"convoy":' + result + '}'
    db_filename = f'{db_filename[:-5]}.json'
    with open(db_filename, 'w') as file:
        file.write(result)
    if len(database) == 1:
        print(f'1 vehicle was saved into {db_filename}')
    else:
        print(f'{len(database)} vehicles were saved into {db_filename}')
    s3db_to_xml(conn, db_filename)


def s3db_to_xml(conn, db_filename):
    database = pd.read_sql_query("SELECT * FROM convoy", conn)
    database = database.loc[database['score'] <= 3]
    database = database.filter(items=database.keys()[:-1])
    result = database.to_xml(root_name='convoy', row_name='vehicle', xml_declaration=False, index=False)
    if result == '<convoy/>':
        result = '<convoy></convoy>'
    with open(f'{db_filename[:-5]}.xml', 'w') as file:
        file.write(result)
    if len(database) == 1:
        print(f"{len(database)} vehicle was saved into {db_filename[:-5]}.xml")
    else:
        print(f"{len(database)} vehicles were saved into {db_filename[:-5]}.xml")
    close_connection(conn)


def close_connection(conn):
    if conn:
        conn.close()


def main():
    inp_file_name = input('Input file name\n')
    xlsx_csv(inp_file_name)


if __name__ == '__main__':
    main()
