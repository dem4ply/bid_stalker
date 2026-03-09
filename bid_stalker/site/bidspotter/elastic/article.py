from chibi_hybrid import Class_property
from chibi_django.snippet.elasticsearch import build_index_name
from chibi_django.snippet.elasticsearch import (
    name as name_analizer,
    name_space )
from elasticsearch_dsl import field, InnerDoc
from chibi_elasticsearch.models import Chibi_model
from chibi_elasticsearch.snippet import build_index_name


class Info( InnerDoc ):
    description = field.Text(
        analyzer=name_analizer,
        fields={
            'space': field.Text( analyzer=name_space ),
        } )
    auction = field.Text(
        analyzer=name_analizer,
        fields={
            'space': field.Text( analyzer=name_space ),
        } )
    shipping = field.Text(
        analyzer=name_analizer,
        fields={
            'space': field.Text( analyzer=name_space, ),
        } )
    terms = field.Text(
        analyzer=name_analizer,
        fields={
            'space': field.Text( analyzer=name_space, ),
        } )


class Catalog( InnerDoc ):
    name = field.Text(
        analyzer=name_analizer,
        fields={
            'space': field.Text( analyzer=name_space ),
        } )
    pk = field.Keyword()


class Auctioneer( InnerDoc ):
    name = field.Text(
        analyzer=name_analizer,
        fields={
            'space': field.Text( analyzer=name_space ),
        } )
    url = field.Keyword()


class Article( Chibi_model ):
    url = field.Keyword()
    name = field.Text(
        analyzer=name_analizer,
        fields={
            'space': field.Text( analyzer=name_space, ),
            'keyword': field.Keyword(),
        } )
    info = field.Object( Info )
    catalog = field.Object( Catalog )
    tags = field.Keyword( multi=True )
    audition_date = field.Date()
    auctioneer = field.Object( Auctioneer )

    class Index:
        name = build_index_name(
            'bidspotter__article', app_name='bid_stalker' )
        settings = { 'number_of_shards': 1, 'number_of_replicas': 1 }

    def save_if_not_exists( self ):
        if not type( self ).Q.url_exists( self.url ):
            self.save()

    class Q:
        @Class_property
        def model( cls ):
            return Article

        @classmethod
        def url( cls, url, search=None ):
            if search is None:
                search = cls.model.search()

            search = search.filter( 'term', url=url )
            return search

        @classmethod
        def catalog_pk( cls, pk, search=None ):
            if search is None:
                search = cls.model.search()

            search = search.filter( 'term', catalog__pk=pk )
            return search

        @classmethod
        def url_exists( cls, url, search=None ):
            search = cls.url( url, search=search )
            return search.count() > 0
