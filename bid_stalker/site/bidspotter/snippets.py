from chibi_atlas import Chibi_atlas


def parse_script_to_article( script ):
    lines = script.split( '\n' )
    lines = map( str.strip, lines )
    lines = list( filter( bool, lines ) )
    start = 0
    end = 0
    for i, line in enumerate( lines ):
        if line.startswith( '{' ):
            start = i + 1
            continue
        if line.endswith( '};' ):
            end = i
            break

    data = lines[ start:end ]
    data_kv = map( lambda x: x.split( ":", 1 ), data )
    try:
        data_dict = { k.strip(): v.strip() for k, v in data_kv }
    except:
        import pdb
        pdb.set_trace()
        raise
    result = _clean_parse( data_dict )
    return result


def _clean_parse( data ):
    result = Chibi_atlas()
    for k, v in data.items():
        # elemina las comillas
        if v.startswith( '"False" ===' ) or v.startswith( '"True" ===' ):
            a, b = v.split( '?', 1 )
            a, b = a.split( '===', 1 )
            if 'false' in a.lower():
                a = False
            else:
                a = True
            if 'false' in b.lower():
                b = False
            else:
                b = True
            v = a == b
        elif v.startswith( r'"\/Date(' ):
            v = v.replace( r'"\/Date(', "" )
            v = v.replace( r')\/', "" )
        elif v.startswith( r'parseFloat' ):
            v = v.replace( r'parseFloat(', "" )
            v = v.replace( r'),', "" )
            if v.startswith( '"' ) or v.startswith( "'" ):
                v = v = v[1:-1]
            v = float( v )
        elif v.startswith( '"' ) or v.startswith( "'" ):
            v = v = v[1:-2]
        result[ k ] = v
    return result
