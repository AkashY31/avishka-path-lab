"""Contact form API — stores inquiries in SQLite."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from database.db import get_db
from database.models import Contact
from core.whatsapp_notify import send_contact_whatsapp
from core.email_notify import send_contact_email

router = APIRouter()


class ContactRequest(BaseModel):
    name: str
    email: str
    phone: str | None = None
    subject: str
    message: str


@router.post("/submit")
def submit_contact(req: ContactRequest, db: Session = Depends(get_db)):
    if len(req.message.strip()) < 10:
        raise HTTPException(status_code=400, detail="Message too short.")

    contact = Contact(
        name=req.name.strip(),
        email=req.email.strip().lower(),
        phone=req.phone,
        subject=req.subject.strip(),
        message=req.message.strip(),
    )
    db.add(contact)
    db.commit()

    import threading
    contact_data = {"name": req.name, "email": req.email, "phone": req.phone,
                    "subject": req.subject, "message": req.message}
    threading.Thread(target=send_contact_whatsapp, args=(contact_data,), daemon=True).start()
    threading.Thread(target=send_contact_email, args=(contact_data,), daemon=True).start()

    return {
        "success": True,
        "message": (
            f"Thank you, {req.name.split()[0]}! We've received your message. "
            "Our team will get back to you within 24 hours. "
            "For urgent queries, call 7355230710."
        ),
    }
