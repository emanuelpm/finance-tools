""" Helper program to convert Mint CSV files to the desired input formats for other programs """

import argparse
import os
from financetools import banktivity, helpers, mint


SUPPORTED_ACTIONS = [
    "StripHeaders",
    "ModifyDebitAmounts",
    "RemoveTransType"
]

SUPPORTED_PROFILES = [
    "Banktivity"
]


def convert_mint_csv_via_profile(input_file, output_file, profile, categories_file, verbose):
    ''' Convert a Mint CSV file to a specified profile's CSV '''

    # If the input is a directory, recurse for each file then return
    if os.path.isdir(input_file):
        if verbose:
            print('Converting Mint CSV files in directory: ' + input_file + ' to: ' + output_file)

        for file in os.listdir(input_file):
            if file.endswith('.csv'):
                convert_mint_csv_via_profile(os.path.join(input_file, file),
                                             os.path.join(output_file, file),
                                             profile,
                                             categories_file,
                                             verbose)
        return

    # We are processing a file
    if verbose:
        print('Converting Mint CSV file: ' + input_file + ' to: ' + output_file)
        print('Profile: ' + profile)

    transactions = mint.read_mint_csv(input_file, verbose)
    mint.validate_mint_csv_contents(transactions, verbose)

    # Python doesn't have constants so be sure to copy since we will perform destructive actions!!
    header = mint.MINT_CSV_HEADERS.copy()

    if profile == 'Banktivity':
        for transaction in transactions:
            if transaction['Transaction Type'] == 'debit':
                transaction['Amount'] = '-' + transaction['Amount']

        for transaction in transactions:
            del transaction['Transaction Type']

        header.remove('Transaction Type')
    else:
        helpers.print_error_and_quit('Unsupported profile: ' + profile)

    if categories_file is not None:
        if os.path.exists(categories_file):
            category_remap = helpers.read_category_remap_csv(categories_file)
            for transaction in transactions:
                if transaction['Category'] in category_remap:
                    transaction['Category'] = category_remap[transaction['Category']]
        else:
            helpers.print_error_and_quit('Categories file does not exist: ' + categories_file)

    helpers.write_csv(output_file, header, False, transactions, verbose)


def convert_mint_csv_via_actions(input_file, output_file, actions, categories_file, verbose):
    ''' Convert the CSV file by applying the actions then write it out'''
    # If the input is a directory, recurse for each file then return
    if os.path.isdir(input_file):
        if verbose:
            print('Converting Mint CSV files in directory: ' + input_file + ' to: ' + output_file)

        for file in os.listdir(input_file):
            if file.endswith('.csv'):
                convert_mint_csv_via_actions(os.path.join(input_file, file), os.path.join(output_file, file), actions,
                                             verbose)
        return

    # We are processing a file
    if verbose:
        print('Converting Mint CSV file: ' + input_file + ' to: ' + output_file)
        if len(actions) > 1:
            print('Actions: ' + str(actions))
        else:
            print('Action: ' + action)

    transactions = mint.read_mint_csv(input_file, verbose)
    mint.validate_mint_csv_contents(transactions, verbose)

    # Python doesn't have constants so be sure to copy since we will perform destructive actions!!
    header = mint.MINT_CSV_HEADERS.copy()

    if 'ModifyDebitAmounts' in actions:
        for transaction in transactions:
            if transaction['Transaction Type'] == 'debit':
                transaction['Amount'] = '-' + transaction['Amount']

    if 'RemoveTransType' in actions:
        for transaction in transactions:
            del transaction['Transaction Type']
        header.remove('Transaction Type')

    if categories_file is not None:
        if os.path.exists(categories_file):
            category_remap = helpers.read_category_remap_csv(categories_file)
            for transaction in transactions:
                if transaction['Category'] in category_remap:
                    transaction['Category'] = category_remap[transaction['Category']]
        else:
            helpers.print_error_and_quit('Categories file does not exist: ' + categories_file)

    helpers.write_csv(output_file, header, 'StripHeaders' not in actions, transactions, verbose)


if __name__ == '__main__':
    ''' Main entry point '''
    parser = argparse.ArgumentParser(description='Mint CSV Converter')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Verbose output')
    parser.add_argument('-i', '--input', type=str, action='store', required=True,
                        help='Input file')
    parser.add_argument('-o', '--output', type=str, action='store', required=True,
                        help='Output file')
    parser.add_argument('-p', '--profile', type=str, action='store', choices=SUPPORTED_PROFILES,
                        help='The application profile to export to')
    parser.add_argument('-c', '--categories', type=str, action='store',
                        help='CSV file containing mapping from Mint Categories to remapped Categories')
    parser.add_argument('-a', '--actions', type=str, action='store', metavar=SUPPORTED_ACTIONS,
                        help='[Legacy, use financetools if you can] Action to perform')
    parser.add_argument('-f', '--force', action='store_true',
                        help='Force convert when input and output are the same')
    parser.add_argument('--atomic', action='store_true',
                        help='Only perform action if all actions can be performed without error')

    args = parser.parse_args()

    # Validate that the input file/dir exists
    if not os.path.exists(args.input):
        helpers.print_error_and_quit('Input file or directory does not exist')
    elif args.atomic:
        if os.path.isdir(args.input):
            mint.validate_mint_csvs(args.input, args.verbose)
        else:
            mint.validate_mint_csv(args.input, args.verbose)

    if os.path.isdir(args.input) and not os.path.exists(args.output):
        # Create directory if we are converting a directory
        os.makedirs(args.output)
    elif args.atomic:
        if os.path.isdir(args.output):
            mint.validate_mint_csvs(args.output, args.verbose)
        else:
            mint.validate_mint_csv(args.output, args.verbose)

    if args.input == args.output and not args.force:
        helpers.print_error_and_quit('Input and output files are the same. Use -f to force conversion')

    if args.profile is not None:
        convert_mint_csv_via_profile(args.input,
                                     args.output,
                                     args.profile,
                                     args.categories,
                                     args.verbose)
    else:
        # Convert actions to an array of actions separated by commas then validate
        if args.actions is not None:
            args.actions = [s.strip() for s in args.actions.split(",")]
            for action in args.actions:
                if action not in SUPPORTED_ACTIONS:
                    helpers.print_error_and_quit('Unsupported action: ' + action)
        else:
            helpers.print_error_and_quit('No profile or actions specified')

        # If we got this far then we can start performing our actions
        convert_mint_csv_via_actions(args.input,
                                     args.output,
                                     args.actions,
                                     args.categories,
                                     args.verbose)
