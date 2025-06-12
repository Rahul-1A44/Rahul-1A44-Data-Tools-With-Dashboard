# test_gmail_login.py
import smtplib
import os
from dotenv import load_dotenv

load_dotenv()

email = os.getenv("MAIL")
password = os.getenv("MAIL_PASS")

print("MAIL =", email)
print("MAIL_PASS =", password)

try:
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(email, password)
        print("✅ SUCCESS: Logged in to Gmail SMTP")
except Exception as e:
    print("❌ FAILED:", e)
