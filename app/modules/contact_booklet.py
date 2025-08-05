from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from app.db.database import SessionLocal, Base, engine
from app.db.models import Contact as ORMContact
import json

@dataclass
class Contact:
    surname: str
    forename: str
    other_names: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    others: Dict[str, Any] = field(default_factory=dict)
    email: Optional[str] = None
    address: Optional[str] = None  
    phone: Optional[str] = None
    id: Optional[int] = None  # Database ID, populated when loaded from DB

class ContactManager:
    def __init__(self):
        # Ensure all tables are created before using the session
        Base.metadata.create_all(bind=engine)
        self.db: Session = SessionLocal()

    def load_contacts(self, offset: int = 0, limit: int = 20):
        try:
            contacts = self.db.query(ORMContact).offset(offset).limit(limit).all()
            result = []
            for c in contacts:
                result.append(Contact(
                    surname=c.surname,
                    forename=c.forename,
                    other_names=json.loads(c.other_names) if c.other_names else [],
                    email=c.email,
                    phone=c.phone,
                    address=c.address,
                    tags=json.loads(c.tags) if c.tags else [],
                    others=json.loads(c.others) if c.others else {},
                    id=c.id
                ))
            return {'success': True, 'contacts': result}
        except Exception as e:
            return {'success': False, 'error': str(e), 'manager': 'ContactBookletService'}

    def add_contact(self, contact: Contact):
        try:
            db_contact = ORMContact(
                surname=contact.surname,
                forename=contact.forename,
                other_names=json.dumps(contact.other_names),
                email=contact.email,
                phone=contact.phone,
                address=contact.address,
                tags=json.dumps(contact.tags),
                others=json.dumps(contact.others)
            )
            self.db.add(db_contact)
            self.db.commit()
            self.db.refresh(db_contact)
            return {'success': True, 'contact_id': db_contact.id}
        except Exception as e:
            self.db.rollback()
            return {'success': False, 'error': str(e), 'manager': 'ContactBookletService'}

    def find_contact(self, name: str = None, contact_id: int = None, offset: int = 0, limit: int = 20):
        """
        Find contacts by name or ID.
        
        Args:
            name: Name to search for (searches both surname and forename)
            contact_id: Specific contact ID to find
            offset: Number of records to skip (for pagination)
            limit: Maximum number of records to return
            
        Returns:
            Dict with 'success' boolean and either 'contacts' list or 'error' message
        """
        try:
            if contact_id is not None:
                # Search by specific ID
                contact = self.db.query(ORMContact).filter(ORMContact.id == contact_id).first()
                if contact:
                    result = [Contact(
                        surname=contact.surname,
                        forename=contact.forename,
                        other_names=json.loads(contact.other_names) if contact.other_names else [],
                        email=contact.email,
                        phone=contact.phone,
                        address=contact.address,
                        tags=json.loads(contact.tags) if contact.tags else [],
                        others=json.loads(contact.others) if contact.others else {},
                        id=contact.id
                    )]
                    return {'success': True, 'contacts': result}
                else:
                    return {'success': True, 'contacts': []}
            elif name is not None:
                # Search by name
                query = self.db.query(ORMContact).filter(
                    (ORMContact.surname.ilike(f"%{name}%")) |
                    (ORMContact.forename.ilike(f"%{name}%"))
                )
                contacts = query.offset(offset).limit(limit).all()
                result = []
                for c in contacts:
                    result.append(Contact(
                        surname=c.surname,
                        forename=c.forename,
                        other_names=json.loads(c.other_names) if c.other_names else [],
                        email=c.email,
                        phone=c.phone,
                        address=c.address,
                        tags=json.loads(c.tags) if c.tags else [],
                        others=json.loads(c.others) if c.others else {},
                        id=c.id
                    ))
                return {'success': True, 'contacts': result}
            else:
                return {'success': False, 'error': 'Either name or contact_id must be provided', 'manager': 'ContactBookletService'}
        except Exception as e:
            return {'success': False, 'error': str(e), 'manager': 'ContactBookletService'}

    def delete_contact(self, name: str):
        try:
            contacts = self.db.query(ORMContact).filter(
                (ORMContact.surname.ilike(f"%{name}%")) |
                (ORMContact.forename.ilike(f"%{name}%"))
            )
            count = contacts.delete(synchronize_session=False)
            self.db.commit()
            return {'success': True, 'deleted': count}
        except Exception as e:
            self.db.rollback()
            return {'success': False, 'error': str(e), 'manager': 'ContactBookletService'}

    def update_contact(self, contact_id: int, updated: Contact):
        try:
            db_contact = self.db.query(ORMContact).filter(ORMContact.id == contact_id).first()
            if not db_contact:
                return {'success': False, 'error': 'Contact not found', 'manager': 'ContactBookletService'}
            db_contact.surname = updated.surname
            db_contact.forename = updated.forename
            db_contact.other_names = json.dumps(updated.other_names)
            db_contact.email = updated.email
            db_contact.phone = updated.phone
            db_contact.address = updated.address
            db_contact.tags = json.dumps(updated.tags)
            db_contact.others = json.dumps(updated.others)
            self.db.commit()
            return {'success': True}
        except Exception as e:
            self.db.rollback()
            return {'success': False, 'error': str(e), 'manager': 'ContactBookletService'}

    def get_contact_by_id(self, contact_id: int):
        """
        Get a single contact by its ID.
        
        Args:
            contact_id: The ID of the contact to retrieve
            
        Returns:
            Dict with 'success' boolean and either 'contact' object or 'error' message
        """
        try:
            db_contact = self.db.query(ORMContact).filter(ORMContact.id == contact_id).first()
            if not db_contact:
                return {'success': False, 'error': 'Contact not found', 'manager': 'ContactBookletService'}
            
            contact = Contact(
                surname=db_contact.surname,
                forename=db_contact.forename,
                other_names=json.loads(db_contact.other_names) if db_contact.other_names else [],
                email=db_contact.email,
                phone=db_contact.phone,
                address=db_contact.address,
                tags=json.loads(db_contact.tags) if db_contact.tags else [],
                others=json.loads(db_contact.others) if db_contact.others else {},
                id=db_contact.id
            )
            return {'success': True, 'contact': contact}
        except Exception as e:
            return {'success': False, 'error': str(e), 'manager': 'ContactBookletService'}