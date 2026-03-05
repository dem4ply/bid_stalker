from marshmallow import Schema, INCLUDE, fields, EXCLUDE, pre_load


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
