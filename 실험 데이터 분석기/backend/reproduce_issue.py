import requests
import os

URL = "http://localhost:8000/api/generate/extract-manual"
PDF_PATH = "test_data/manual_test.pdf"

def main():
    if not os.path.exists(PDF_PATH):
        print("PDF not found. Run create_test_pdf.py first.")
        return

    print(f"Sending {PDF_PATH} to {URL}...")
    try:
        with open(PDF_PATH, "rb") as f:
            files = {"file": f}
            response = requests.post(URL, files=files)
            
        print(f"Status Code: {response.status_code}")
        print("Response Body:")
        print(response.text)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
