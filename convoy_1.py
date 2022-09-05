import pandas as pd


def xlsx_csv(file_name):
    vehicles_df = pd.read_excel(file_name, sheet_name='Vehicles', dtype=str)
    file_name = file_name.replace('.xlsx', '.csv')
    vehicles_df.to_csv(file_name, index=None, header=True)
    if vehicles_df.shape[0] == 1:
        print(f'{vehicles_df.shape[0]} line was imported to {file_name}')
    else:
        print(f'{vehicles_df.shape[0]} lines were imported to {file_name}')


def main():
    inp_file_name = input('Input file name\n')
    xlsx_csv(inp_file_name)


if __name__ == '__main__':
    main()