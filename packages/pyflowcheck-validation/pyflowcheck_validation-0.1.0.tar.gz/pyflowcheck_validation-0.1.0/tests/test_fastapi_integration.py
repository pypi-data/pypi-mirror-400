from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
import pytest
from py_flowcheck import Schema

app = FastAPI()

request_schema = Schema({
    "user_id": int,
    "action": str
})

response_schema = Schema({
    "success": bool,
    "message": str
})

@app.post("/action")
async def perform_action(request: Request):
    data = await request.json()
    
    # Manual validation for testing
    request_schema.validate(data)
    
    result = {"success": True, "message": "Action performed"}
    
    # Manual validation for testing
    response_schema.validate(result)
    
    return result

client = TestClient(app)

def test_perform_action_create():
    response = client.post("/action", json={"user_id": 1, "action": "create"})
    assert response.status_code == 200

def test_perform_action_update():
    response = client.post("/action", json={"user_id": 1, "action": "update"})
    assert response.status_code == 200

def test_perform_action_delete():
    response = client.post("/action", json={"user_id": 1, "action": "delete"})
    assert response.status_code == 200