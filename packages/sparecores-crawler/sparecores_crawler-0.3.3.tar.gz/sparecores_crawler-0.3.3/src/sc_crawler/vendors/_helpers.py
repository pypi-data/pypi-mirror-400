"""Shared helpers for all vendors."""

from typing import List, Optional

from sc_crawler.tables import Region, Vendor


def convert_regions_to_zones(vendor: Vendor) -> List[dict]:
    """Create a dummy list of [zones][sc_crawler.tables.Zone] from the list of [regions][sc_crawler.tables.Region] of a [vendor][sc_crawler.tables.Vendor].

    Args:
        vendor: The [vendor][sc_crawler.tables.Vendor] to convert the regions of.

    Returns:
        A list of [zones][sc_crawler.tables.Zone] as [dict]s.
    """
    items = []
    for region in vendor.regions:
        items.append(
            {
                "vendor_id": vendor.vendor_id,
                "region_id": region.region_id,
                "zone_id": region.region_id,
                "name": region.name,
                "api_reference": region.name,
                "display_name": region.name,
            }
        )
    return items


def get_region_by_id(region_id: str, vendor: Vendor) -> Optional[Region]:
    """Get a [region][sc_crawler.tables.Region] by its ID or alias.

    Args:
        region_id: The ID or alias of the region to get.
        vendor: The [vendor][sc_crawler.tables.Vendor] to get the region from.

    Returns:
        The [region][sc_crawler.tables.Region] if found, otherwise None.
    """
    return next(
        (
            region
            for region in vendor.regions
            if (region_id in [region.api_reference, *region.aliases])
        ),
        None,
    )
