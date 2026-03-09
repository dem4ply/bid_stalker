from marshmallow import Schema, INCLUDE, fields, EXCLUDE, pre_load
from chibi_atlas import Chibi_atlas


class Event( Schema ):
    attendance_mode = fields.String( data_key='eventAttendanceMode' )
    status = fields.String( data_key='eventStatus' )

    class Meta:
        unknown = EXCLUDE


class Address( Schema ):
    kind = fields.String( data_key='@type' )
    country = fields.String( data_key='addressCountry' )
    locality = fields.String( data_key='addressLocality' )
    region = fields.String( data_key='addressRegion' )
    postal_code = fields.String( data_key='postalCode' )
    street = fields.String( data_key='streetAddress' )

    class Meta:
        unknown = INCLUDE


class Location( Schema ):
    kind = fields.String( data_key='@type' )
    url = fields.String()
    address = fields.Nested( Address, allow_none=True )

    class Meta:
        unknown = INCLUDE


class Organizer( Schema ):
    kind = fields.String( data_key='@type' )
    name = fields.String()
    url = fields.String()

    class Meta:
        unknown = INCLUDE


class Audiction( Schema ):
    name = fields.String()
    description = fields.String( allow_none=True )
    kind = fields.String( data_key='@type' )
    end_date = fields.DateTime( data_key='endDate' )
    start_date = fields.DateTime( data_key='startDate' )
    event = fields.Nested( Event )
    image_url = fields.String( data_key='image' )
    location = fields.Nested( Location, allow_none=True, many=True )
    url = fields.String()
    organizer = Organizer()

    class Meta:
        unknown = EXCLUDE

    @pre_load
    def add_event( self, data, *args, **kw ):
        data[ 'event' ] = data
        return data

    @pre_load
    def location_to_list( self, data, *args, **kw ):
        if 'location' in data and data[ 'location' ]:
            if not isinstance( data[ 'location' ], list ):
                data[ 'location' ] = [ data[ 'location' ] ]
        return data


class Lot( Schema ):
    kind = fields.String()
    number = fields.String()


class Auctioneer( Schema ):
    name = fields.String()
    url = fields.Url()


class Info_article( Schema ):
    description = fields.String()
    auction = fields.String()
    shipping = fields.String()
    terms = fields.String()

    class Meta:
        unknown = INCLUDE


class Catalog( Schema ):
    name = fields.String()
    url = fields.Url()
    pk = fields.String( allow_none=True )

    class Meta:
        unknown = INCLUDE


class Article( Schema ):
    url = fields.Url()
    name = fields.String()
    catalog = fields.Nested( Catalog )
    description = fields.String( data_key="info.description" )
    info = fields.Nested( Info_article )
    lot = fields.Nested( Lot )
    images_url = fields.List( fields.Url )
    tags = fields.List( fields.String )
    audiction_date = fields.DateTime( format='%Y-%m-%dT%H-%M-%S%z' )
    auctioneer = fields.Nested( Auctioneer )

    class Meta:
        unknown = INCLUDE
        model = Chibi_atlas
