import csv
import datetime as dt
import logging as logg

from prettytable import PrettyTable

from constants import BASE_DIR, DATETIME_FORMAT, PRETTY, FILE


def control_output(results, cli_args):
    OUTPUT_METHODS = {
        None: default_output,
        PRETTY: pretty_output,
        FILE: file_output
    }
    OUTPUT_METHODS[cli_args.output](results, cli_args)


def default_output(results, cli_args=None):
    for row in results:
        print(*row)


def pretty_output(results, cli_args=None):
    table = PrettyTable()
    table.align = 'l'
    table.field_names = results[0]
    table.add_rows(results[1:])
    print(table)


def file_output(results, cli_args):
    results_dir = BASE_DIR / 'results'
    results_dir.mkdir(exist_ok=True)
    parser_mode = cli_args.mode
    now = dt.datetime.now()
    now_formatted = now.strftime(DATETIME_FORMAT)
    file_name = f'{parser_mode}_{now_formatted}.csv'
    file_path = results_dir / file_name
    with open(file_path, 'w', encoding='utf-8') as file:
        writer = csv.writer(file, dialect='unix')
        writer.writerows(results)
    logg.info(f'Файл с результатами был сохранён в {file_path}')
