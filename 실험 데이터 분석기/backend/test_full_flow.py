"""
전체 E2E 플로우 테스트 스크립트
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_detect_sheets():
    """멀티시트 감지 테스트"""
    print("=" * 60)
    print("1. 멀티시트 감지 테스트")
    print("=" * 60)

    with open("test_data/multi_experiment.xlsx", "rb") as f:
        response = requests.post(
            f"{BASE_URL}/api/analyze/detect-sheets",
            files={"file": f}
        )

    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Sheets found: {data.get('total_sheets')}")
    for sheet in data.get("sheets", []):
        print(f"  - {sheet['sheet_name']}: {sheet['columns']}, {sheet['row_count']} rows")
    return data

def test_batch_analysis():
    """배치 분석 테스트"""
    print("\n" + "=" * 60)
    print("2. 배치 분석 테스트")
    print("=" * 60)

    experiments = [
        {
            "sheet_name": "단진자실험",
            "experiment_name": "단진자 주기-길이 관계",
            "x_column": "길이(m)",
            "y_column": "주기제곱(s^2)"
        },
        {
            "sheet_name": "옴의법칙",
            "experiment_name": "옴의 법칙 검증",
            "x_column": "전압(V)",
            "y_column": "전류(mA)"
        },
        {
            "sheet_name": "자유낙하",
            "experiment_name": "자유 낙하 운동",
            "x_column": "시간(s)",
            "y_column": "거리(m)"
        }
    ]

    report_title = "물리학 실험 종합 리포트"

    with open("test_data/multi_experiment.xlsx", "rb") as f:
        response = requests.post(
            f"{BASE_URL}/api/analyze/batch",
            files={"file": f},
            data={
                "experiments_json": json.dumps(experiments),
                "report_title": report_title
            }
        )

    print(f"Status: {response.status_code}")
    data = response.json()

    if data.get("success"):
        batch_data = data.get("data", {})
        print(f"Batch ID: {batch_data.get('batch_id')}")
        print(f"Total experiments: {batch_data.get('total_experiments')}")
        for exp in batch_data.get("experiments", []):
            stats = exp.get("statistics", {})
            print(f"\n  {exp['experiment_name']}:")
            print(f"    R² = {stats.get('r_squared', 0):.6f}")
            print(f"    slope = {stats.get('slope', 0):.6f}")
            print(f"    Graph generated: {'Yes' if exp.get('graph', {}).get('image_base64') else 'No'}")
    else:
        print(f"Error: {data.get('message')}")
        print(json.dumps(data, indent=2, ensure_ascii=False))

    return data

def test_full_report(batch_data):
    """전체 리포트 생성 테스트"""
    print("\n" + "=" * 60)
    print("3. 전체 리포트 생성 테스트")
    print("=" * 60)

    if not batch_data.get("success"):
        print("배치 분석 실패로 리포트 생성 테스트 스킵")
        return None

    batch = batch_data.get("data", {})

    request_body = {
        "batch_id": batch.get("batch_id"),
        "report_title": batch.get("report_title"),
        "experiments": batch.get("experiments"),
        "options": {
            "language": "ko",
            "include_data_tables": True,
            "tone": "academic"
        }
    }

    response = requests.post(
        f"{BASE_URL}/api/generate/full-report",
        json=request_body
    )

    print(f"Status: {response.status_code}")
    data = response.json()

    if data.get("success"):
        print(f"Report generated successfully!")
        md_content = data.get("markdown_content", "")
        print(f"Markdown length: {len(md_content)} characters")
        print(f"\nFirst 500 chars of report:")
        print("-" * 40)
        print(md_content[:500] if md_content else "No content")
    else:
        print(f"Error: {data.get('message')}")

    return data

def main():
    print("=" * 60)
    print("LabReportAI E2E 플로우 테스트")
    print("=" * 60)

    # 1. 멀티시트 감지
    sheets_data = test_detect_sheets()

    # 2. 배치 분석
    batch_data = test_batch_analysis()

    # 3. 전체 리포트 생성
    report_data = test_full_report(batch_data)

    print("\n" + "=" * 60)
    print("테스트 완료!")
    print("=" * 60)

if __name__ == "__main__":
    main()
