def print_error_and_quit(message):
    ''' Print an error message and exit the program '''
    print(message)
    exit(1)


def write_csv(output_file, header, write_header, transactions, verbose):
    if verbose:
        print('Writing CSV file: ' + output_file)

    import csv
    with open(output_file, 'w', newline='') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=header)
        if write_header is not False:
            writer.writeheader()
        for transaction in transactions:
            writer.writerow(transaction)

def read_category_remap_csv(input_file):
    ''' Read the category remap file and return a dictionary of mappings '''
    import csv
    category_remap = {}
    with open(input_file, 'r') as csv_file:
        reader = csv.DictReader(csv_file, fieldnames=['Mint Category', 'New Category'])
        for row in reader:
            category_remap[row['Mint Category']] = row['New Category']
    return category_remap
