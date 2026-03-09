import logging
import json
from chibi_atlas import Chibi_atlas
from chibi_browser import Chibi_browser, wait_conditions
from chibi_site import Chibi_site
from bid_stalker.site.bidspotter.serializers import (
    Audiction as Audiction_serializer,
    Article as Article_serializer,
)
from bid_stalker.site.bidspotter.elastic import (
    Audiction as Audiction_model,
    Article as Article_model,
)

from bid_stalker.site.bidspotter.snippets import (
    parse_script_to_article
)
import requests
import time


logger = logging.getLogger( "chibi_stalker.bidspotter" )


class Bidspotter( Chibi_site ):
    default_user_agent = (
        'Mozilla/5.0 (Windows NT 6.1; WOW64) '
        'AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/56.0.2924.87 Safari/537.36'
    )
    def __new__( cls, *args, **kw ):
        instance = super().__new__( cls, *args, **kw )
        if not instance.session:
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

    def prepare_session( self ):
        logger.info( "abriendo navegado para obtener las cookies" )
        if not self.cookies:
            browser = Chibi_browser( self )
            browser.wait().until( wait_conditions.document.ready )
            self.cookies = browser.cookies
            self.user_agent = browser.user_agent
            browser.close()
        else:
            logger.warning( "la session ya tenia cookies" )

    @property
    def auction( self ):
        result = Catalog( self + '/en-us/auction-catalogues', **self.kw )
        return result

    def get( self, *args, **kw ):
        return super().get( *args, timeout=5, **kw )


class Catalog( Chibi_site ):
    @property
    def current_page( self ):
        pages = self.soup.select_one(
            "div.pagination-pages ul.pagination-content" )
        current = int( pages.attrs[ 'data-current-page-number' ] )
        return current

    @property
    def total_pages( self ):
        pages = self.soup.select_one(
            "div.pagination-pages ul.pagination-content" )
        total = int( pages.attrs[ 'data-pages' ] )
        return total

    @property
    def next_page( self ):
        if self.current_page >= self.total_pages:
            return None
        return self + { 'page': self.current_page + 1 }

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
        article_container = self.soup.select_one(
            'div.auction-listing-results' )
        articles = article_container.select(
            'div.auction-summary-standard script' )
        for article in articles:
            article_data = Chibi_atlas( json.loads( article.text ) )
            article = Audiction(
                article_data.url, parent=self, article_data=article_data,
                **self.kw )
            yield article
        if self.next_page is not None:
            yield from self.next_page.articles

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

    def __new__( cls, *args, **kw ):
        instance = super().__new__( cls, *args, **kw )
        if not instance.session:
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

    def prepare_session( self ):
        logger.info( "abriendo navegado para obtener las cookies" )
        if not self.cookies:
            browser = Chibi_browser( self )
            browser.wait().until( wait_conditions.document.ready )
            time.sleep( 10 )
            """
            input(
                "preciona enter cuando termines de resolver "
                "el estupido captcha" )
            """
            self.cookies = browser.cookies
            self.user_agent = browser.user_agent
            browser.close()
        else:
            logger.warning( "la session ya tenia cookies" )

    @property
    def current_page( self ):
        pages = self.soup.select_one(
            "div.pagination-pages ul.pagination-content" )
        current = int( pages.attrs[ 'data-current-page-number' ] )
        return current

    @property
    def total_pages( self ):
        pages = self.soup.select_one(
            "div.pagination-pages ul.pagination-content" )
        total = int( pages.attrs[ 'data-pages' ] )
        return total

    @property
    def next_page( self ):
        if self.current_page >= self.total_pages:
            return None
        result = self + { 'page': self.current_page + 1 }
        return result


    def to_dict( self ):
        serializer = Audiction_serializer()
        parse = serializer.load( self.kw.article_data, many=False )
        result = Chibi_atlas( parse )
        return result

    def to_es( self ):
        return Audiction_model( **self.to_dict() )

    @property
    def articles( self ):
        try:
            scripts = self.soup.select(
                "div.lot-listing-results div#results script" )
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 202:
                self.cookies = {}
                self.prepare_session()
            else:
                import pdb
                pdb.set_trace()
                raise
        scripts = self.soup.select(
            "div.lot-listing-results div#results script" )
        scripts = list( script for script in scripts if 'src' not in script )

        articles_link = self.soup.select(
            'div.lot-listing-results article div.main '
            'div.lot-header-grid-only a' )
        for link in articles_link:
            yield Article( self + link.attrs.href )
        if self.next_page is not None:
            yield from self.next_page.articles


class Article( Chibi_site ):

    @property
    def info( self ):
        result = Chibi_atlas()
        main = self.soup.select_one( 'main' )
        containers = main.select( 'div.ui.container' )
        if not containers:
            import pdb
            pdb.set_trace()
            raise NotImplementedError(
                f"no se encontraron los containers en el articulo {self}" )
        header = containers[0]
        result.lot = Chibi_atlas()
        result.lot.number = header.select_one( "p.lot-number" ).text.strip()
        result.lot.kind = header.select_one( "p.lot" ).text.lower().strip()
        body = containers[-1]
        tabs = body.select_one( 'div.tabs-wrapper div.ui[role=tablist] a' )
        result.tabs = [ tab.text.strip() for tab in tabs ]
        panels = body.select( 'div.tabs-wrapper div.ui[role=tabpanel]' )
        result.info = Chibi_atlas()
        for panel in panels:
            key = panel.attrs[ 'data-tab' ].strip()
            result.info[ key ] = panel.text.strip()

        images_html = main.select(
            'div.lot-details-image.slider div.image img' )
        images = []
        for src in images_html:
            images.append(
                src.attrs.get( 'src', src.attrs.get( 'data-lazy' ) ) )
        result.images = images
        tags = self.soup.select( 'div.seo-tags div.content span' )
        tags = map( lambda x: x.text, tags )
        tags = map( str.strip, tags )
        result.tags = set( tags )
        result.name = header.select( "h1.header" )[0].text
        result.catalog = Chibi_atlas()
        result.catalog.url = header.select_one( "p.description a" ).attrs.href
        result.catalog.url = self + result.catalog.url
        result.catalog.name = header.select_one(
            "p.description a" ).text.strip()
        right_data = self.soup.select(
            "div.ui.container div.row div.six.wide.column "
            "div.ui.basic.segment" )[2]
        result.audiction_date = right_data.select_one(
            "div.Rtable-cell--row span time" ).attrs.datetime
        others = right_data.select( 'div.Rtable-cell--row' )
        for other in others:
            label = other.select_one( 'label' ).text.strip().lower()
            if 'auction date' in label:
                continue
            value = other.select_one( 'strong' ).text.strip()
            label = label.replace( ' ', "_" )
            label = label.replace( ':', "" )
            label = label.replace( "'", "" )
            result[ label ] = value

        right_data = self.soup.select(
            "div.ui.container div.row div.six.wide.column "
            "div.ui.basic.segment" )[3]
        auctioneer = right_data.select(
            "div.Rtable-cell--row div.Rtable-cell" )[2]
        auctioneer_link = auctioneer.select_one( "p a" )
        result.auctioneer = Chibi_atlas()
        result.auctioneer.name = auctioneer_link.text
        result.auctioneer.url = self + auctioneer_link.attrs.href
        result.url = self
        return result

    def to_dict( self ):
        serializer = Article_serializer()
        info = self.info
        parse = serializer.load( info, many=False )
        result = Chibi_atlas( parse )
        return result

    def to_es( self ):
        data = self.to_dict()
        return Article_model( **data )


bidspotter = Bidspotter( 'https://www.bidspotter.com/' )
bidspotter_auctions = bidspotter + ( 'en-us/auction-catalogues' )
