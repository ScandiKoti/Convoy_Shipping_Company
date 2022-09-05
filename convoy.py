import pandas as pd


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
    file_name = file_name.split('.')[0]
    with open(f'{file_name}[CHECKED].csv', 'w') as file:
        for row in text:
            file.write(row)
    if count == 1:
        print('{} cell was corrected in {}[CHECKED].csv'.format(count, file_name))
    else:
        print('{} cells were corrected in {}[CHECKED].csv'.format(count, file_name))


def main():
    inp_file_name = input('Input file name\n')
    xlsx_csv(inp_file_name)


if __name__ == '__main__':
    main()
