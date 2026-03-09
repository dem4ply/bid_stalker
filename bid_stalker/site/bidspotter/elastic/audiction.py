from chibi_hybrid import Class_property
from chibi_django.snippet.elasticsearch import build_index_name
from chibi_django.snippet.elasticsearch import (
    name as name_analizer,
    name_space )
from elasticsearch_dsl import field, InnerDoc
from chibi_elasticsearch.models import Chibi_model
from chibi_elasticsearch.snippet import build_index_name
from .article import Article


class Event( InnerDoc ):
    attendance_mode = field.Keyword()
    status = field.Keyword()


class Location( InnerDoc ):
    kind = field.Keyword()
    url = field.Keyword()


class Organizer( InnerDoc ):
    kind = field.Keyword()
    url = field.Keyword()
    name = field.Text(
        analyzer=name_analizer,
        fields={
            'space': field.Text( analyzer=name_space ),
            'keyword': field.Keyword(),
        } )


class Audiction( Chibi_model ):
    name = field.Text(
        analyzer=name_analizer,
        fields={
            'space': field.Text( analyzer=name_space ),
            'keyword': field.Keyword(),
        } )
    description = field.Text(
        analyzer=name_analizer,
        fields={
            'space': field.Text( analyzer=name_space, ),
        } )
    kind = field.Keyword()
    end_date = field.Date()
    start_date = field.Date()
    event = field.Object( Event )
    image_url = field.Keyword()
    location = field.Object( Location )
    organizer = field.Object( Organizer )
    url = field.Keyword()

    @property
    def site( self ):
        from bid_stalker.site.bidspotter.bidspotter import (
            Audiction as Audiction_site
        )
        return Audiction_site( self.url )

    @property
    def articles( self ):
        return Article.Q.catalog_pk( self.pk )

    class Index:
        name = build_index_name(
            'bidspotter__audiction', app_name='bid_stalker' )
        settings = { 'number_of_shards': 1, 'number_of_replicas': 1 }

    def save_if_not_exists( self ):
        if not type( self ).Q.url_exists( self.url ):
            self.save()

    class Q:
        @Class_property
        def model( cls ):
            return Audiction

        @classmethod
        def url( cls, url, search=None ):
            if search is None:
                search = cls.model.search()

            search = search.filter( 'term', url=url )
            return search

        @classmethod
        def url_exists( cls, url, search=None ):
            search = cls.url( url, search=search )
            return search.count() > 0
