from urllib.parse import quote


def test_root_redirects_to_static_index(client):
    # Arrange
    expected_location = "/static/index.html"

    # Act
    response = client.get("/", follow_redirects=False)

    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == expected_location


def test_get_activities_returns_expected_structure(client):
    # Arrange
    required_keys = {"description", "schedule", "max_participants", "participants"}

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200

    payload = response.json()
    assert isinstance(payload, dict)
    assert payload

    for details in payload.values():
        assert required_keys.issubset(details.keys())
        assert isinstance(details["participants"], list)


def test_signup_success_adds_participant(client):
    # Arrange
    activity_name = "Tennis Club"
    encoded_activity_name = quote(activity_name, safe="")
    email = "new.student@mergington.edu"

    # Act
    response = client.post(
        f"/activities/{encoded_activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for {activity_name}"

    activities_response = client.get("/activities")
    participants = activities_response.json()[activity_name]["participants"]
    assert email in participants


def test_signup_rejects_duplicate_participant(client):
    # Arrange
    activity_name = "Chess Club"
    encoded_activity_name = quote(activity_name, safe="")
    existing_email = "michael@mergington.edu"

    # Act
    response = client.post(
        f"/activities/{encoded_activity_name}/signup",
        params={"email": existing_email},
    )

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_signup_returns_not_found_for_unknown_activity(client):
    # Arrange
    unknown_activity = "Unknown Club"
    encoded_activity_name = quote(unknown_activity, safe="")
    email = "student@mergington.edu"

    # Act
    response = client.post(
        f"/activities/{encoded_activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_success_removes_participant(client):
    # Arrange
    activity_name = "Chess Club"
    encoded_activity_name = quote(activity_name, safe="")
    email = "michael@mergington.edu"

    # Act
    response = client.delete(
        f"/activities/{encoded_activity_name}/unregister",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Unregistered {email} from {activity_name}"

    activities_response = client.get("/activities")
    participants = activities_response.json()[activity_name]["participants"]
    assert email not in participants


def test_unregister_returns_not_found_for_unknown_activity(client):
    # Arrange
    unknown_activity = "Unknown Club"
    encoded_activity_name = quote(unknown_activity, safe="")
    email = "student@mergington.edu"

    # Act
    response = client.delete(
        f"/activities/{encoded_activity_name}/unregister",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_returns_not_found_for_missing_participant(client):
    # Arrange
    activity_name = "Tennis Club"
    encoded_activity_name = quote(activity_name, safe="")
    email = "not.registered@mergington.edu"

    # Act
    response = client.delete(
        f"/activities/{encoded_activity_name}/unregister",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Student not found in this activity"
