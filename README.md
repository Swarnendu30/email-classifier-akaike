# 📧 Email Processing API

This project is a FastAPI-based microservice that processes raw email text. It does two things:
- 🔒 **Masks personally identifiable information (PII)** such as name, phone number, email-id etc. and **Payment Card Industry (PCI) information** like card nubmer, CVV, etc.
- 🧠 **Classifies** the email into one or multiple out of **8 fixed categories** based on its content.

✅ Deployed on Hugging Face Spaces for public access and testing.

---

## 🌍 Live Demo (Hugging Face Space)

You can test the API online: 
- FastAPI GUI: https://swarnendub30-akaike-proj.hf.space/docs
- API Deployment link: https://swarnendub30-akaike-proj.hf.space/process-email
