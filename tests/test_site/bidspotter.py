#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest
import itertools
from vcr_unittest import VCRTestCase
from bid_stalker.site.bidspotter import bidspotter_auctions, bidspotter
from bid_stalker.site.bidspotter import Catalog
from chibi_requests import status_code
from elasticsearch_dsl import Document
from chibi_elasticsearch.unittests.vcr import Chibi_elastic_vcr
from chibi.config import configuration


class Test_bidsspotter( VCRTestCase ):
    def test_audiction_property_should_return_catalog( self ):
        catalog = bidspotter.auction
        self.assertIsInstance( catalog, Catalog )
        self.assertEqual( catalog.base_name, 'auction-catalogues' )
        self.assertEqual(
            catalog.dir_name, 'https://www.bidspotter.com/en-us' )


class Test_bidspotter_cookies( unittest.TestCase ):
    @classmethod
    def setUpClass( cls ):
        super().setUpClass()
        cls.bid = bidspotter
        cls.bid.prepare_session()
        cls.site = bidspotter.auction


class Test_bidsspotter_auctions( Test_bidspotter_cookies, VCRTestCase ):

    def test_should_return_200( self ):
        response = self.site.get()
        self.assertEqual( response.status_code, status_code.HTTP_200_OK )

    def test_catalog_should_have_articles( self ):
        articles = list( itertools.islice( self.site.articles, 10 ) )
        self.assertTrue( articles )
        self.assertEqual( len( articles ), 10  )

    def test_articles_should_have_data( self ):
        articles = list( itertools.islice( self.site.articles, 10 ) )
        self.assertTrue( articles )
        for article in articles:
            self.assertTrue( article.kw.article_data )

    def test_catalog_should_have_countries( self ):
        countries = self.site.countries
        self.assertTrue( countries )
        self.assertIsInstance( countries, dict )

    def test_catalog_countries_should_be_catalogs( self ):
        countries = self.site.countries
        self.assertTrue( countries )
        for k, v in countries.items():
            self.assertTrue( v )
            self.assertIsInstance( v, Catalog )


class Test_auction_data( Test_bidspotter_cookies, Chibi_elastic_vcr ):
    @classmethod
    def setUpClass( cls, ):
        super().setUpClass()
        configuration.elasticsearch.test_app = True

    def setUp( self ):
        super().setUp()
        self.articles = list( itertools.islice( self.site.articles, 10 ) )
        self.article = self.articles[0]

    def test_to_dict_should_return_a_dict( self ):
        result = self.article.to_dict()
        self.assertIsInstance( result, dict )
        self.assertTrue( result )

    def test_if_description_is_missing_should_return_none( self ):
        self.article.kw.article_data.description = None
        result = self.article.to_dict()
        self.assertIsNone( result.description )

    def test_if_description_is_missing_should_return_empty( self ):
        self.article.kw.article_data.description = ""
        result = self.article.to_dict()
        self.assertEqual( result.description, "" )

    def test_to_dict_should_have_expected_keys( self ):
        result = self.article.to_dict()
        self.assertIn( 'event', result )
        self.assertIn( 'attendance_mode', result.event )
        self.assertIn( 'status', result.event )
        self.assertIn( 'location', result )

    def test_to_dict_should_return_a_es( self ):
        result = self.article.to_es()
        self.assertIsInstance( result, Document )
        self.assertTrue( result )

    def test_location_can_be_none( self ):
        self.article.kw.article_data.location = None
        result = self.article.to_dict()
        self.assertIsNone( result.location )

    def test_location_can_be_one( self ):
        location = self.article.kw.article_data.location
        if isinstance( location, list ):
            self.fail( "en esta prueba location no puede ser una lista" )
        self.article.kw.article_data.location = location
        result = self.article.to_dict()
        self.assertTrue( result.location )

    def test_location_can_be_many( self ):
        location = self.article.kw.article_data.location
        self.article.kw.article_data.location = [ location, location ]
        result = self.article.to_dict()
        self.assertTrue( result.location )
        self.assertEqual( len( result.location ), 2 )

    def test_location_can_have_address( self ):
        location = self.article.kw.article_data.location
        location.address = {
            '@type': 'PostalAddress',
            'addressCountry': 'Mexico',
            'addressLocality': 'Arteaga',
            'addressRegion': 'Mexico CP',
            'postalCode': '25350',
            'streetAddress': 'Parque Industrial Arteaga KM 8.52D Coahuila'
        }
        result = self.article.to_dict()
        self.assertTrue( result.location[0].address )

    def test_location_address_is_optional( self ):
        location = self.article.kw.article_data.location
        location.address = None
        result = self.article.to_dict()
        self.assertNotIn( 'address', result.location )

    def test_location_address_can_be_empty_dict( self ):
        location = self.article.kw.article_data.location
        location.address = {}
        result = self.article.to_dict()
        self.assertNotIn( 'address', result.location )
