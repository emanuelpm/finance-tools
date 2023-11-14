''' Helper program to convert Mint CSV files to the desired input formats for other programs '''

import argparse
import csv
import os
import re


EXPECTED_MINT_CSV_HEADERS = [
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

SUPPORTED_ACTIONS = [
    "StripHeaders",
    "ModifyDebitAmounts",
    "RemoveTransType"
]


''' Print an error message and exit the program '''
def print_error_and_quit(message):
    print(message)
    exit(1)

''' Read a Mint CSV file and return the transactions '''
def read_mint_csv(input_file, verbose):
    if verbose:
        print('Reading CSV file: ' + input_file)

    transactions = []

    with open(input_file, 'r', newline='') as csv_file:
        try:
            input_file = csv.DictReader(csv_file, quoting=csv.QUOTE_ALL, fieldnames=EXPECTED_MINT_CSV_HEADERS)
            for row in input_file:
                transactions.append(row)
        except ValueError:
            print_error_and_quit('Invalid CSV file: ' + input_file)

    return transactions

''' Write the converted CSV file '''
def write_csv(output_file, header, write_header, transactions, verbose):
    if verbose:
        print('Writing CSV file: ' + output_file)

    with open(output_file, 'w', newline='') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=header)
        if write_header:
            writer.writeheader()
        for transaction in transactions:
            writer.writerow(transaction)

''' Convert the CSV file then write it out'''
def convert_mint_csv(input_file, output_file, actions, verbose):
    if verbose:
        print('Converting Mint CSV file: ' + input_file + ' to ' + output_file)

    transactions = read_mint_csv(input_file, verbose)
    validate_mint_csv_contents(transactions, verbose)

    # Python doesn't have constants so be sure to copy since we will perform destructive actions!!
    header = EXPECTED_MINT_CSV_HEADERS.copy()

    if 'ModifyDebitAmounts' in actions:
        for transaction in transactions:
            if transaction['Transaction Type'] == 'debit':
                transaction['Amount'] = '-' + transaction['Amount']

    if 'RemoveTransType' in actions:
        for transaction in transactions:
            del transaction['Transaction Type']
        header.remove('Transaction Type')

    write_csv(output_file, header, not 'StripHeaders' in actions, transactions, verbose)

''' Validate the Mintness of a set of CSV rows '''
def validate_mint_csv_contents(transactions, verbose):
    row_num = 1
    for transaction in transactions:
        row_num = row_num + 1
        if len(transaction) != len(EXPECTED_MINT_CSV_HEADERS):
            print_error_and_quit('Invalid Mint CSV file contents: row ' + str(row_num) + ' doesn\'t have the correct number of columns')

''' Validate a Mint CSV file '''
def validate_mint_csv(input_file, verbose):
    if verbose:
        print('Validating Mint CSV file: ' + input_file)

    transactions = read_mint_csv(input_file, verbose)
    validate_mint_csv_contents(transactions, verbose)

''' Validate a directory of Mint CSV files '''
def validate_mint_csvs(input_dir, verbose):
    if verbose:
        print('Validating Mint CSV files in directory: ' + input_dir)

    for file in os.listdir(input_dir):
        if file.endswith('.csv'):
            validate_mint_csv(os.path.join(input_dir, file), verbose)


''' Main entry point '''
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Mint Migration Helpers')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')
    parser.add_argument('-i', '--input', type=str, action='store', help='Input file', required=True)
    parser.add_argument('-o', '--output', type=str, action='store', help='Output file', required=True)
    parser.add_argument('-a', '--actions', type=str, action='store', metavar=SUPPORTED_ACTIONS, help='Action to perform', required=True)
    parser.add_argument('-f', '--force', action='store_true', help='Force convert when input and output are the same')
    parser.add_argument('--atomic', action='store_true', help='Only perform action if all actions can be performed')

    args = parser.parse_args()

    # Validate that the input file/dir exists
    if not os.path.exists(args.input):
        print_error_and_quit('Input file or directory does not exist')
    elif args.atomic:
        if os.path.isdir(args.input):
            validate_mint_csvs(args.input, args.verbose)
        else:
            validate_mint_csv(args.input, args.verbose)

    if os.path.isdir(args.input) and not os.path.exists(args.output):
        # Create directory if we are converting a directory
        os.makedirs(args.output)
    elif args.atomic:
        if os.path.isdir(args.output):
            validate_mint_csvs(args.output, args.verbose)
        else:
            validate_mint_csv(args.output, args.verbose)

    if args.input == args.output and not args.force:
        print_error_and_quit('Input and output files are the same. Use -f to force conversion')

    # Convert actions to an array of actions separated by commas then validate
    if args.actions is not None:
        args.actions = [s.strip() for s in args.actions.split(",")]
        for action in args.actions:
            if action not in SUPPORTED_ACTIONS:
                print_error_and_quit('Unsupported action: ' + action)
    else:
        print_error_and_quit('No actions specified')

    # If we got this far then we can start performing our actions
    if args.verbose:
        print('Input file: ' + args.input)
        print('Output file: ' + args.output)
        if len(args.actions) > 1:
            print('Actions: ' + str(args.actions))
        else:
            print('Action: ' + args.action)

    if os.path.isdir(args.input):
        for file in os.listdir(args.input):
            if file.endswith('.csv'):
                convert_mint_csv(os.path.join(args.input, file), os.path.join(args.output, file), args.actions, args.verbose)
    else:
        convert_mint_csv(args.input, args.output, args.actions, args.verbose)
