import requests
from fhir.resources import get_fhir_model_class
from fhir.resources.resource import Resource

FHIR_BASE_URL = "http://localhost:8080/fhir"  # or your actual base URL


class FHIRClient:
    def __init__(self, base_url=FHIR_BASE_URL):
        self.base_url = base_url

    def get_resource_by_id(self, resource_type, resource_id) -> Resource:
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
    
    def search_resource_by_identifier(self, resource_type: str, identifier: str) -> Resource:
        """
        Search for a FHIR resource by its identifier.
        """
        url = f"{self.base_url}/{resource_type}?identifier={identifier}"
        response = requests.get(url)
        if response.status_code == 200:
            resources = response.json().get("entry", [])
            if resources:
                resource_json = resources[0]["resource"]
                resource_class = get_fhir_model_class(resource_type)
                return resource_class(**resource_json)
            else:
                raise ValueError(f"No {resource_type} found with identifier: {identifier}")
        else:
            response.raise_for_status()


    def _create_resource(self, resource: Resource) -> Resource:
        """
        Create a new FHIR resource.
        """
        url = f"{self.base_url}/{resource.get_resource_type()}"
        headers = {"Content-Type": "application/fhir+json"}
        response = requests.post(url, data=resource.model_dump_json(), headers=headers)
        if response.status_code in (201, 200):
            resource_json = response.json()
            resource_class = get_fhir_model_class(resource.get_resource_type())
            return resource_class(**resource_json)
        else:
            response.raise_for_status()

    def _update_resource(self, resource: Resource) -> Resource:
        """Update an existing FHIR resource."""
        url = f"{self.base_url}/{resource.get_resource_type()}/{resource.id}"
        headers = {"Content-Type": "application/fhir+json"}
        response = requests.put(url, data=resource.model_dump_json(), headers=headers)
        if response.status_code in (200, 204):
            resource_json = response.json()
            resource_class = get_fhir_model_class(resource.get_resource_type())
            return resource_class(**resource_json)
        else:
            response.raise_for_status()

    def search_patient_by_user_id(self, user_id: str) -> Resource:
        """
        Search for a Patient resource by user ID.
        """
        return self.search_resource_by_identifier("Patient", user_id)
    
    def get_placeholder_mapping(self, user_id: str) -> dict:
        """
        Retrieve a mapping of placeholders to actual values for a given user ID.
        This is a placeholder implementation and should be replaced with actual logic.
        """
        # Example mapping, replace with actual logic
        patient_id = self.search_patient_by_user_id(user_id).id
        return {
            "<patient_id>": patient_id,
        }
    
    def create_resource(self, resource_data: dict, user_id: str) -> Resource:
        """
        Create a new FHIR resource of the specified type with the provided data.
        Placeholders in the data will be replaced with actual values from the mapping.
        """
        mapping = self.get_placeholder_mapping(user_id)
        resource_data = replace_placeholders(resource_data, mapping)
        resource_type = resource_data.get("resourceType")
        resource = get_fhir_model_class(resource_type)(**resource_data)
        return self._create_resource(resource)


def replace_placeholders(resource_dict: dict, mapping: dict) -> dict:
    
    def _replace(obj):
        if isinstance(obj, dict):
            return {k: _replace(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [_replace(i) for i in obj]
        elif isinstance(obj, str):
            for placeholder, real in mapping.items():
                obj = obj.replace(placeholder, real)
            return obj
        else:
            return obj
    
    return _replace(resource_dict)


    
 