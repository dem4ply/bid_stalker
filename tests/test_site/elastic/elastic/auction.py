#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
import unittest
import itertools
from unittest.mock import patch
from vcr_unittest import VCRTestCase
from bid_stalker.site.bidspotter import bidspotter_auctions, bidspotter
from bid_stalker.site.bidspotter import Catalog
from chibi_requests import status_code
from elasticsearch_dsl import Document
from chibi.config import configuration
from bid_stalker.site.bidspotter.elastic import Audiction
from chibi_elasticsearch.config import review_elasticsearch_config
from chibi_elasticsearch.snippet import create_index_if_not_exists
from chibi_elasticsearch.unittests import patch_doc_save

from tests.test_site.bidspotter import Test_bidspotter_cookies
from chibi_elasticsearch.unittests.vcr import Chibi_elastic_vcr

from bid_stalker.site.bidspotter.bidspotter import Audiction as Audiction_site


class Test_elastic( Test_bidspotter_cookies, Chibi_elastic_vcr ):
    @classmethod
    def setUpClass( cls, ):
        super().setUpClass()
        configuration.elasticsearch.test_app = True
        Audiction._index._name = (
            "test__bid_stalker__bidspotter__audiction" )
        create_index_if_not_exists( Audiction )


class Test_auction_elastic_index( Test_elastic ):
    def test_should_work( self ):
        self.assertEqual(
            Audiction._index._name,
            "test__bid_stalker__bidspotter__audiction"
        )


class Test_auction_elastic_save_article( Test_elastic ):
    def setUp( self ):
        super().setUp()
        self.articles = list( itertools.islice( self.site.articles, 10 ) )
        self.article = self.articles[0]

    def test_save_model_should_work( self ):
        model = self.article.to_es()
        result = model.save()
        self.assertTrue( result )


class Test_audiction_model( Test_elastic ):
    @classmethod
    def setUpClass( cls ):
        super().setUpClass()
        cls.articles = list( itertools.islice( cls.site.articles, 10 ) )
        cls.article = cls.articles[0]
        cls.model = cls.article.to_es()
        models = list( Audiction.Q.url( cls.model.url ).scan() )
        # elimina los modelos repetidos por fallas
        if models and len( models ) > 1:
            cls.model = models.pop()
            for model in models:
                model.delete()
        else:
            cls.model.save()
        cls.flush_and_get( cls.model )

    @classmethod
    def flush_and_get( cls, model, retry=0, max_retry=5 ):
        Audiction._index.flush()
        time.sleep( 1 )
        try:
            Audiction.get( id=cls.model.meta.id )
        except:
            if retry > max_retry:
                raise
            time.sleep( 1 )
            cls.flush_and_get( model, retry=retry+1, max_retry=max_retry )

class Test_auction_basic_model( Test_audiction_model ):

    def test_should_work( self ):
        self.assertTrue( self.model )
        self.assertTrue( self.model.meta.id )

    def test_should_be_posible_to_search_with_url( self ):
        s = Audiction.Q.url( self.model.url )
        model = s.execute()[0]
        self.assertEqual( self.model.meta.id, model.meta.id )

    def test_model_have_url( self ):
        self.assertTrue( self.model.url )

    def test_model_have_image_url( self ):
        self.assertTrue( self.model.image_url )

    def test_model_have_image_name( self ):
        self.assertTrue( self.model.name )

    def test_model_have_image_dates( self ):
        self.assertTrue( self.model.start_date )
        self.assertTrue( self.model.end_date )


class Test_auction_Q( Test_audiction_model ):
    def test_url_exists_should_return_true_if_exists( self ):
        self.assertTrue(
            Audiction.Q.url_exists( self.model.url ) )

    def test_url_exists_should_return_false_if_not_exists( self ):
        self.assertFalse(
            Audiction.Q.url_exists( "url not exists" ) )


class Test_auction_save_if_url_not_exists( Test_audiction_model ):
    @patch_doc_save
    def test_when_url_exists_should_not_call_save( self, save ):
        self.model.save_if_not_exists()
        save.assert_not_called()

    @patch_doc_save
    def test_when_url_not_exists_should_call_save( self, save ):
        model = Audiction( **self.model.to_dict() )
        model.url = "other url"
        model.save_if_not_exists()
        save.assert_called_once()


class Test_auction_site( Test_audiction_model ):
    def test_should_be_a_instance_of_audiction( self ):
        site = self.model.site
        self.assertIsInstance( site, Audiction_site )

    def test_site_should_have_the_same_url( self ):
        site = self.model.site
        self.assertEqual( site, self.model.url )
