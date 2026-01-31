from reportlab.pdfgen import canvas
import os

def create_pdf(filename):
    c = canvas.Canvas(filename)
    c.drawString(100, 800, "Physics Experiment Manual: Simple Pendulum")
    c.drawString(50, 750, "1. Purpose: To determine g.")
    c.drawString(50, 700, "2. Theory: T = 2*pi*sqrt(L/g)")
    c.save()
    print(f"Created {filename}")

if __name__ == "__main__":
    os.makedirs("test_data", exist_ok=True)
    create_pdf("test_data/manual_test.pdf")
