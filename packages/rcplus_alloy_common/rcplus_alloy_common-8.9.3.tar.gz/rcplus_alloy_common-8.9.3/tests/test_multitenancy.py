import json

from rcplus_alloy_common.multitenancy import (
    CustomAttributeRawDataFormat,
    CustomAttributeType,
    TenantConfig
)


def test_parse_config_object():  # noqa: PLR0915
    with open("tests/tenant_configs.json") as f:
        obj = json.load(f)

    configs = [TenantConfig(**tenant_obj) for tenant_obj in obj]
    assert len(configs) == 3
    assert isinstance(configs[0], TenantConfig)
    assert configs[0].name == "tenant_1"
    assert configs[0].timezone == "Europe/Berlin"
    assert configs[0].cron_schedule == {
        "alloy-tracking-pipeline-tenant_1-downsample": "20 1,9,12,18 * * *"
    }
    assert configs[1].name == "tenant_2"
    assert configs[1].timezone is None
    assert configs[1].cron_schedule is None
    assert configs[2].name == "tenant_3"
    assert configs[2].timezone is None
    assert configs[2].cron_schedule is None
    assert configs[0].activation_channels.gam.network_id == 987654321
    assert configs[0].activation_channels.gam.activate_by_default is True
    assert configs[0].activation_channels.xandr.member_id == 4321
    assert configs[0].activation_channels.xandr.aws_region == "eu-west-1"
    assert configs[0].activation_channels.xandr.ppid_source == "ringier.ch"
    assert configs[0].activation_channels.xandr.activate_by_default is True
    assert configs[0].activation_channels.das.network_id == 56789
    assert configs[0].activation_channels.das.activate_by_default is False
    assert configs[0].features.sso_data is True
    assert configs[0].features.enterprise is True
    assert configs[0].features.dcr is True
    assert configs[0].features.byok is True
    assert configs[0].features.gotom is True
    assert configs[0].features.coops is True
    assert configs[0].features.audience_segment_service is True
    assert configs[1].features.audience_segment_service is False

    assert len(configs[0].custom_attributes) == 6
    assert configs[0].custom_attributes[0].name == "subscriptions"
    assert configs[0].custom_attributes[0].target_external_id_name is None
    assert configs[0].custom_attributes[0].display_name == "Subscriptions"
    assert configs[0].custom_attributes[0].category == "Interests"
    assert configs[0].custom_attributes[0].active is True
    assert configs[0].custom_attributes[0].external_id_name == "external_id1"
    assert configs[0].custom_attributes[0].raw_data_format == CustomAttributeRawDataFormat.parquet
    assert configs[0].custom_attributes[0].incremental is True
    assert configs[0].custom_attributes[0].type == CustomAttributeType.direct
    assert configs[0].custom_attributes[0].id_pii is False
    assert configs[0].custom_attributes[0].value_pii is False
    assert configs[0].custom_attributes[0].s3_predictions_params_path is None
    assert configs[0].custom_attributes[1].name == "smg_audience_segment"
    assert configs[0].custom_attributes[1].target_external_id_name is None
    assert configs[0].custom_attributes[1].display_name == "SMG audience segment"
    assert configs[0].custom_attributes[1].category == "SMG"
    assert configs[0].custom_attributes[1].active is True
    assert configs[0].custom_attributes[1].external_id_name == "network_userid"
    assert configs[0].custom_attributes[1].raw_data_format == CustomAttributeRawDataFormat.parquet
    assert configs[0].custom_attributes[1].incremental is True
    assert configs[0].custom_attributes[1].type == CustomAttributeType.audience_segment
    assert configs[0].custom_attributes[1].id_pii is False
    assert configs[0].custom_attributes[1].value_pii is False
    assert configs[0].custom_attributes[1].s3_predictions_params_path is None
    assert configs[0].custom_attributes[2].name == "income"
    assert configs[0].custom_attributes[2].target_external_id_name is None
    assert configs[0].custom_attributes[2].display_name == "Income"
    assert configs[0].custom_attributes[2].category == "Socio"
    assert configs[0].custom_attributes[2].active is False
    assert configs[0].custom_attributes[2].external_id_name == "external_id2"
    assert configs[0].custom_attributes[2].raw_data_format == CustomAttributeRawDataFormat.parquet
    assert configs[0].custom_attributes[2].incremental is False
    assert configs[0].custom_attributes[2].type == CustomAttributeType.training
    assert configs[0].custom_attributes[2].id_pii is True
    assert configs[0].custom_attributes[2].value_pii is False
    assert configs[0].custom_attributes[2].s3_predictions_params_path == "s3://models-bucket/tenant_1/income"
    assert configs[0].custom_attributes[3].name == "sso_id__farcaster_id"
    assert configs[0].custom_attributes[3].target_external_id_name == "farcaster_id"
    assert configs[0].custom_attributes[3].display_name is None
    assert configs[0].custom_attributes[3].category is None
    assert configs[0].custom_attributes[3].active is True
    assert configs[0].custom_attributes[3].external_id_name == "sso_id"
    assert configs[0].custom_attributes[3].raw_data_format == CustomAttributeRawDataFormat.parquet
    assert configs[0].custom_attributes[3].incremental is True
    assert configs[0].custom_attributes[3].type == CustomAttributeType.external_id
    assert configs[0].custom_attributes[3].id_pii is True
    assert configs[0].custom_attributes[3].value_pii is True
    assert configs[0].custom_attributes[3].s3_predictions_params_path is None

    assert configs[0].kropka_tenants == ["kropka_1", "kropka_2"]
    assert configs[0].content_providers[0].name == "content-provider-1"
    assert configs[0].content_providers[0].section_prefixes == ["prefix_1", "prefix_2"]
    assert configs[0].content_providers[0].uri_prefixes == ["www.content-provider-1.ext"]
    assert configs[0].content_providers[0].source_system == "source_1"
    assert configs[0].content_providers[0].content_id_extraction_query == "query_1"
    assert configs[0].content_providers[0].hardcoded_taxonomies[0].name == "taxonomy_1"
    assert configs[0].content_providers[0].hardcoded_taxonomies[0].score == 0.5
    assert configs[0].content_providers[0].is_uri_extracted_id_external_id is True
    assert configs[0].content_providers[0].canonical_id_extraction is None
    assert configs[0].content_providers[0].app_ids == ["app_1"]
    assert configs[0].content_providers[1].name == "content-provider-2"
    assert configs[0].content_providers[1].section_prefixes == ["prefix_3", "prefix_4"]
    assert configs[0].content_providers[1].uri_prefixes == ["www.content-provider-2.ext"]
    assert configs[0].content_providers[1].source_system == "source_2"
    assert configs[0].content_providers[1].content_id_extraction_query is None
    assert configs[0].content_providers[1].hardcoded_taxonomies is None
    assert configs[0].content_providers[1].is_uri_extracted_id_external_id is False
    assert configs[0].content_providers[1].canonical_id_extraction.uri_provider == "source_2~content-provider-2"
    assert configs[0].content_providers[1].canonical_id_extraction.id_regex == "(\\w+)$"
    assert configs[0].content_providers[1].canonical_id_extraction.use_uri_path_hash_as_extracted_id is None
    assert configs[0].content_providers[1].app_ids is None
    assert configs[0].tracking_providers[0].tracker == "tracker_0"
    assert configs[0].tracking_providers[0].logical_paths == ["path_1"]
    assert configs[0].tracking_providers[0].configs is None
    assert configs[0].tracking_providers[1].tracker == "tracker_1"
    assert configs[0].tracking_providers[1].logical_paths == ["path_1", "path_2"]
    assert configs[0].tracking_providers[1].configs is not None
    assert len(configs[0].tracking_providers[1].configs) == 2
    assert configs[0].tracking_providers[1].configs[0] is not None
    assert len(configs[0].tracking_providers[1].configs[0].app_ids) == 2
    assert configs[0].tracking_providers[1].configs[0].app_ids[0] == "app_id_11"
    assert configs[0].tracking_providers[1].configs[0].app_ids[1] == "app_id_12"
    assert configs[0].tracking_providers[1].configs[0].id_regex == "-(\\d+)$"
    assert configs[0].tracking_providers[1].configs[0].skip_urls_contextual == ["https://blick.ch/fr/$"]
    assert configs[0].tracking_providers[1].configs[0].use_uri_path_hash_as_extracted_id is False
    assert len(configs[0].tracking_providers[1].configs[0].data_layer_auto_tracking_events) == 2
    assert configs[0].tracking_providers[1].configs[0].data_layer_auto_tracking_events[0].key_name == "event1"
    assert configs[0].tracking_providers[1].configs[0].data_layer_auto_tracking_events[0].key_value == "virtual_pageview1"
    assert configs[0].tracking_providers[1].configs[0].data_layer_auto_tracking_events[0].event_path == "data1"
    assert configs[0].tracking_providers[1].configs[0].data_layer_auto_tracking_events[1].key_name == "event2"
    assert configs[0].tracking_providers[1].configs[0].data_layer_auto_tracking_events[1].key_value == "virtual_pageview2"
    assert configs[0].tracking_providers[1].configs[1] is not None
    assert len(configs[0].tracking_providers[1].configs[1].app_ids) == 1
    assert configs[0].tracking_providers[1].configs[1].app_ids[0] == "app_id_2"
    assert configs[0].tracking_providers[1].configs[1].id_regex is None
    assert configs[0].tracking_providers[1].configs[1].skip_urls_contextual is None
    assert configs[0].tracking_providers[1].configs[1].use_uri_path_hash_as_extracted_id is True
    assert len(configs[0].tracking_providers[1].configs[1].data_layer_auto_tracking_events) == 0

    assert configs[1].activation_channels.gam.network_id == 12313
    assert configs[1].activation_channels.gam.activate_by_default is True
    assert configs[1].activation_channels.xandr is None
    assert configs[1].activation_channels.das is None
    assert configs[1].features.sso_data is False
    assert configs[1].features.enterprise is False
    assert configs[1].features.dcr is False
    assert configs[1].features.byok is False
    assert configs[1].features.gotom is False
    assert configs[1].features.coops is False
    assert len(configs[1].custom_attributes) == 0
    assert configs[1].kropka_tenants == []
    assert configs[1].content_providers[0].name == "content-provider-3"
    assert configs[1].content_providers[0].section_prefixes == ["prefix_5", "prefix_6"]
    assert configs[1].content_providers[0].uri_prefixes == ["www.content-provider-3.ext"]
    assert configs[1].content_providers[0].source_system == "source_3"
    assert configs[1].content_providers[0].hardcoded_taxonomies is None
    assert configs[1].content_providers[0].is_uri_extracted_id_external_id is None
    assert configs[1].content_providers[0].content_id_extraction_query is None
    assert configs[1].content_providers[0].app_ids is None
    assert configs[1].tracking_providers[0].tracker == "tracker_2"
    assert configs[1].tracking_providers[0].logical_paths == []

    assert configs[2].is_test_tenant is True
    assert configs[2].activation_channels.gam.network_id == 12313
    assert configs[2].activation_channels.gam.activate_by_default is False
    assert configs[2].activation_channels.xandr is None
    assert configs[2].activation_channels.das is None
    assert configs[2].features.sso_data is False
    assert configs[2].features.enterprise is False
    assert configs[2].features.dcr is False
    assert configs[2].features.byok is False
    assert configs[2].features.gotom is False
    assert configs[2].features.coops is False
    assert len(configs[2].custom_attributes) == 2
    assert configs[2].custom_attributes[0].name == "real_estate_offer_type"
    assert configs[2].custom_attributes[0].target_external_id_name is None
    assert configs[2].custom_attributes[0].display_name == "Offer Type"
    assert configs[2].custom_attributes[0].category == "Real Estate Features"
    assert configs[2].custom_attributes[0].active is True
    assert configs[2].custom_attributes[0].external_id_name is None
    assert configs[2].custom_attributes[0].raw_data_format is None
    assert configs[2].custom_attributes[0].incremental is None
    assert configs[2].custom_attributes[0].type == CustomAttributeType.content
    assert configs[2].custom_attributes[0].id_pii is None
    assert configs[2].custom_attributes[0].value_pii is False
    assert configs[2].custom_attributes[0].s3_predictions_params_path is None
    assert configs[2].custom_attributes[0].query.conditions[0].condition.operator == "in"
    assert configs[2].custom_attributes[0].query.conditions[0].condition.value == [
        "homegate-ch",
        "immoscout24-ch"
    ]
    assert configs[2].custom_attributes[0].query.conditions[0].condition.attribute == "content_provider"
    assert configs[2].custom_attributes[0].query.conditions[0].result.type == "jsonpath"
    assert configs[2].custom_attributes[0].query.conditions[0].result.jsonpath == "$.attributes.offerType[0]"
    assert configs[2].custom_attributes[0].query.conditions[0].result.string == "content_attributes"
    assert configs[2].custom_attributes[0].query.conditions[0].result.separator == ","
    assert configs[2].custom_attributes[0].query.result is None
    assert configs[2].custom_attributes[0].map_values is not None
    assert configs[2].custom_attributes[0].map_values[0].values == [
        "rent",
        "mieten",
        "affittare",
        "louer"
    ]
    assert configs[2].custom_attributes[0].map_values[0].name == "rent"
    assert configs[2].custom_attributes[0].map_values[1].values == [
        "buy",
        "kaufen",
        "comprare",
        "acheter"
    ]
    assert configs[2].custom_attributes[0].map_values[1].name == "buy"
    assert configs[2].custom_attributes[1].name == "real_estate_filter_category"
    assert configs[2].custom_attributes[1].target_external_id_name is None
    assert configs[2].custom_attributes[1].display_name == "Filter: Category"
    assert configs[2].custom_attributes[1].category == "Real Estate Features"
    assert configs[2].custom_attributes[1].active is False
    assert configs[2].custom_attributes[1].external_id_name is None
    assert configs[2].custom_attributes[1].raw_data_format is None
    assert configs[2].custom_attributes[1].incremental is None
    assert configs[2].custom_attributes[1].type == CustomAttributeType.tracking
    assert configs[2].custom_attributes[1].id_pii is None
    assert configs[2].custom_attributes[1].value_pii is False
    assert configs[2].custom_attributes[1].s3_predictions_params_path is None
    assert configs[2].custom_attributes[1].query.conditions[0].condition.operator == "in"
    assert configs[2].custom_attributes[1].query.conditions[0].condition.value == [
        "alle-immobilien.ch"
    ]
    assert configs[2].custom_attributes[1].query.conditions[0].condition.attribute == "app_id"
    assert configs[2].custom_attributes[1].query.conditions[0].result.type == "regex"
    assert configs[2].custom_attributes[1].query.conditions[0].result.pattern == "(?:affitta|mieten|rent|louer|acheter|kaufen|buy|compra)/(?!(?:kanton|cantone|cantons|canton)-)([^/]+)/"
    assert configs[2].custom_attributes[1].query.conditions[0].result.string == "page_url"
    assert configs[2].custom_attributes[1].query.conditions[1].condition.operator == "in"
    assert configs[2].custom_attributes[1].query.conditions[1].condition.value == [
        "homegate.ch",
        "immoscout24.ch"
    ]
    assert configs[2].custom_attributes[1].query.conditions[1].condition.attribute == "app_id"
    assert configs[2].custom_attributes[1].query.conditions[1].result.type == "jsonpath"
    assert configs[2].custom_attributes[1].query.conditions[1].result.jsonpath == "$.h_search_filter_category_075"
    assert configs[2].custom_attributes[1].query.conditions[1].result.string == "custom_tracking_attributes"
    assert configs[2].custom_attributes[1].query.result is None
    assert configs[2].custom_attributes[1].map_values is None
    assert configs[2].kropka_tenants == []
    assert configs[2].content_providers[0].name == "content-provider-3"
    assert configs[2].content_providers[0].section_prefixes == ["prefix_5", "prefix_6"]
    assert configs[2].content_providers[0].uri_prefixes == ["www.content-provider-3.ext"]
    assert configs[2].content_providers[0].source_system == "source_3"
    assert configs[2].content_providers[0].hardcoded_taxonomies is None
    assert configs[2].content_providers[0].is_uri_extracted_id_external_id is False
    assert configs[2].content_providers[0].canonical_id_extraction.uri_provider == "source_3~content-provider-3"
    assert configs[2].content_providers[0].canonical_id_extraction.id_regex is None
    assert configs[2].content_providers[0].canonical_id_extraction.use_uri_path_hash_as_extracted_id is True
    assert configs[2].content_providers[0].app_ids is None
    assert configs[2].tracking_providers is None
