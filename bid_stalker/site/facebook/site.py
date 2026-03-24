import datetime
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


logger = logging.getLogger( "chibi_stalker.facebook" )


class Facebook( Chibi_browser ):
    def login( self, email, password ):
        self.browser.get(
            "https://www.facebook.com/login/device-based/regular/login/" )
        time.sleep( 1 )
        login = None
        divs = self.select( 'div' )
        for div in divs:
            label = div.get_attribute( 'aria-label' )
            if label and label.lower().strip() == 'continuar':
                login = div
        if login:
            login.click()
            time.sleep( 1 )
            password_input = self.select_one( 'input[name="pass"]' )
            password_input.send_keys( password )
            login = None
            divs = self.select( 'div' )
            for div in divs:
                label = div.text
                if label and label.lower().strip() == 'iniciar sesión':
                    login = div
            if not login:
                import pdb
                pdb.set_trace()
                pass
        else:
            email_input = self.select_one( 'input[name="email"]' )
            password_input = self.select_one( 'input[name="pass"]' )
            #login = self.select( 'button[name="login"]' )
            login = None
            divs = self.select( 'div' )
            login = self.select_arial_label_one( 'div', "iniciar sesión" )
            if not login:
                login = self.select_one( 'button[name="login"]' )
                if not login:
                    import pdb
                    pdb.set_trace()
                    pass
            email_input.send_keys( email )
            password_input.send_keys( password )
            login.click()
        self.wait( 360 ).until(
            wait_conditions.driver.url.equal( "https://www.facebook.com/" ),
            message="esperando a que cambie a facebook.com",
        )

    def select_arial_label( self, select, text ):
        results = []
        divs = self.select( select )
        for div in divs:
            label = div.get_attribute( 'aria-label' )
            if label and label.lower().strip() == text:
                results.append( div )
        return results

    def select_arial_label_one( self, select, text ):
        for s in self.select_arial_label( select, text ):
            return s
        return None

    def select_text( self, select, text ):
        results = []
        divs = self.select( select )
        for div in divs:
            label = div.text
            if label and label.lower().strip() == text:
                results.append( div )
        return results

    def select_text_one( self, select, text ):
        for s in self.select_text( select, text ):
            return s
        return None

    @property
    def categories( self ):
        categories = self.select_arial_label_one( 'ul', 'categorías' )
        lis = categories.select( "li" )
        result = { li.text.lower().strip(): li for li in lis }
        return result

    @property
    def search_input( self ):
        return self.select_arial_label_one(
            'ul', 'buscar en marketplace' )

    @property
    def items_links( self ):
        links = self.soup.select( "a" )
        for link in links:
            if link.attrs.href.startswith( '/marketplace/item' ):
                yield link
                #yield Chibi_site( self + link.href )

    @property
    def items( self ):
        for item in self.items_links:
            link = Chibi_site( self + item.attrs.href )
            image = item.select_one( "img" )
            spans = item.select( "span" )

            texts = []
            for span in spans:
                text = span.text.strip()
                if text not in texts:
                    texts.append( text )

            if len( texts ) == 6:
                if texts[1] in texts[0] and texts[2] in texts[0]:
                    texts.pop(0)
                    texts.pop(1)
            elif len( texts ) == 5:
                if texts[1] in texts[0] and texts[2] in texts[0]:
                    texts.pop(0)
                    texts.pop(1)

            try:
                price, name, place = texts
            except:
                try:
                    price, name, place, trash = texts
                except:
                    import pdb
                    pdb.set_trace()
                    raise
            link_clean = link.url
            yield Chibi_atlas( {
                'url': link_clean,
                'images_url': [ image.attrs.src ],
                'string_price': price,
                'name': name,
                'place': place,
            } )

    def images_item( self, item ):
        images = marketplace.soup.select( "img" )
        name = item.name.lower()
        for img in images:
            try:
                alt = img.attrs.alt.lower().strip()
            except:
                alt = ""
            if name in alt:
                if "foto del producto" in alt:
                    yield img.attrs.src

    def click_ver_mas( self ):
        pass

    def get_detail_of_item( self, item ):
        divs = self.soup.select( "div.xod5an3" )
        found = False
        for div in divs:
            if "información sobre" in div.text.lower():
                if div.select( "svg" ):
                    for span in div.select( "span" ):
                        yield span.text.lower().strip()
                    found = True
            elif "descripción del vendedor" in div.text.lower():
                spans = div.select( "span" )
                for span in spans:
                    yield span.text.lower().strip()
                found = True
            if found:
                break
        if not found:
            select = (
                "div.x1n2onr6.x1ja2u2z.x9f619.x78zum5.xdt5ytf.x2lah0s"
                ".x193iq5w.xsag5q8.x1jx94hy span" )
            spans = self.soup.select( select )
            if not spans:
                import pdb
                pdb.set_trace()
                pass
            texts = []
            for span in spans:
                text = span.text.strip().lower()
                if text not in texts:
                    texts.append( text )
            if 'detalles' not in texts:
                found = False
                import pdb
                pdb.set_trace()
                found = False
            else:
                found = True
                yield from texts
        if not found:
            import pdb
            pdb.set_trace()
            pass

    def get_profile_info( self, item ):
        links = self.soup.select( "a" )
        for link in links:
            if link.attrs.href.startswith( '/marketplace/profile/' ):
                text = link.text.lower().strip()
                if 'detalles del vendedor' in text:
                    continue
                else:
                    url = Chibi_site( self + link.attrs.href )
                    name = link.text.strip().lower()
                    pk_profile = url.base_name
                    return {
                        'url': url.url,
                        'name': name,
                        'pk': pk_profile,
                    }
        import pdb
        pdb.set_trace()
        pass

    def go_to_item( self, item ):
        marketplace.browser.get( item.url )
        time.sleep( 10 )

    def get_item_info( self, item ):
        if 'unavailable_product' in self.browser.current_url:
            logger.info( "item: {item.name} no disponible" )
            result = Chibi_atlas()
            result.date_unavailable_product = datetime.datetime.now(
                tz=datetime.UTC )
            result.unavailable_product = True
        else:
            images_url = list( self.images_item( item ) )
            publish_relative = marketplace.soup.select_one( "abbr span" )
            if not publish_relative:
                logger.info( "no se encontro fecha de publicacion" )
                publish_relative = None
            else:
                publish_relative = publish_relative.text
                publish_relative.strip().lower()
            details = "\n".join( self.get_detail_of_item( item ) )
            result = Chibi_atlas()
            result.images_url = images_url
            result.publish_date_relative = publish_relative
            result.details = details
            result.profile = self.get_profile_info( item )
            result.unavailable_product = False

        return result




marketplace = Facebook( 'https://www.facebook.com/marketplace/' )
