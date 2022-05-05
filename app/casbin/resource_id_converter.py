from app.casbin.role_definition import ResourceDomainEnum


def get_resource_id_from_item_id(item_id: str, domain: ResourceDomainEnum) -> str:
    return domain + item_id


def get_item_id_from_resource_id(resource_id: str, domain: ResourceDomainEnum) -> str:
    if resource_id.startswith(domain):
        return resource_id[len(domain) :]
    else:
        raise Exception("resource id not starting with resource name..")
