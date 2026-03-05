# -*- coding: utf-8 -*-
import argparse
import sys

from chibi.config import basic_config, load as load_config
from chibi.config import default_file_load, configuration

from bid_stalker import bidspotter

from elasticsearch_dsl.connections import connections
from chibi_elasticsearch.config import review_elasticsearch_config
from chibi_elasticsearch.snippet import (
    index_exists, create_index_if_not_exists )


default_file_load( 'bid_stalker.py', touch=False )
parser = argparse.ArgumentParser(
    description="Scrapper for bids online", fromfile_prefix_chars='@'
)


"""
parser.add_argument(
    "params", nargs='*', metavar="params",
    help="argumentos de cli" )
"""

parser.add_argument(
    "--log_level", dest="log_level", default="INFO",
    help="nivel de log", )

sub_parsers = parser.add_subparsers(
    dest='command', help='sub-command help' )


parser_elastic = sub_parsers.add_parser(
    'elastic',
    help=(
        'revisa la conecion con elasticsearch'
    ), )

sub_elastic_parser = parser_elastic.add_subparsers(
    dest='command_elastic', help='sub-command para elastic' )

sub_elastic_parser.add_parser( "create", help="crea los indices faltantes" )
sub_elastic_parser.add_parser( "list", help="lista las subastas" )

scan_parser = sub_elastic_parser.add_parser(
    "scan", help="escanea los articulos de la subasta" )
scan_parser.add_argument(
    "--missing", dest="missing", action="store_true",
    help="escanea solo los articulos faltantes"
)
scan_parser.add_argument(
    "--pk", dest='pk',
    help="pk de elasticsearch de la subasta" )

parser_bidspotter = sub_parsers.add_parser(
    'bidspotter',
    help=(
        'bidspotter, si no se manda un pais imprimira la lista de paises '
        'disponibles'
    ), )


parser_bidspotter.add_argument(
    "--to_elastic", dest="to_elastic", action="store_true",
    help="define si envia los resultados a elasticsearch"
)

parser_bidspotter.add_argument(
    "country", nargs="?", metavar="country",
    help="nombre del pais a usar" )


def main():
    """Console script for bid_stalker."""
    args = parser.parse_args()
    basic_config( args.log_level )

    if args.command == 'bidspotter':
        bidspotter.prepare_session()
        if args.country is None:
            for country, url in bidspotter.auction.countries.items():
                print( country )
                print( f"\t{url}" )
        else:
            audiction = bidspotter.auction.countries[ args.country ]
            for article in audiction.articles:
                data = article.to_dict()
                if args.to_elastic:
                    model = article.to_es()
                    model.save_if_not_exists()
                print( data.name )
                print( f"\turl: {article}" )
                try:
                    print( f"\tdescription: {data.description}" )
                except AttributeError:
                    print( "\tdescription: " )
                    # no  tiene descripcion
                    pass
                print( "" )

    elif args.command == 'elastic':
        from bid_stalker.site.bidspotter.elastic import Audiction
        from bid_stalker.site.bidspotter.elastic import Article
        if args.command_elastic == 'create':
            create_index_if_not_exists( Audiction )
            review_elasticsearch_config()
        elif args.command_elastic == 'list':
            print( "bidspotter" )
            for audiction in Audiction.search().scan():
                print( f"\tpk:   {audiction.pk}" )
                print( f"\tname: {audiction.name}" )
                print( f"\turl:  {audiction.url}" )
                print()
            create_index_if_not_exists( Audiction )
            review_elasticsearch_config()
        elif args.command_elastic == 'scan':
            audiction = Audiction.get( id=args.pk )
            for article in audiction.articles:
                article_model = article.to_es()
                if args.missing:
                    Article.save_if_not_exists()
                else:
                    raise NotImplementedError(
                        "no implementado escaneo completo" )
            print( args.pk )
            print( "scan" )
        else:
            review_elasticsearch_config()
        print( f"bidspotter.Audiction.exists: {index_exists( Audiction )}" )
    else:
        raise NotImplementedError(
            "no esta implementada la opcion de '{args.command}'" )
    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
