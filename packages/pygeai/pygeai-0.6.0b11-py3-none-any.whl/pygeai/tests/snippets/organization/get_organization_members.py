from pygeai.organization.managers import OrganizationManager

manager = OrganizationManager()

response = manager.get_organization_members(organization_id="4aa15b61-d3c7-4a5c-99b8-052d18a04ff2")
print(f"response: {response}")
