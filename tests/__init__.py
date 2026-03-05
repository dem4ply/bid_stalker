# -*- coding: utf-8 -*-
from chibi.config import configuration, basic_config


basic_config( 'WARNING' )

configuration.loggers[ 'vcr.stub' ].level = 'WARNING'
# configuration.loggers[ 'vcr.cassette' ].level = 'WARNING'
configuration.loggers[ 'vcr' ].level = 'WARNING'
