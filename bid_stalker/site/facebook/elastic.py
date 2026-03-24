import datetime
from chibi_hybrid import Class_property
from chibi_django.snippet.elasticsearch import build_index_name
from chibi_django.snippet.elasticsearch import (
    name as name_analizer,
    name_space )
from elasticsearch_dsl import field, InnerDoc, Q
from chibi_elasticsearch.models import Chibi_model
from chibi_elasticsearch.snippet import build_index_name
from bid_stalker.site.facebook import marketplace
from chibi.file.temp import Chibi_temp_path
from chibi_requests import Chibi_url
import requests


class Profile( InnerDoc ):
    url = field.Keyword()
    name = field.Text(
        analyzer=name_analizer,
        fields={
            'space': field.Text( analyzer=name_space, ),
        } )
    pk = field.Keyword()


class Item( Chibi_model ):
    url = field.Keyword()
    name = field.Text(
        analyzer=name_analizer,
        fields={
            'space': field.Text( analyzer=name_space, ),
            'keyword': field.Keyword(),
        } )

    images_url = field.Keyword( multi=True )
    string_price = field.Keyword()
    price = field.Float()
    place = field.Text(
        analyzer=name_analizer,
        fields={
            'space': field.Text( analyzer=name_space, ),
            'keyword': field.Keyword(),
        } )

    publish_date_relative = field.Keyword()
    scan_date = field.Date()
    details = field.Text(
        analyzer=name_analizer,
        fields={
            'space': field.Text( analyzer=name_space, ),
        } )
    profile = field.Object( Profile )
    unavailable_product = field.Boolean()
    date_unavailable_product = field.Date()
    category = field.Keyword()
    currency = field.Keyword()

    class Index:
        name = build_index_name(
            'facebook__item', app_name='bid_stalker' )
        settings = { 'number_of_shards': 1, 'number_of_replicas': 1 }

    def read_item_from_source( self, browser, download_folder=None ):
        marketplace.go_to_item( self )
        result = marketplace.get_item_info( self )
        if result.unavailable_product:
            self.unavailable_product = result.unavailable_product
            self.date_unavailable_product = result.date_unavailable_product
            self.save()
        else:
            self.images_url = result.images_url
            self.publish_date_relative = result.publish_date_relative
            self.scan_date = datetime.datetime.now( tz=datetime.UTC )
            self.details = result.details
            self.profile = result.profile
            self.unavailable_product = result.unavailable_product
            self.save()
            self.download_images( browser, download_folder )
            self.save()

    def download_images( self, browser, download_folder=None ):
        if download_folder is None:
            download_folder = Chibi_temp_path( delete_on_del=False )
        new_images = []
        name = self.name.replace( " ", "_" )
        session = requests.session()
        session.headers[ 'User-Agent' ] = browser.user_agent

        cookies = {
            cookie[ 'name' ]: cookie[ 'value' ]
            for cookie in browser.cookies }
        session.cookies.clear()
        for k, v in cookies.items():
            session.cookies.set( k, v )

        for i, url in enumerate( self.images_url ):
            url = Chibi_url( url )
            url.session = session
            path = url.download( download_folder )
            extencion = path.extension
            new_path = (
                download_folder + f"{name}__{i}__{self.pk}.{extencion}" )
            path.move( new_path )
            new_images.append( path )

        self.images_url = new_images
        self.save()

    def save_if_not_exists( self ):
        if not type( self ).Q.url_exists( self.url ):
            self.save()

    def convert_price( self ):
        if '$' in self.string_price:
            currency, price = self.string_price.split( '$', 1 )
            self.currency = currency
            try:
                big, small = price.rsplit( '.', 1 )
            except ValueError:
                big = price
                small = 0
            big = big.replace( '.', '' )
            self.price = float( f"{big}.{small}" )
        elif "gratis" in self.string_price.lower():
            self.price = 0
        else:
            raise NotImplementedError(
                f"no se implemento el parseo con '{self.string_price}'" )

    class Q:
        @Class_property
        def model( cls ):
            return Item

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

        @classmethod
        def with_details( cls, search=None ):
            if search is None:
                search = cls.model.search()
            search = search.filter( Q( "exists", field="details" ) )
            return search

        @classmethod
        def with_no_details( cls, search=None ):
            if search is None:
                search = cls.model.search()
            search = search.filter( ~Q( "exists", field="details" ) )
            return search

        @classmethod
        def not_unavailable_product( cls, search=None ):
            if search is None:
                search = cls.model.search()
            q = (
                Q( "term", unavailable_product=False )
                | ~Q( "exists", field='unavailable_product' )
            )
            search = search.filter( q )
            return search

