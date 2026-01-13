from aliyunsdkbssopenapi.request.v20171214 import DescribePricingModuleRequest
from aliyunsdkcore.acs_exception.exceptions import ServerException
from aliyunsdkcore.request import CommonRequest
from aliyunsdkecs.request.v20140526 import (
    DescribeInstanceTypesRequest,
    DescribePriceRequest,
    DescribeZonesRequest,
)


def get_zones(tempcl):
    """
    Gathers the zones available in given region. Takes a client object as a parameter. Returns a dictionary with zone info.
    """
    # client = get_client()
    region_list = get_regions(one_region_query=ONE_REGION_QUERY)
    request = DescribeZonesRequest.DescribeZonesRequest()
    response = tempcl.do_action_with_exception(request)
    zone_info_in_list = json.loads(response.decode("utf-8"))
    return zone_info_in_list


def get_instance_types(tempclient):
    """
    Gathers the available ECS instance types available in the given region. Receives a client object as a parameter. Returns a dictionary with instance type info.
    """
    request = DescribeInstanceTypesRequest.DescribeInstanceTypesRequest()
    response = tempclient.do_action_with_exception(request)
    instance_type_info_in_list = json.loads(response.decode("utf-8"))
    return instance_type_info_in_list


def get_disk_capabilities(tempclient):
    """
    Gathers information on pricing data on modules related to ECS instances. Returns a dictionary with disk info.
    """
    req = DescribePricingModuleRequest.DescribePricingModuleRequest()
    req.set_ProductCode("ecs")
    req.set_SubscriptionType("PayAsYouGo")
    response = tempclient.do_action_with_exception(req)
    return json.loads(response.decode("utf-8"))


def get_instance_price(tempclient, instance_type):
    """
    Gathers information on pricing data of ECS instances. Returns a dictionary with price info. (Deprecated)
    """
    request = DescribePriceRequest.DescribePriceRequest()
    request.set_InstanceType(instance_type)
    request.set_SystemDiskCategory("cloud_ssd")
    request.set_SystemDiskSize(50)  # above minimum system disk size
    response = tempclient.do_action_with_exception(request)
    return json.loads(response.decode("utf-8"))


def get_instance_price_with_sku_price_list(tempclient, next_token=None):
    """
    Gathers information on pricing data of ECS instances by using CommonRequest, targeting the QuerySkuPriceList endpoint. Returns a dictionary with price info of 50 instances, and the query gets called again until the next_token is not present in the previous query.
    """
    request = CommonRequest()
    request.set_accept_format("json")
    request.set_domain("business.ap-southeast-1.aliyuncs.com")
    request.set_version("2017-12-14")
    request.set_action_name("QuerySkuPriceList")
    request.set_method("GET")

    request.add_query_param("CommodityCode", "ecs_intl")
    request.add_query_param("PriceEntityCode", "instance_type")
    request.add_query_param("PageSize", "50")
    request.add_query_param("Lang", "en")

    if next_token:
        request.add_query_param("NextPageToken", next_token)
    try:
        response = tempclient.do_action_with_exception(request)
    except ServerException as se:
        logger.error("unexpected error while getting sku price.")
        logger.debug(se)
        return {}

    return json.loads(response.decode("utf-8"))
