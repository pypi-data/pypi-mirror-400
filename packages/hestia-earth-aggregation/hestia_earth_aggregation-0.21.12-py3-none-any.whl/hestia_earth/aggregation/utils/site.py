from typing import Dict
from collections import Counter
from functools import reduce
from hestia_earth.schema import SchemaType, SiteDefaultMethodClassification
from hestia_earth.utils.tools import non_empty_list, to_precision, list_sum
from hestia_earth.utils.model import linked_node

from . import _aggregated_node, sum_data, _aggregated_version, format_aggregated_list
from .term import _format_country_name, get_by_id
from .queries import find_regions_by_ids
from .source import format_aggregated_sources
from .measurement import new_measurement
from .management import new_management


def _format_aggregate(new_func: dict):
    def format(aggregate: dict):
        return _aggregated_version(new_func(aggregate))

    return format


def format_site_results(data: dict):
    measurements = list(
        map(_format_aggregate(new_measurement), data.get("measurements", []))
    )
    management = list(
        map(_format_aggregate(new_management), data.get("management", []))
    )
    return ({"measurements": measurements} if measurements else {}) | (
        {"management": management} if management else {}
    )


def format_site(site_data: dict, sites: list):
    sites = sites or [site_data]
    return (
        create_site(sites[0])
        | format_site_results(site_data)
        | {
            "aggregatedSites": format_aggregated_list("Site", sites),
            "aggregatedSources": format_aggregated_sources(sites, "defaultSource"),
            "numberOfSites": sum_data(sites, "numberOfSites"),
        }
    )


def _site_id(n: dict, include_siteType: bool):
    return "-".join(
        non_empty_list(
            [_format_country_name(n), n.get("siteType") if include_siteType else None]
        )
    )


def _site_name(n: dict, include_siteType: bool):
    return " - ".join(
        non_empty_list(
            [
                _format_country_name(n, as_id=False),
                n.get("siteType") if include_siteType else None,
            ]
        )
    )


def _get_country_from_id(term_id: str):
    country_id = term_id if term_id.startswith("region") else term_id[0:8]
    return get_by_id(country_id)


def _site_country_region(data: dict):
    # if region is level > 0, then need to add region and country
    return ({"region": linked_node(data)} if data.get("gadmLevel", 0) > 0 else {}) | (
        {
            "country": linked_node(
                data
                if data.get("gadmLevel", 0) == 0
                else _get_country_from_id(data.get("@id", ""))
            )
        }
    )


def create_site(data: dict, include_siteType=True):
    site = {"type": SchemaType.SITE.value}
    site["siteType"] = data["siteType"]
    site["name"] = _site_name(data, include_siteType)
    site["id"] = _site_id(data, include_siteType)
    site["defaultMethodClassification"] = SiteDefaultMethodClassification.MODELLED.value
    site["defaultMethodClassificationDescription"] = "aggregated data"
    site["dataPrivate"] = False
    site["aggregatedDataValidated"] = False
    return _aggregated_node(site) | _site_country_region(data["country"])


def update_site(country: dict, source: dict = None, include_siteType=True):
    def update(site: dict):
        site = site | _site_country_region(country)
        site["name"] = _site_name(site, include_siteType)
        site["id"] = _site_id(site, include_siteType)
        return site | ({} if source is None else {"defaultSource": source})

    return update


def _parent_region_id(region_id: str):
    parts = region_id.split(".")
    return (
        region_id
        if len(parts) == 1
        else ".".join([parts[0], f"{parts[1]}{'' if '_1' in parts[1] else '_1'}"])
    )


def site_parent_region_id(site: dict):
    # site can be a combined site, in which case the region is a dict without `@id`
    region_id = (site.get("region") or site.get("country")).get("@id")
    return None if region_id is None else _parent_region_id(region_id)


def _format_description(region: Dict[str, int]):
    total = sum(region.values())
    description = ";".join(
        [f"{k}: {to_precision(v * 100 / total, 2)}" for k, v in region.items()]
    )
    return {"description": description}


def _parse_region(site: dict, use_description: bool = True):
    description = site.get("description")
    return (
        {
            region.split(": ")[0]: float(region.split(": ")[1])
            for region in description.split(";")
        }
        if description and use_description
        else {site.get("country", {}).get("name"): 100}
    )


def format_site_description_weighted(
    sites: list, weights: dict, use_description: bool = True
):
    total_weight = list_sum(non_empty_list([w.get("weight") for w in weights.values()]))
    regions = [
        Counter(
            {
                name: value
                * weights.get(site.get("id") or site.get("@id"), {}).get("weight", 100)
                * 100
                / total_weight
            }
        )
        for site in sites
        for name, value in _parse_region(site, use_description=use_description).items()
        if name
    ]
    region = reduce(lambda prev, curr: prev + curr, regions, Counter({}))
    return _format_description(dict(region))


def format_site_description(region: Dict[str, int]):
    region_mapper = {v["@id"]: v["name"] for v in find_regions_by_ids(region.keys())}
    return _format_description({region_mapper[k]: v for k, v in region.items()})
