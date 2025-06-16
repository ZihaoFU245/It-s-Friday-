import unittest
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.db.database import Base, engine, SessionLocal
from app.db.models import Contact as ORMContact
from app.modules.contact_booklet import Contact, ContactManager

class TestContactManager(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Create tables
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
        cls.manager = ContactManager()

    def setUp(self):
        # Clear contacts before each test
        session = SessionLocal()
        session.query(ORMContact).delete()
        session.commit()
        session.close()

    def test_add_and_load_contact(self):
        contact = Contact(
            surname="Doe",
            forename="John",
            other_names=["Johnny"],
            email="john@example.com",
            phone="1234567890",
            address="123 Main St",
            tags=["friend"],
            others={"note": "Test contact"}
        )
        contact_id = self.manager.add_contact(contact)
        self.assertIsInstance(contact_id, int)
        contacts = self.manager.load_contacts()
        self.assertEqual(len(contacts), 1)
        self.assertEqual(contacts[0].surname, "Doe")
        self.assertEqual(contacts[0].forename, "John")

    def test_update_contact(self):
        contact = Contact(
            surname="Smith",
            forename="Jane",
            other_names=[],
            email="jane@example.com",
            phone="9876543210",
            address=None,
            tags=[],
            others={}
        )
        contact_id = self.manager.add_contact(contact)
        updated = Contact(
            surname="Smith",
            forename="Janet",
            other_names=["Jan"],
            email="janet@example.com",
            phone="9876543210",
            address="456 Elm St",
            tags=["colleague"],
            others={"department": "HR"}
        )
        result = self.manager.update_contact(contact_id, updated)
        self.assertTrue(result)
        contacts = self.manager.load_contacts()
        self.assertEqual(contacts[0].forename, "Janet")
        self.assertEqual(contacts[0].email, "janet@example.com")

    def test_delete_contact(self):
        contact = Contact(
            surname="Brown",
            forename="Charlie",
            other_names=[],
            email="charlie@example.com",
            phone="5555555555",
            address=None,
            tags=[],
            others={}
        )
        self.manager.add_contact(contact)
        deleted = self.manager.delete_contact("Brown")
        self.assertGreaterEqual(deleted, 1)
        contacts = self.manager.load_contacts()
        self.assertEqual(len(contacts), 0)

if __name__ == "__main__":
    unittest.main()
