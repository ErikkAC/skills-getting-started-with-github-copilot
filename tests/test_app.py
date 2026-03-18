def test_root_redirect(client):
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities(client):
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data


def test_signup_for_activity_success(client):
    activity_name = "Chess Club"
    email = "test_student@mergington.edu"

    # ensure email is not already in participants
    current = client.get("/activities").json()[activity_name]["participants"]
    if email in current:
        current.remove(email)

    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for {activity_name}"

    # duplicate signup should fail
    duplicate = client.post(f"/activities/{activity_name}/signup", params={"email": email})
    assert duplicate.status_code == 400
    assert duplicate.json()["detail"] == "Student already signed up for this activity"


def test_remove_participant_success_and_errors(client):
    activity_name = "Programming Class"
    email = "remove_test@mergington.edu"

    # ensure participant exists
    client.post(f"/activities/{activity_name}/signup", params={"email": email})

    response = client.delete(f"/activities/{activity_name}/participants", params={"email": email})
    assert response.status_code == 200
    assert response.json()["message"] == f"Removed {email} from {activity_name}"

    not_found = client.delete(f"/activities/{activity_name}/participants", params={"email": email})
    assert not_found.status_code == 404
    assert not_found.json()["detail"] == "Participant not found in activity"


def test_signup_for_unknown_activity(client):
    response = client.post("/activities/Nonexistent/signup", params={"email": "x@x.com"})
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_remove_participant_unknown_activity(client):
    response = client.delete("/activities/Unknown/participants", params={"email": "x@x.com"})
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"
