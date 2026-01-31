"""
Gemini AI 고찰 생성 테스트
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_generate_discussion():
    """AI 고찰 생성 테스트"""
    
    # 테스트용 통계 데이터
    test_data = {
        "experiment_title": "RC 회로 시정수 측정 실험",
        "statistics": {
            "slope": 10.018,
            "intercept": 0.0,
            "r_squared": 0.9994,
            "std_error": 0.086,
            "error_rate_percent": 0.18,
            "data_points": 10,
            "x_range": [0.1, 1.0],
            "y_range": [1.0, 10.0]
        },
        "context": "이 실험은 RC 회로에서 커패시터의 충전/방전 특성을 측정하는 실험입니다."
    }
    
    print("=== AI 고찰 생성 테스트 ===\n")
    print(f"실험 제목: {test_data['experiment_title']}")
    print(f"R²: {test_data['statistics']['r_squared']}")
    print(f"기울기: {test_data['statistics']['slope']}")
    print()
    
    response = requests.post(
        f"{BASE_URL}/api/generate/discussion",
        json=test_data,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"Success: {result['success']}")
        print(f"Model Used: {result['model_used']}")
        print()
        print("=== 생성된 고찰 ===")
        print(result['discussion'][:500] + "..." if len(result['discussion']) > 500 else result['discussion'])
    else:
        print(f"Error: {response.text}")

if __name__ == "__main__":
    test_generate_discussion()
