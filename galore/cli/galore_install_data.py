from argparse import ArgumentParser
import galore.cross_sections

def main():
    parser = get_parser()
    args = parser.parse_args()
    args = vars(args)
    run(**args)

def get_parser():
    parser = ArgumentParser()
    parser.add_argument('reference', type=str,
                        help=""" 'Scofield' or 'Yeh'""")
   
    return parser

def run(reference):
    if reference == 'Scofield' or reference == 'Yeh':

        url,data_file_dir,data_file_path =galore.cross_sections.get_csv_file_path(reference)
        galore.cross_sections.galore_install_data(url,data_file_dir,data_file_path)
    
    else:
        print("You can enter reference 'Scofield' or 'Yeh' ")
  