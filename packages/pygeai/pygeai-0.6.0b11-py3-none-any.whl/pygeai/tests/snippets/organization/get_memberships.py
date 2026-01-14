from pygeai.organization.managers import OrganizationManager

manager = OrganizationManager(alias="sdkorg")

response = manager.get_memberships(
    email="alejandro.trinidad@globant.com",
    start_page=1,
    page_size=10,
    #order_key="organizationName",
    #order_direction="asc"
)
print(f"response: {response}")
