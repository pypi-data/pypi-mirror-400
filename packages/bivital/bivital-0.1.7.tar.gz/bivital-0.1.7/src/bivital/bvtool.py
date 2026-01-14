from bivital import pipeline as bvp
from bivital import monitor as bvm
from bivital import firmware as bvf
from bivital import storage as bvs 
import argparse
import sys

def main():
    parser = argparse.ArgumentParser(description="Main parser with subcommands")
    subparsers = parser.add_subparsers(dest="subcommand", help="sub-command help --> type <argument> -h/--help")

    # Project parser
    project_parser = subparsers.add_parser("project", help="Project help")
    project_parser.add_argument("-p", "--path", help="type the path, Default: choose from file explorer")
    project_parser.add_argument("-n", "--name", help="the name of the Project or Series")

    # Series parser
    series_parser = subparsers.add_parser("series", help="Series help")
    series_parser.add_argument("-p", "--path", help="type the path, Default: choose from file explorer")
    series_parser.add_argument("-n", "--name", help="the name of the Project or Series")

    # Data parser
    data_parser = subparsers.add_parser("data", help="Data help")
    data_parser.add_argument("-p", "--path", help="type the path, Default: choose from file explorer")
    data_parser.add_argument("-s", "--source", help="PC or BiVital as Data sources, Default: ask for source",
                             choices=['pc', 'bivital'], type=str.casefold)

    # Label parser
    label_parser = subparsers.add_parser("label", help="Label help")
    label_parser.add_argument("-p", "--path", help="type the path, Default: choose from file explorer")

    # Example parser
    subparsers.add_parser("example", help="Example help")

    # Monitor parser
    subparsers.add_parser("monitor", help="Start serial monitor (see 'bvtool monitor --help')", add_help=False)

    # Firmware parser
    subparsers.add_parser("firmware", help="Firmware help", add_help=False)

    # Storage parser
    subparsers.add_parser("storage", help="Storage help", add_help=False)

    if len(sys.argv) > 1:
        sys.argv[1] = sys.argv[1].casefold()

    args, unknown = parser.parse_known_args()

    if args.subcommand == "project":
        bvp.BiVital_DataPipeline().createProject(path=args.path, name=args.name)

    elif args.subcommand == "series":
        bvp.BiVital_DataPipeline().add_measurement_series(path=args.path, name=args.name)

    elif args.subcommand == "data":
        bvp.BiVital_DataPipeline().add_data(path=args.path, source=args.source)

    elif args.subcommand == "label":
        bvp.BiVital_DataPipeline().add_label(path=args.path)

    elif args.subcommand == "example":
        bvp.BiVital_DataPipeline().open_example()

    elif args.subcommand == "monitor":
        bvm.main(unknown)

    elif args.subcommand == "firmware":
        bvf.main(unknown)

    elif args.subcommand == "storage":
        bvs.main(unknown)
    
if __name__ == "__main__":
    main()

