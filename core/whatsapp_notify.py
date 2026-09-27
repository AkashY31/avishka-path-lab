"""
WhatsApp notification via CallMeBot API (free).

One-time setup for the lab owner:
  1. Save +34 644 60 49 14 in your phone contacts (name: CallMeBot)
  2. Send this exact message via WhatsApp to that number:
       I allow callmebot to send me messages
  3. You'll receive an API key — save it as CALLMEBOT_API_KEY in .env

Docs: https://www.callmebot.com/blog/free-api-whatsapp-messages/
"""

import os
import urllib.request
import urllib.parse
from datetime import datetime


LAB_WHATSAPP = os.getenv("LAB_WHATSAPP_NUMBER", "")   # e.g. 917355230710 (with country code, no +)
CALLMEBOT_KEY = os.getenv("CALLMEBOT_API_KEY", "")


def send_whatsapp(message: str) -> bool:
    """
    Send a WhatsApp message to the lab owner via CallMeBot.
    Returns True on success, False if not configured or fails.
    """
    if not LAB_WHATSAPP or not CALLMEBOT_KEY:
        print("[WhatsApp] LAB_WHATSAPP_NUMBER or CALLMEBOT_API_KEY not set — skipping.")
        return False

    try:
        encoded_msg = urllib.parse.quote(message)
        url = (
            f"https://api.callmebot.com/whatsapp.php"
            f"?phone={LAB_WHATSAPP}&text={encoded_msg}&apikey={CALLMEBOT_KEY}"
        )
        with urllib.request.urlopen(url, timeout=10) as resp:
            status = resp.status
        print(f"[WhatsApp] Notification sent (HTTP {status})")
        return status == 200
    except Exception as e:
        print(f"[WhatsApp] Failed to send notification: {e}")
        return False


def send_booking_whatsapp(booking_data: dict) -> bool:
    """Send a formatted booking notification to the lab via WhatsApp."""
    tests_str = ", ".join(t["name"] for t in booking_data.get("tests", []))
    message = (
        f"🔬 *NEW BOOKING — Avishka Pathology*\n\n"
        f"📋 Ref: {booking_data['reference']}\n"
        f"👤 Patient: {booking_data['patient_name']}\n"
        f"📞 Phone: {booking_data['phone']}\n"
        f"📅 Slot: {booking_data['appointment_date']} at {booking_data['appointment_slot']}\n"
        f"🧪 Tests: {tests_str}\n"
        f"💰 Total: ₹{booking_data['total_cost']:.0f}\n"
        f"⏰ Received: {datetime.now().strftime('%d %b %Y, %I:%M %p')}\n\n"
        f"➡️ Please call {booking_data['phone']} to confirm."
    )
    return send_whatsapp(message)


def send_contact_whatsapp(contact_data: dict) -> bool:
    """Send a contact form notification to the lab via WhatsApp."""
    message = (
        f"📨 *CONTACT FORM — Avishka Pathology*\n\n"
        f"👤 Name: {contact_data['name']}\n"
        f"📞 Phone: {contact_data.get('phone', '—')}\n"
        f"📧 Email: {contact_data.get('email', '—')}\n"
        f"📌 Subject: {contact_data.get('subject', '—')}\n"
        f"💬 Message: {contact_data.get('message', '—')}\n"
        f"⏰ {datetime.now().strftime('%d %b %Y, %I:%M %p')}"
    )
    return send_whatsapp(message)
