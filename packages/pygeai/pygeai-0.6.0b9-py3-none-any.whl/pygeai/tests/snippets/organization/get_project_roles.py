from pygeai.organization.managers import OrganizationManager

manager = OrganizationManager(alias="sdkorg")

response = manager.get_project_roles(project_id="2ca6883f-6778-40bb-bcc1-85451fb11107")
print(f"response: {response}")
