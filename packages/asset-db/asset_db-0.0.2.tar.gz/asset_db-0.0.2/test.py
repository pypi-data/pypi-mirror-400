from asset_db.repository.neo4j.neo_repository import NeoRepository
from oam import (
    Asset,
    Relation,
    FQDN,
    IPAddress,
    IPAddressType,
    BasicDNSRelation,
    DNSRecordProperty,
    SourceProperty,
    DNSRecordProperty,
    valid_relationship
)
from asset_db.types.entity import Entity
from asset_db.types.edge import Edge
from asset_db.types.entity_tag import EntityTag
from asset_db.types.edge_tag import EdgeTag

uri = "neo4j://localhost"
auth = ("neo4j", "password")

with NeoRepository(uri, auth) as db:
    fqdn = db.create_asset(FQDN("www.oppliger.pro"))
    ip   = db.create_asset(IPAddress("130.11.0.45", IPAddressType.IPv4))
    rel  = db.create_edge(Edge(
        relation    = BasicDNSRelation("dns_record", rrtype=16),
        from_entity = fqdn,
        to_entity   = ip
    ))
    rel_tag = db.create_edge_property(rel, DNSRecordProperty(
        property_name="TXT",
        rrtype=1,
        data="test"
    ))
    ip_tag = db.create_entity_property(fqdn, DNSRecordProperty("dns_record", "key=value", 16))

    print(rel_tag)


