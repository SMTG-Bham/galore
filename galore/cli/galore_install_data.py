import logging
from argparse import ArgumentParser
import galore.cross_sections


def main():
    parser = get_parser()
    args = parser.parse_args()
    args = vars(args)
    run(**args)


def get_parser():
    parser = ArgumentParser()
    parser.add_argument('dataset', type=str.lower, choices= ['scofield','yeh'],
                        help=""" Accepted values are 'Scofield' and 'Yeh'""")

    return parser


def run(dataset):
    if dataset.lower() == 'scofield' or dataset.lower() == 'yeh':

        url, data_file_dir, data_file_path = galore.cross_sections.get_csv_file_path(
            dataset)
        galore.cross_sections.galore_install_data(
            url, data_file_dir, data_file_path)

    else:
        print("Dataset '{dataset}' was not recognised. Accepted values are 'Scofield' and 'Yeh'.".format(dataset = dataset))
       
