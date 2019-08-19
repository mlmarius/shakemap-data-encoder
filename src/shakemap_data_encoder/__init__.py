from typing import Dict
import xml.etree.cElementTree as ET
from dateutil.parser import parse
import xml.dom.minidom


def extract_generic_data(data: Dict[str, Dict[str, str]]) -> Dict[str, str]:
    first = data[list(data.keys())[0]]
    return {
        "eq_id": str(first['eq_id']),
        "netid": "RO",
        "network": "RO",
        "eq_lat": str(first['eq_lat']),
        "eq_lon": str(first['eq_lon']),
        "eq_depth": str(first['eq_depth']),
        "eq_Mw": str(first['eq_Mw']),
        "eq_origin": first['eq_origin'].replace('/', '-')+'Z',
        "locstring": "unknown",
        "event_type": "ACTUAL",
        "created_at": "unknown"
    }


def get_event_xml(data: Dict[str, Dict[str, str]]) -> str:
    generic = extract_generic_data(data)
    earthquake = ET.Element(
        "earthquake",
        id=generic['eq_id'],
        netid=generic['netid'],
        network=generic['network'],
        lat=generic['eq_lat'],
        lon=generic['eq_lon'],
        depth=generic['eq_depth'],
        mag=generic['eq_Mw'],
        time=generic['eq_origin'],
        locstring=generic['locstring'],
        event_type=generic['event_type'],
    )
    return ET.tostring(earthquake).decode('utf-8')


def get_ci_xml(data: Dict[str, Dict[str, str]]) -> str:
    header = '''
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<!DOCTYPE shakemap-data [
<!ELEMENT shakemap-data (earthquake,stationlist)>
<!ELEMENT stationlist (station+)>
<!ATTLIST stationlist
  created	CDATA	#REQUIRED
>

<!ELEMENT station (comp+)>
<!ATTLIST station
  code		CDATA 			#REQUIRED
  name		CDATA 			#REQUIRED
  insttype	CDATA 			#REQUIRED
  lat		CDATA 			#REQUIRED
  lon		CDATA 			#REQUIRED
  source	(SCSN|CGS|NSMP) 	'SCSN'
  netid		CDATA			#REQUIRED
  commtype	(DIG|ANA) 		'DIG'
  dist          CDATA                   '10.0'
  loc		CDATA			''
>

<!ELEMENT comp (acc,vel,psa*)>
<!ATTLIST comp
  name          CDATA  #REQUIRED
  originalname  CDATA  #IMPLIED
>

<!ELEMENT acc EMPTY>
<!ELEMENT vel EMPTY>
<!ELEMENT psa03 EMPTY>
<!ELEMENT psa10 EMPTY>
<!ELEMENT psa30 EMPTY>
<!ATTLIST acc
  value  CDATA         #REQUIRED
  flag   CDATA        ''
>
<!ATTLIST vel
  value CDATA          #REQUIRED
  flag  CDATA         ''
>
<!ATTLIST psa03
  value CDATA          #REQUIRED
  flag  CDATA         ''
>
<!ATTLIST psa10
  value CDATA          #REQUIRED
  flag  CDATA         ''
>
<!ATTLIST psa30
  value CDATA          #REQUIRED
  flag  CDATA         ''
>
<!ELEMENT  earthquake EMPTY>
<!ATTLIST earthquake
  id 		ID	#REQUIRED
  lat		CDATA	#REQUIRED
  lon		CDATA	#REQUIRED
  mag		CDATA	#REQUIRED
  year          CDATA   #REQUIRED
  month         CDATA   #REQUIRED
  day           CDATA   #REQUIRED
  hour          CDATA   #REQUIRED
  minute        CDATA   #REQUIRED
  second        CDATA   #REQUIRED
  timezone      CDATA   #REQUIRED
  depth		CDATA	#REQUIRED
  type		CDATA	#REQUIRED
  locstring	CDATA	#REQUIRED
  pga		CDATA   #REQUIRED
  pgv		CDATA   #REQUIRED
  sp03		CDATA   #REQUIRED
  sp10		CDATA   #REQUIRED
  sp30		CDATA   #REQUIRED
  created	CDATA	#REQUIRED
>
]>
    '''.strip()

    generic = extract_generic_data(data)
    root = ET.Element(
        'shakemap-data',
        code_version="3.5",
        map_version="1"
    )

    origin_time = parse(generic['eq_origin'])
    root.append(ET.Element(
        'earthquake',
        id=generic['eq_id'],
        lat=generic['eq_lat'],
        lon=generic['eq_lon'],
        mag=generic['eq_Mw'],
        year=str(origin_time.year),
        month=str(origin_time.month),
        day=str(origin_time.day),
        hour=str(origin_time.hour),
        minute=str(origin_time.minute),
        second=str(origin_time.second),
        timezone='UTC',
        depth=generic['eq_depth'],
        network=generic['network'],
        locstring=generic['locstring'],
        created=generic['created_at']
    ))

    station_list = ET.Element(
        'stationlist',
        created=generic['created_at']
    )

    for key, station in data.items():
        station_element = ET.Element(
            'station',
            code=station['sta_name'],
            name=station['sta_name'],
            insttype='ACCELEROMETER',
            lat=str(station['sta_lat']),
            lon=str(station['sta_lon']),
            dist=str(station['sta_epicdist']),
            source='RSN',
            netid=generic['netid'],
            commtype='unknown',
            loc='--',
            intensity=str(station['Intensity_max'])
        )

        for suffix in ('HNE', 'HNN'):

            comps = ET.Element(
                'comp',
                name=suffix
            )

            comps.append(ET.Element(
                'pga',
                value=str(station[f'PGA_{suffix}']),
                flag='0'
            ))

            comps.append(ET.Element(
                'pgv',
                value=str(station[f'PGV_{suffix}']),
                flag='0'
            ))

            comps.append(ET.Element(
                'psa03',
                value=str(station[f'PSA03_{suffix}']),
                flag='0'
            ))

            comps.append(ET.Element(
                'psa10',
                value=str(station[f'PSA10_{suffix}']),
                flag='0'
            ))

            comps.append(ET.Element(
                'psa30',
                value=str(station[f'PSA30_{suffix}']),
                flag='0'
            ))
            station_element.append(comps)

        station_list.append(station_element)

    root.append(station_list)
    out = ET.tostring(root).decode('utf-8')
    out = f"{header}\n{out}"

    # dom = xml.dom.minidom.parse(xml)  # or xml.dom.minidom.parseString(xml_string)
    dom = xml.dom.minidom.parseString(out)
    pretty_xml_as_string = dom.toprettyxml()
    return pretty_xml_as_string
