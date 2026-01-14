from pygeai.organization.managers import OrganizationManager

manager = OrganizationManager()

response = manager.get_project_memberships(
    email="user@example.com",
    start_page=1,
    page_size=10,
    order_key="projectName",
    order_direction="desc"
)
print(f"response: {response}")
