from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
import requests
import os

# Load Environment Variables


load_dotenv()

API_KEY = os.getenv("API_KEY")
BASE_ID = os.getenv("BASE_ID")
TABLE_ID = os.getenv("TABLE_ID")

BASE_URL = f"https://api.airtable.com/v0/{BASE_ID}/{TABLE_ID}"

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# FastAPI App


app = FastAPI(
    title="Student CRUD API",
    description="FastAPI CRUD using Airtable",
    version="1.0"
)

# Student Model


class Student(BaseModel):
    student_id: int
    name: str
    age: int


# Helper Function


def find_airtable_record(student_id: int):
    """
    Find Airtable record by StudentID
    """

    response = requests.get(
        BASE_URL,
        headers=HEADERS
    )

    if response.status_code != 200:
        raise HTTPException(
            status_code=response.status_code,
            detail=response.text
        )

    records = response.json().get("records", [])

    for record in records:
        fields = record.get("fields", {})

        if fields.get("StudentID") == student_id:
            return record["id"]

    return None


# CREATE Student


@app.post("/students")
def create_student(student: Student):

    payload = {
        "fields": {
            "StudentID": student.student_id,
            "Name": student.name,
            "Age": student.age
        }
    }

    response = requests.post(
        BASE_URL,
        headers=HEADERS,
        json=payload
    )

    if response.status_code == 200:
        return {
            "message": "Student created successfully",
            "data": response.json()
        }

    raise HTTPException(
        status_code=response.status_code,
        detail=response.text
    )


# READ All Students

@app.get("/students")
def get_all_students():

    response = requests.get(
        BASE_URL,
        headers=HEADERS
    )

    if response.status_code == 200:
        return response.json()["records"]

    raise HTTPException(
        status_code=response.status_code,
        detail=response.text
    )


# READ Single Student


@app.get("/students/{student_id}")
def get_student(student_id: int):

    response = requests.get(
        BASE_URL,
        headers=HEADERS
    )

    if response.status_code != 200:
        raise HTTPException(
            status_code=response.status_code,
            detail=response.text
        )

    records = response.json()["records"]

    for record in records:
        fields = record.get("fields", {})

        if fields.get("StudentID") == student_id:
            return record

    raise HTTPException(
        status_code=404,
        detail="Student not found"
    )


# UPDATE Student


@app.put("/students/{student_id}")
def update_student(
    student_id: int,
    updated_student: Student
):

    record_id = find_airtable_record(student_id)

    if not record_id:
        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )

    update_url = f"{BASE_URL}/{record_id}"

    payload = {
        "fields": {
            "StudentID": updated_student.student_id,
            "Name": updated_student.name,
            "Age": updated_student.age
        }
    }

    response = requests.patch(
        update_url,
        headers=HEADERS,
        json=payload
    )

    if response.status_code == 200:
        return {
            "message": "Student updated successfully",
            "data": response.json()
        }

    raise HTTPException(
        status_code=response.status_code,
        detail=response.text
    )


# DELETE Student


@app.delete("/students/{student_id}")
def delete_student(student_id: int):

    record_id = find_airtable_record(student_id)

    if not record_id:
        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )

    delete_url = f"{BASE_URL}/{record_id}"

    response = requests.delete(
        delete_url,
        headers=HEADERS
    )

    if response.status_code == 200:
        return {
            "message": "Student deleted successfully"
        }

    raise HTTPException(
        status_code=response.status_code,
        detail=response.text
    )


# Home Route


@app.get("/")
def home():
    return {
        "message": "FastAPI Airtable CRUD API Running"
    }


# Run Server


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )
