import requests

def test_generate_report():
    url = "http://localhost:8000/generate_report"
    payload = {
        "query": "GS 주식과 비트코인 전망에 대해서 알려주세요.",
        "date": "2025-05-27"
    }
    response = requests.post(url, json=payload)
    assert response.status_code == 200
    data = response.json()
    print(data)
    # assert data["status"] == "success"
    # assert "report" in data