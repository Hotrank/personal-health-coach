### test create and retrieve a FHIR resource
import unittest

from fhir.resources.patient import Patient
from services.fhir import FHIRClient


class TestFHIRClient(unittest.TestCase):
    def setUp(self):
        self.fhir_client = FHIRClient()  # Adjust base URL as needed

    def test_create_update_read_patient(self):
        # Create a new Patient resource
        patient = Patient(
            id="test-patient",
            name=[{"family": "Doe", "given": ["John"]}],
        )
        created_patient = self.fhir_client.create_resource(patient)
        self.assertEqual(created_patient.name[0].family, "Doe")
        self.assertEqual(created_patient.name[0].given[0], "John")

        # Update the Patient resource
        created_patient.name[0].given[0] = "Jane"
        updated_patient = self.fhir_client.update_resource(created_patient)

        self.assertEqual(updated_patient.name[0].given[0], "Jane")

        retrieved_patient = self.fhir_client.get_resource("Patient", created_patient.id)
        self.assertEqual(retrieved_patient.id, created_patient.id)
        self.assertEqual(retrieved_patient.name[0].family, "Doe")
        self.assertEqual(retrieved_patient.name[0].given[0], "Jane")
