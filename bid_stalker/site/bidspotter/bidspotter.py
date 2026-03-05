import logging
import json
from chibi_atlas import Chibi_atlas
from chibi_browser import Chibi_browser, wait_conditions
from chibi_site import Chibi_site
from bid_stalker.site.bidspotter.serializers import (
    Audiction as Audiction_serializer
)
from bid_stalker.site.bidspotter.elastic import (
    Audiction as Audiction_model
)
import requests


logger = logging.getLogger( "chibi_stalker.bidspotter" )


class Bidspotter( Chibi_site ):
    default_user_agent = (
        'Mozilla/5.0 (Windows NT 6.1; WOW64) '
        'AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/56.0.2924.87 Safari/537.36'
    )
    def __new__( cls, *args, **kw ):
        instance = super().__new__( cls, *args, **kw )
        instance.build_session()
        #instance.user_agent = Bidspotter.default_user_agent
        return instance

    def build_session( self ):
        self.session = requests.session()

    @property
    def user_agent( self ):
        return self.session.headers[ 'User-Agent' ]

    @user_agent.setter
    def user_agent( self, value ):
        self.session.headers[ 'User-Agent' ] = value

    @property
    def cookies( self ):
        return self.session.cookies

    @cookies.setter
    def cookies( self, value ):
        cookies = {
            cookie[ 'name' ]: cookie[ 'value' ] for cookie in value }
        self.session.cookies.clear()
        for k, v in cookies.items():
            self.session.cookies.set( k, v )

    @property
    def auction( self ):
        result = Catalog( self + '/en-us/auction-catalogues', **self.kw )
        return result

    def prepare_session( self ):
        if not self.cookies:
            browser = Chibi_browser( self )
            browser.wait().until( wait_conditions.document.ready )
            self.cookies = browser.cookies
            self.user_agent = browser.user_agent
            browser.close()
        else:
            logger.warning( "la session ya tenia cookies" )

    def get( self, *args, **kw ):
        return super().get( *args, timeout=5, **kw )


class Catalog( Chibi_site ):
    def _build_url( self, name, *args, **kw ):
        """
        """
        result = type( self )( self, parent=self, **kw ) + name
        self._build_url_set_auth( result )
        return result

    def get( self, *args, **kw ):
        return super().get( *args, timeout=5, **kw )

    @property
    def articles( self ):
        article_container = self.soup.select_one( 'div.auction-listing-results' )
        articles = article_container.select(
            'div.auction-summary-standard script' )
        for article in articles:
            article_data = Chibi_atlas( json.loads( article.text ) )
            article = Audiction(
                article_data.url, parent=self, article_data=article_data,
                **self.kw )
            yield article

    @property
    def countries( self ):
        countries = self.soup.select(
            '#FilteredSearch_countryName ul li a' )

        result = Chibi_atlas()
        for country in countries:
            country_name = country.text.split( '(', 1 )[0]
            link = self + country.attrs.href
            result[ country_name.lower().strip() ] = link
        return result


class Audiction( Chibi_site ):

    def to_dict( self ):
        serializer = Audiction_serializer()
        parse = serializer.load( self.kw.article_data, many=False )
        result = Chibi_atlas( parse )
        return result

    def to_es( self ):
        return Audiction_model( **self.to_dict() )

    def es_model( self ):
        s = Audiction_model.Q.url( self )
        import pdb
        pdb.set_trace()
        pass

    @property
    def articles( self ):
        import pdb
        pdb.set_trace()
        pass


bidspotter = Bidspotter( 'https://www.bidspotter.com/' )
bidspotter_auctions = bidspotter + ( 'en-us/auction-catalogues' )
