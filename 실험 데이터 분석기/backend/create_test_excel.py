"""
멀티시트 테스트 Excel 파일 생성
"""

import pandas as pd
import numpy as np
import os

def create_test_excel():
    os.makedirs("test_data", exist_ok=True)

    # 실험 1: 단진자 실험 (주기 vs 길이)
    np.random.seed(42)
    length = np.array([0.2, 0.4, 0.6, 0.8, 1.0, 1.2])
    period_squared = 4 * np.pi**2 / 9.8 * length + np.random.normal(0, 0.01, len(length))
    df1 = pd.DataFrame({
        "길이(m)": length,
        "주기제곱(s^2)": period_squared
    })

    # 실험 2: 옴의 법칙 (전압 vs 전류)
    voltage = np.array([1.0, 2.0, 3.0, 4.0, 5.0, 6.0])
    resistance = 100  # 100 ohm
    current = voltage / resistance * 1000 + np.random.normal(0, 0.2, len(voltage))  # mA
    df2 = pd.DataFrame({
        "전압(V)": voltage,
        "전류(mA)": current
    })

    # 실험 3: 자유 낙하 (시간 vs 거리)
    time = np.array([0.1, 0.2, 0.3, 0.4, 0.5])
    distance = 0.5 * 9.8 * time**2 + np.random.normal(0, 0.005, len(time))
    df3 = pd.DataFrame({
        "시간(s)": time,
        "거리(m)": distance
    })

    # Excel 파일로 저장 (멀티시트)
    filepath = "test_data/multi_experiment.xlsx"
    with pd.ExcelWriter(filepath, engine="openpyxl") as writer:
        df1.to_excel(writer, sheet_name="단진자실험", index=False)
        df2.to_excel(writer, sheet_name="옴의법칙", index=False)
        df3.to_excel(writer, sheet_name="자유낙하", index=False)

    print(f"Created: {filepath}")
    print(f"Sheets: 단진자실험, 옴의법칙, 자유낙하")

if __name__ == "__main__":
    create_test_excel()
