import requests

def test_generate_report():
    url = "http://localhost:8000/generate_report"
    payload = {
        "query": "오늘의 금융 시장 동향과 투자 전략을 분석하여 보고서를 작성해주세요",
        "date": "2025-05-18"
    }
    response = requests.post(url, json=payload)
    assert response.status_code == 200
    data = response.json()
    print(data)




if __name__ == "__main__":
    test_generate_report()