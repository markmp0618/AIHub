"""
Test PDF extraction from the backend
"""
import requests
from pathlib import Path
import io
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# 간단한 테스트 PDF 생성
def create_test_pdf():
    """간단한 실험 매뉴얼 PDF 생성"""
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    
    # 제목
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, 750, "RC 회로 실험 매뉴얼")
    
    # 실험 목적
    c.setFont("Helvetica-Bold", 14)
    c.drawString(100, 720, "1. 실험 목적")
    c.setFont("Helvetica", 12)
    text = "RC 회로의 시상수를 측정하고 이론값과 비교한다."
    c.drawString(120, 700, text)
    
    # 이론
    c.setFont("Helvetica-Bold", 14)
    c.drawString(100, 670, "2. 이론")
    c.setFont("Helvetica", 12)
    c.drawString(120, 650, "RC 회로의 시상수는 τ = RC로 정의된다.")
    c.drawString(120, 630, "충전 시 전압은 V(t) = V0(1 - e^(-t/τ))로 변화한다.")
    
    # 오차 원인
    c.setFont("Helvetica-Bold", 14)
    c.drawString(100, 600, "3. 주요 오차 원인")
    c.setFont("Helvetica", 12)
    c.drawString(120, 580, "- 접촉 저항: 회로 연결부의 접촉 불량")
    c.drawString(120, 560, "- 기기 오차: 오실로스코프의 측정 정밀도 한계")
    c.drawString(120, 540, "- 온도 변화: 실험 중 저항값 변화")
    
    # 기구
    c.setFont("Helvetica-Bold", 14)
    c.drawString(100, 510, "4. 실험 기구")
    c.setFont("Helvetica", 12)
    c.drawString(120, 490, "- 오실로스코프")
    c.drawString(120, 470, "- 함수 발생기")
    c.drawString(120, 450, "- 저항 (1kΩ)")
    c.drawString(120, 430, "- 커패시터 (100μF)")
    
    c.save()
    buffer.seek(0)
    return buffer.getvalue()


def test_pdf_endpoint():
    """PDF 추출 API 엔드포인트 테스트"""
    url = "http://localhost:8000/api/generate/extract-manual"
    
    print("[*] 테스트 PDF 생성 중...")
    pdf_bytes = create_test_pdf()
    
    print(f"PDF 크기: {len(pdf_bytes)} bytes")
    
    print("\n[*] API 호출 중...")
    files = {
        'file': ('test_manual.pdf', pdf_bytes, 'application/pdf')
    }
    
    try:
        response = requests.post(url, files=files, timeout=60)
        
        print(f"\n[*] 응답 상태 코드: {response.status_code}")
        print(f"응답 내용:\n{response.text[:500]}")
        
        if response.status_code == 200:
            data = response.json()
            print("\n[SUCCESS] 성공!")
            print(f"Success: {data.get('success')}")
            print(f"Message: {data.get('message')}")
            
            if 'data' in data and data['data']:
                manual_info = data['data']
                print("\n[*] 추출된 매뉴얼 정보:")
                print(f"실험 목적: {manual_info.get('experiment_purpose')}")
                print(f"이론: {manual_info.get('theory')[:100]}...")
                print(f"오차 가이드 수: {len(manual_info.get('error_guides', []))}")
                
                if manual_info.get('error_guides'):
                    print("\n오차 가이드:")
                    for i, eg in enumerate(manual_info['error_guides'], 1):
                        print(f"  {i}. {eg.get('cause')}: {eg.get('description')}")
                
                if manual_info.get('equipment_list'):
                    print(f"\n기구 목록: {manual_info['equipment_list']}")
        else:
            print(f"\n[ERROR] 실패!")
            print(f"응답: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("\n[ERROR] 연결 실패! 서버가 실행 중인지 확인하세요.")
        print("서버 시작 명령: uvicorn app.main:app --reload --port 8000")
    except Exception as e:
        print(f"\n[ERROR] 오류 발생: {str(e)}")


if __name__ == "__main__":
    print("=" * 60)
    print("PDF 매뉴얼 추출 테스트")
    print("=" * 60)
    test_pdf_endpoint()

