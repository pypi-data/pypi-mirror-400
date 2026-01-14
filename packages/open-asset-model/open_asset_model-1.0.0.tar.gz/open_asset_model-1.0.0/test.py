from oam import AssetType, RelationType
from oam import get_asset_by_type, get_relation_by_type
from oam import describe_oam_object

fqdn_cls = get_relation_by_type(RelationType.BasicDNSRelation)


