### test create and retrieve a FHIR resource
import unittest

from fhir.resources.patient import Patient
from services.fhir import FHIRClient


class TestFHIRClient(unittest.TestCase):
    def setUp(self):
        self.fhir_client = FHIRClient()  # Adjust base URL as needed

    def test_create_and_retrieve_patient(self):
        # Create a new Patient resource
        patient = Patient(
            id="test-patient",
            name=[{"family": "Doe", "given": ["John"]}],
        )
        created_patient = self.fhir_client.create_resource(patient)

        retrieved_patient = self.fhir_client.get_resource("Patient", created_patient.id)
        self.assertEqual(retrieved_patient.id, created_patient.id)
        self.assertEqual(retrieved_patient.name[0].family, "Doe")
        self.assertEqual(retrieved_patient.name[0].given[0], "John")
