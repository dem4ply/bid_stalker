#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
import unittest
import itertools
from vcr_unittest import VCRTestCase
from chibi.file.temp import Chibi_temp_path
from bid_stalker.site.bidspotter import bidspotter_auctions, bidspotter
from bid_stalker.site.bidspotter import Catalog
from bid_stalker.site.bidspotter.bidspotter import Article
from bid_stalker.site.bidspotter.elastic import Article as Article_model
from chibi_requests import status_code
from elasticsearch_dsl import Document
from chibi_elasticsearch.unittests.vcr import Chibi_elastic_vcr
from chibi.config import configuration
from bid_stalker.site.facebook import marketplace

import unittest
import itertools
from unittest.mock import patch
from vcr_unittest import VCRTestCase
from bid_stalker.site.bidspotter import bidspotter_auctions, bidspotter
from bid_stalker.site.bidspotter import Catalog
from chibi_requests import status_code
from elasticsearch_dsl import Document
from chibi.config import configuration
from bid_stalker.site.facebook.elastic import Item
from chibi_elasticsearch.config import review_elasticsearch_config
from chibi_elasticsearch.snippet import create_index_if_not_exists
from chibi_elasticsearch.unittests import patch_doc_save

from tests.test_site.bidspotter import Test_bidspotter_cookies
from chibi_elasticsearch.unittests.vcr import Chibi_elastic_vcr


@unittest.skip( "lenta y nesesta usuario" )
class Test_facebook( unittest.TestCase ):
    @classmethod
    def setUpClass( cls, ):
        super().setUpClass()
        configuration.elasticsearch.test_app = True
        Item._index._name = (
            "test__bid_stalker__facebook__item" )
        create_index_if_not_exists( Item )
        cls.user = ""
        cls.password = ""

    def test_should_open_marketplace( self ):
        marketplace.login( self.user, self.password )
        time.sleep( 10 )
        marketplace.get()
        time.sleep( 10 )
        marketplace.press_key.esc()
        time.sleep( 10 )
        marketplace.categories[ 'vehículos' ].click()
        time.sleep( 10 )
        links_1 = list( marketplace.items )
        marketplace.press_key.page_down()
        time.sleep( 10 )
        links_2 = list( marketplace.items )

        links_1_set = set( ( l.url for l in links_1 ) )
        links_2_set = set( ( l.url for l in links_2 ) )


        self.assertTrue( links_2_set - links_1_set )
        for item in links_1:
            self.assertFalse( item.url.params )


        marketplace.browser.get( item.url )
        time.sleep( 10 )
        result = marketplace.get_item_info( item )
        self.assertTrue( result )
        self.assertIn( "images_url", result )
        self.assertIn( "publish_date_relative", result )
        self.assertIn( "details", result )
        self.assertIn( "profile", result )
        self.assertTrue( result.details )

        download_folder = Chibi_temp_path()

        item = Item( **links_1[0] )
        item.save_if_not_exists()
        item.read_item_from_source(
            marketplace, download_folder=download_folder )

        self.assertTrue( item.details )
        self.assertTrue( item.images_url )
        self.assertTrue( item.publish_date_relative )
        self.assertTrue( item.scan_date )
        self.assertTrue( item.profile )


class Test_facebook_elastic( unittest.TestCase ):
    @classmethod
    def setUpClass( cls, ):
        super().setUpClass()
        configuration.elasticsearch.test_app = True
        Item._index._name = (
            "test__bid_stalker__facebook__item" )
        create_index_if_not_exists( Item )

    def test_convert_price_string_to_float( self ):
        item = Item( string_price="MX$255.000" )
        item.convert_price()
        self.assertEqual( item.price, 255.00 )
        self.assertEqual( item.currency, 'MX' )

    def test_convert_price_string_to_float_2( self ):
        item = Item( string_price="MX$1.234.567" )
        item.convert_price()
        self.assertEqual( item.price, 1234.567 )
        self.assertEqual( item.currency, 'MX' )

    def test_convert_price_string_to_float_3( self ):
        item = Item( string_price="MX$200" )
        item.convert_price()
        self.assertEqual( item.price, 200 )
        self.assertEqual( item.currency, 'MX' )

    def test_convert_price_string_to_float_4( self ):
        item = Item( string_price="Gratis" )
        item.convert_price()
        self.assertEqual( item.price, 0 )
