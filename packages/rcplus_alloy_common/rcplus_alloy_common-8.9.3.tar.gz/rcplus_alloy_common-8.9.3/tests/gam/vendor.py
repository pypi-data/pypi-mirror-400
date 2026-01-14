import base64

from rcplus_alloy_common.gam.vendor.common import GAMSOAPBaseModel
from rcplus_alloy_common.gam.vendor.line_items import (
    LineItem,
    GeoTargeting,
    Location,
    CustomCriteria,
    CustomCriteriaSet,
    AudienceSegmentCriteria,
    get_custom_criteria_set_children_discriminator_value as ccs_discriminator,
)
from rcplus_alloy_common.gam.vendor.line_item_creative_associations import LineItemCreativeAssociation
from rcplus_alloy_common.gam.vendor.companies import Company
from rcplus_alloy_common.gam.vendor.creatives import Creative, CreativeAsset
from rcplus_alloy_common.gam.vendor.orders import Order
from rcplus_alloy_common.gam.vendor.forecast import DeliveryForecast
from rcplus_alloy_common.gam.vendor.network import Network
from rcplus_alloy_common.gam.vendor.audience_segments import AudienceSegment
from rcplus_alloy_common.gam.vendor.inventory import AdUnit
from rcplus_alloy_common.gam.vendor.custom_targeting import CustomTargetingKey, CustomTargetingValue


def test_vendor():
    assert issubclass(LineItem, GAMSOAPBaseModel)
    assert issubclass(GeoTargeting, GAMSOAPBaseModel)
    assert issubclass(LineItemCreativeAssociation, GAMSOAPBaseModel)
    assert issubclass(Company, GAMSOAPBaseModel)
    assert issubclass(Creative, GAMSOAPBaseModel)
    assert issubclass(Order, GAMSOAPBaseModel)
    assert issubclass(DeliveryForecast, GAMSOAPBaseModel)
    assert issubclass(Network, GAMSOAPBaseModel)
    assert issubclass(AudienceSegment, GAMSOAPBaseModel)
    assert issubclass(AdUnit, GAMSOAPBaseModel)
    assert issubclass(CustomTargetingKey, GAMSOAPBaseModel)
    assert issubclass(CustomTargetingValue, GAMSOAPBaseModel)


def test_geo_targeting():
    # test that the only required field of Location is id
    geo = GeoTargeting(
        targetedLocations=[
            Location(
                id=1,
            )
        ]
    )

    assert geo.model_dump(exclude_none=True, exclude_unset=True) == {
        "targetedLocations": [
            {
                "id": 1,
                "xsi_type": "Location",
            },
        ],
        "xsi_type": "GeoTargeting",
    }


def test_ccs_discriminator():

    audience_segment_criteria = AudienceSegmentCriteria(
        audienceSegmentIds=[1, 2],
        operator="IS",
    )
    custom_criteria = CustomCriteria(
        keyId=1,
        valueIds=[2, 3],
        operator="IS",
    )
    custom_criteria_set = CustomCriteriaSet(
        children=[
            audience_segment_criteria,
            custom_criteria,
        ],
        logicalOperator="AND",
    )

    assert ccs_discriminator(custom_criteria_set) == "CustomCriteriaSet"
    assert ccs_discriminator(custom_criteria) == "CustomCriteria"
    assert ccs_discriminator(audience_segment_criteria) == "AudienceSegmentCriteria"
    assert ccs_discriminator({"xsi_type": "CustomCriteriaSet"}) == "CustomCriteriaSet"
    assert ccs_discriminator({"xsi_type": "CustomCriteria"}) == "CustomCriteria"
    assert ccs_discriminator({"xsi_type": "AudienceSegmentCriteria"}) == "AudienceSegmentCriteria"
    assert ccs_discriminator(custom_criteria_set.model_dump()) == "CustomCriteriaSet"
    assert ccs_discriminator(custom_criteria.model_dump()) == "CustomCriteria"
    assert ccs_discriminator(audience_segment_criteria.model_dump()) == "AudienceSegmentCriteria"

    custom_criteria_set_without_xsi_type = custom_criteria_set.model_dump()
    del custom_criteria_set_without_xsi_type["xsi_type"]
    assert ccs_discriminator(custom_criteria_set_without_xsi_type) == "CustomCriteriaSet"

    custom_criteria_without_xsi_type = custom_criteria.model_dump()
    del custom_criteria_without_xsi_type["xsi_type"]
    assert ccs_discriminator(custom_criteria_without_xsi_type) == "CustomCriteria"

    audience_segment_criteria_without_xsi_type = audience_segment_criteria.model_dump()
    del audience_segment_criteria_without_xsi_type["xsi_type"]
    assert ccs_discriminator(audience_segment_criteria_without_xsi_type) == "AudienceSegmentCriteria"


def test_creative_asset_bytes_array():

    # test case
    binary = b"test"
    b64_binary = base64.b64encode(binary)
    creative_asset = CreativeAsset(assetByteArray=b64_binary)

    # accept string
    assert creative_asset == CreativeAsset(assetByteArray=b64_binary.decode())

    # serialize to python
    assert creative_asset.model_dump(exclude_none=True, exclude_unset=True) == {
        "assetByteArray": b64_binary.decode(),
        "xsi_type": "CreativeAsset",
    }

    # deserialize from json
    assert CreativeAsset.model_validate_json(
        f'{{"assetByteArray": "{b64_binary.decode()}", "xsi_type": "CreativeAsset"}}'
    ) == creative_asset
