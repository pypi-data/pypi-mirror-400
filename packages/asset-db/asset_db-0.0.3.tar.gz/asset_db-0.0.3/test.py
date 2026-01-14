from asset_db.repository.neo4j import NeoRepository
from asset_db.types import Edge
from asset_db.types import Entity
from oam import FQDN
from oam import IPAddress, IPAddressType
from oam import BasicDNSRelation
from oam import DNSRecordProperty
from oam import SourceProperty

uri = "neo4j://localhost"
auth = ("neo4j", "password")

with NeoRepository(uri, auth) as db:
    fqdn = db.create_asset(FQDN("owasp.org"))
    
    ip = db.create_entity(
        Entity(
            asset = IPAddress("104.20.44.163", IPAddressType.IPv4)))
    
    a_record  = db.create_edge(
        Edge(
            relation    = BasicDNSRelation("dns_record", rrtype=1),
            from_entity = fqdn,
            to_entity   = ip))
    
    txt_record = db.create_entity_property(
        fqdn,
        DNSRecordProperty("dns_record", "token=awes0me", 16))
    
    source = db.create_edge_property(
        a_record,
        SourceProperty("myscript", 100))


