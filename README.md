# 🧰 Data Tools with Dashboard

A comprehensive Django-based dashboard web application that allows users to authenticate via Gmail, upload files (PDFs), convert them, and manage data through an interactive and user-friendly interface. This project is designed for small data processing tasks, document handling, and efficient user interaction via a modern dashboard layout.



## 🎯 Project Objectives

- Provide an all-in-one **file management and conversion tool** via a web dashboard.
- Enable secure **Gmail login integration** using Django AllAuth.
- Offer **media upload and storage** capabilities.
- Deliver a clean and responsive **dashboard interface** for interaction.
- Make data manipulation tasks easy for non-technical users via an intuitive UI.

---

## ✨ Features

| Feature | Description |
|--------|-------------|
| 🔐 Gmail Login | Secure authentication using Google (OAuth) |
| 📄 PDF File Upload | Users can upload PDF files from local system |
| 🔁 PDF Conversion | Converts uploaded files to a processed output format (e.g., extracted text or renamed PDFs) |
| 📁 Media Storage | Uploaded files are saved in a media directory and accessible from the dashboard |
| 📊 Dashboard Interface | View uploaded files, interact with conversion tools, manage data |
| 🧾 Logging & Tracking | Track file conversions by timestamp and filename |
| 🧪 File Processing Scripts | Python-based logic to process PDF files (like renaming or extracting data) |
| ⚙️ Admin Panel | Django admin enabled for superuser access |

---

## 🛠️ Tech Stack

- **Backend:** Python 3, Django
- **Frontend:** HTML5, CSS3, Bootstrap (or Tailwind if used), JavaScript
- **Authentication:** Django AllAuth with Google OAuth
- **Database:** SQLite3 (can be upgraded to PostgreSQL for production)
- **File Handling:** Python’s built-in `os`, `datetime`, `PyPDF2` (if used for PDF parsing)
- **Hosting:** GitHub (for code); locally run using Django's development server

---

## 🧱 Project Structure

