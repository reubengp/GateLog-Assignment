from app import app, current_date, guest_records


def setup_function():
    guest_records.clear()


def test_login_page_loads():
    client = app.test_client()

    response = client.get("/")

    assert response.status_code == 200
    assert b"Apartment Guest Register" in response.data


def test_resident_can_add_guest():
    client = app.test_client()

    login_response = client.post(
        "/",
        data={
            "login_type": "resident",
            "flat_number": "A101",
            "password": "resident123",
        },
        follow_redirects=True,
    )

    assert login_response.status_code == 200

    response = client.post(
        "/resident/add",
        data={
            "name": "Priya",
            "phone": "9999999999",
            "flat_number": "A101",
            "visit_date": current_date(),
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Guest added successfully." in response.data
    assert len(guest_records) == 1


def test_security_sees_today_guest_and_marks_entry():
    guest_records.append(
        {
            "id": 1,
            "name": "Kiran",
            "phone": "8888888888",
            "flat_number": "A101",
            "visit_date": current_date(),
            "entry_time": None,
            "exit_time": None,
            "created_at": current_date(),
        }
    )

    client = app.test_client()
    login_response = client.post(
        "/",
        data={
            "login_type": "security",
            "security_name": "Security 1",
            "password": "gate123",
        },
        follow_redirects=True,
    )

    assert login_response.status_code == 200
    assert b"All Guest Records" in login_response.data

    response = client.post("/security/entry/1", follow_redirects=True)

    assert response.status_code == 200
    assert b"Entry time recorded." in response.data
    assert guest_records[0]["entry_time"] is not None
