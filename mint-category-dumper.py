import argparse
import os
import csv
from financetools import helpers, mint


def accumulate_categories_from_csv(categories, input_file):
    if not os.path.exists(input_file):
        helpers.print_error_and_quit('Input file does not exist')

    transactions = mint.read_mint_csv(input_file, False)

    for transaction in transactions:
        if transaction['Category'] is not None:
            categories.add(transaction['Category'])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Mint Category Dumper')
    parser.add_argument('-i', '--input', type=str, action='store', help='Input file', required=True)

    args = parser.parse_args()

    # Validate that the input file/dir exists
    if not os.path.exists(args.input):
        helpers.print_error_and_quit('Input file or directory does not exist')

    categories = set()
    if os.path.isdir(args.input):
        for file in os.listdir(args.input):
            if file.endswith('.csv'):
                accumulate_categories_from_csv(categories, os.path.join(args.input, file))
    else:
        accumulate_categories_from_csv(categories, args.input)

    # Print out the categories
    for category in sorted(categories):
        print(category)