# -*- coding: utf-8 -*-
import argparse
import logging
import time
import sys

from chibi.config import basic_config, load as load_config
from chibi.config import default_file_load, configuration
from chibi.file import Chibi_path

from bid_stalker import bidspotter

from elasticsearch_dsl.connections import connections
from chibi_elasticsearch.config import review_elasticsearch_config
from chibi_elasticsearch.snippet import (
    index_exists, create_index_if_not_exists )


logger = logging.getLogger( "bid_stalker.cli" )


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
    "--pk", dest='pk', required=False,
    help="pk de elasticsearch de la subasta" )

facebook_scan_subparser = scan_parser.add_subparsers(
    dest="command_facebook", help="escanea los items de facebook" )
facebook_scan_parser = facebook_scan_subparser.add_parser(
    "facebook", help="escanea los articulos de marketplace" )

facebook_scan_parser.add_argument(
    "--user", '-u', metavar="user",
    help="nombre de usuario o email de facebook" )

facebook_scan_parser.add_argument(
    "--password", '-p', metavar="password",
    help="nombre de usuario o email de facebook" )

facebook_scan_parser.add_argument(
    "--download_folder", '-d', dest="download_folder", required=True,
    type=Chibi_path, help="directorio de descarga para de las imagenes", )

facebook_scan_parser.add_argument(
    "--name", dest="query_name", required=True,
    type=Chibi_path, help="filtro de query para el nombre del item", )

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

parser_facebook = sub_parsers.add_parser(
    'facebook',
    help=(
        'facebook, si no se manda una categoria imprimira la lista '
        'las categorias disponibles'
    ), )


parser_facebook.add_argument(
    "category", nargs="?", metavar="category",
    help="categoria que se escaneara" )

parser_facebook.add_argument(
    "--user", '-u', metavar="user",
    help="nombre de usuario o email de facebook" )

parser_facebook.add_argument(
    "--password", '-p', metavar="password",
    help="nombre de usuario o email de facebook" )


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
    if args.command == 'facebook':
        from bid_stalker.site.facebook import marketplace
        from bid_stalker.site.facebook.elastic import Item as Facebook_item
        if args.category:
            category = args.category
            if category not in marketplace.categories:
                raise NotImplementedError(
                    'categoria: "{category}" no encontrada' )
            user = args.user
            password = args.password
            marketplace.login( user, password )
            time.sleep( 1 )
            marketplace.get()
            marketplace.categories[ category ].click()
            for i in range( 50 ):
                sleep = 30
                logger.info( f"obteniendo pagina {i} de 50" )
                logger.info( f"sleep de {sleep}" )
                time.sleep( 30 )
                for item_raw in marketplace.items:
                    item = Facebook_item( **item_raw )
                    item.category = category
                    item.save_if_not_exists()
                marketplace.press_key.end()

        else:
            print( "categorias" )
            for c in marketplace.categories:
                print( f"\t{c}" )

    elif args.command == 'elastic':
        from bid_stalker.site.bidspotter.elastic import Audiction
        from bid_stalker.site.bidspotter.elastic import Article
        from bid_stalker.site.facebook.elastic import Item as Facebook_item
        from elasticsearch_dsl import Q
        if args.command_elastic == 'create':
            create_index_if_not_exists( Audiction )
            create_index_if_not_exists( Article )
            create_index_if_not_exists( Facebook_item )
            review_elasticsearch_config()
        elif args.command_elastic == 'list':
            print( "bidspotter" )
            for audiction in Audiction.search().scan():
                print( f"\tpk:   {audiction.pk}" )
                print( f"\tname: {audiction.name}" )
                print( f"\turl:  {audiction.url}" )
                print( f"\tarticles:  {audiction.articles.count()}" )
                print()
            print( "facebook" )
            total_items = Facebook_item.search().count()
            items_with_detail = Facebook_item.Q.with_details().count()
            print(
                "\titems con detalles: "
                f"{items_with_detail} / {total_items}" )
        elif args.command_elastic == 'scan':
            if args.command_facebook:
                from bid_stalker.site.facebook import marketplace
                download_folder = args.download_folder
                if not download_folder.exists:
                    raise NotImplementedError(
                        "no implementado is no existe la carpeta de descarga" )
                missings = args.missing
                if missings:
                    search = Facebook_item.Q.with_no_details()
                    search = Facebook_item.Q.not_unavailable_product(
                        search=search )
                else:
                    raise NotImplementedError
                    search = Facebook_item.Q.with_details()

                if args.query_name:
                    search = search.query(
                        Q( "match", name=args.query_name ) )

                print( search.to_dict() )
                user = args.user
                password = args.password
                marketplace.login( user, password )
                for item in search.scan():
                    item.read_item_from_source(
                        marketplace, download_folder=download_folder )

                print( "facebook" )
            else:
                audiction_model = Audiction.get( id=args.pk )
                #bidspotter.prepare_session()
                audiction = audiction_model.site
                #audiction.session = bidspotter.session

                audiction.prepare_session()

                time.sleep( 10 )
                for article in audiction.articles:
                    if args.missing:
                        try:
                            if Article.Q.url_exists( str( article ) ):
                                logger.info( f"se salta el articulo: {article}" )
                                continue
                        except Exception as e:
                            import pdb
                            pdb.set_trace()
                            raise
                    else:
                        raise NotImplementedError(
                            "no implementado escaneo completo" )
                    article_model = article.to_es()
                    article_model.catalog.pk = audiction_model.pk
                    article_model.save_if_not_exists()
                    time.sleep( 10 )
        else:
            review_elasticsearch_config()
            print( f"bidspotter.Audiction.exists: {index_exists( Audiction )}" )
            print( f"bidspotter.Article.exists: {index_exists( Article )}" )
            print(
                f"bidspotter.Article.exists: {index_exists( Facebook_item )}" )
    else:
        raise NotImplementedError(
            "no esta implementada la opcion de '{args.command}'" )
    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
