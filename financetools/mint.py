import csv
import os
from .helpers import print_error_and_quit


MINT_CSV_HEADERS = [
    'Date',
    'Description',
    'Original Description',
    'Amount',
    'Transaction Type',
    'Category',
    'Account Name',
    'Labels',
    'Notes'
]


def read_mint_csv(input_file, verbose):
    ''' Read a Mint CSV file and return the transactions '''
    if verbose:
        print('Reading CSV file: ' + input_file)

    transactions = []

    with open(input_file, 'r', newline='') as csv_file:
        try:
            input_file = csv.DictReader(csv_file, quoting=csv.QUOTE_ALL, fieldnames=MINT_CSV_HEADERS)
            is_header = True
            for row in input_file:
                if is_header:
                    is_header = False
                    continue
                transactions.append(row)
        except ValueError:
            print_error_and_quit('Invalid CSV file: ' + input_file)

    return transactions


def validate_mint_csv_contents(transactions, verbose):
    ''' Validate the Mintness of a set of CSV rows '''
    row_num = 1
    for transaction in transactions:
        row_num = row_num + 1
        if len(transaction) != len(MINT_CSV_HEADERS):
            print_error_and_quit(
                'Invalid Mint CSV file contents: row ' + str(row_num) + ' doesn\'t have the correct number of columns')


def validate_mint_csv(input_file, verbose):
    ''' Validate a Mint CSV file '''
    if verbose:
        print('Validating Mint CSV file: ' + input_file)

    transactions = read_mint_csv(input_file, verbose)
    validate_mint_csv_contents(transactions, verbose)


def validate_mint_csvs(input_dir, verbose):
    ''' Validate a directory of Mint CSV files '''
    if verbose:
        print('Validating Mint CSV files in directory: ' + input_dir)

    for file in os.listdir(input_dir):
        if file.endswith('.csv'):
            validate_mint_csv(os.path.join(input_dir, file), verbose)
