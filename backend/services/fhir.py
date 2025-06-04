import requests
from fhir.resources import get_fhir_model_class
from fhir.resources.resource import Resource

FHIR_BASE_URL = "http://localhost:8080/fhir"  # or your actual base URL


class FHIRClient:
    def __init__(self, base_url=FHIR_BASE_URL):
        self.base_url = base_url

    def get_resource(self, resource_type, resource_id) -> Resource:
        """
        Retrieve a FHIR resource by type and ID.
        """
        url = f"{self.base_url}/{resource_type}/{resource_id}"
        response = requests.get(url)
        if response.status_code == 200:
            resource_json = response.json()
            resource_class = get_fhir_model_class(resource_type)
            return resource_class(**resource_json)
        else:
            response.raise_for_status()

    def create_resource(self, resource: Resource) -> Resource:
        """
        Create a new FHIR resource.
        """
        url = f"{self.base_url}/{resource.get_resource_type()}"
        headers = {"Content-Type": "application/fhir+json"}
        response = requests.post(url, json=resource.model_dump(), headers=headers)
        if response.status_code in (201, 200):
            resource_json = response.json()
            resource_class = get_fhir_model_class(resource.get_resource_type())
            return resource_class(**resource_json)
        else:
            response.raise_for_status()
