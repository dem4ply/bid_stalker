#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest
import itertools
from vcr_unittest import VCRTestCase
from bid_stalker.site.bidspotter import bidspotter_auctions, bidspotter
from bid_stalker.site.bidspotter import Catalog
from bid_stalker.site.bidspotter.snippets import parse_script_to_article
from chibi_requests import status_code
from elasticsearch_dsl import Document
from chibi_elasticsearch.unittests.vcr import Chibi_elastic_vcr
from chibi.config import configuration


example_1 = r"""
   if (typeof lotCollectionsManager != 'undefined'
        && lotCollectionsManager.push) {
                            var lotModelData =
                            {
                                LotId: 'dd207ae9-fb2a-4f34-be15-b3f70105da72',
                                StartTimeUtc: "\/Date(1771254000000)\/",
                                EndTimeUtc: "\/Date(1772728149505)\/",
                                LeadingBid: parseFloat(10.00),
                                ShowSaleResults: "False" === "True" ? true : false,
                                TotalBids: 0,
                                BidderId: '',
                                WinningBidderId: '802dbcaf-edf5-486d-a05c-b3f9014e873f',
                                Currency: 'GBP',
                                TimeZone: 'GMT Standard Time',
                                Reserve: parseFloat("10.00"),
                                Quantity: '1',
                                IsPieceMeal: 'False' === "True" ? true : false,
                                BidderHasBids: "False" === "True" ? true : false,
                                LotClosed: "True" === "True" ? true : false,
                                SecondsRemaining: -94,
                                AuctionType: "Timed",
                                Status: "WaitingToBeOffered",
                                StartPrice: parseFloat("10.00"),
                                BuyItNowPrice: parseFloat("0"),
                                NextMinimumBid: parseFloat(12.00),
                                BidderStatus: '',
                                IsDynamic: true,
                                AtgLotId:  '0'
                            };

                            var loadDataDynamically = 'false';
                            if (loadDataDynamically) {
                                lotModelData['IsDynamic'] = true;
                            }

                            lotCollectionsManager.push(new GAP.Module.Lot.Model.LotSearchResultModel(), lotModelData);
                        }

"""

class Test_snippets_parse_script( unittest.TestCase ):
    def test_parser_should_return_expected( self ):
        result = parse_script_to_article( example_1 )
        self.assertEqual(
            result.LotId, 'dd207ae9-fb2a-4f34-be15-b3f70105da72' )
        self.assertEqual( result.LeadingBid, 10.0 )
        self.assertEqual( result.ShowSaleResults, False )
        self.assertEqual( result.LotClosed, True )
        self.assertEqual( result.BidderStatus, '' )
