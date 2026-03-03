# -*- coding: utf-8 -*-
import argparse
import sys

from chibi.config import basic_config, load as load_config
from chibi.config import default_file_load, configuration


default_file_load( 'bid_stalker.py', touch=False )
parser = argparse.ArgumentParser(
    description="Scrapper for bids online", fromfile_prefix_chars='@'
)

parser.add_argument(
    "params", nargs='+', metavar="params",
    help="argumentos de cli" )

parser.add_argument(
    "--log_level", dest="log_level", default="INFO",
    help="nivel de log", )


def main():
    """Console script for bid_stalker."""
    args = parser.parse_args()
    basic_config( args.log_level )

    for i, a in args.params:
        print( f"argumento {i}: {a}" )

    print( "Cambia este mensaje enbid_stalker.cli.main" )
    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
