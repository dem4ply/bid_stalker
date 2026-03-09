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
from bid_stalker.site.bidspotter.elastic import Article
from chibi_elasticsearch.config import review_elasticsearch_config
from chibi_elasticsearch.snippet import create_index_if_not_exists
from chibi_elasticsearch.unittests import patch_doc_save

from tests.test_site.bidspotter import Test_bidspotter_article
from chibi_elasticsearch.unittests.vcr import Chibi_elastic_vcr


class Test_elastic( Test_bidspotter_article, Chibi_elastic_vcr ):
    @classmethod
    def setUpClass( cls, ):
        super().setUpClass()
        configuration.elasticsearch.test_app = True
        Article._index._name = (
            "test__bid_stalker__bidspotter__article" )
        create_index_if_not_exists( Article )


class Test_article_elastic_index( Test_elastic ):
    def test_should_work( self ):
        self.assertEqual(
            Article._index._name,
            "test__bid_stalker__bidspotter__article"
        )
