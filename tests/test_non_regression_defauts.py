def setup_festival_data(client):
    f_res = client.post(
        "/festivals",
        json={
            "name": "Hellforge Test",
            "location": "Clisson",
            "start_date": "2027-06-18T10:00:00",
            "end_date": "2027-06-20T23:59:59",
        },
    )
    assert f_res.status_code == 201
    festival = f_res.json()
    a1_res = client.post(
        "/artists",
        json={
            "name": "Iron Vow",
            "genre": "Heavy Metal",
            "required_equipment": ["Micro"],
        },
    )
    assert a1_res.status_code == 201
    artist1 = a1_res.json()
    a2_res = client.post(
        "/artists",
        json={
            "name": "Crimson Engine",
            "genre": "Thrash Metal",
            "required_equipment": ["Micro"],
        },
    )
    assert a2_res.status_code == 201
    artist2 = a2_res.json()
    s_res = client.post(
        "/stages",
        json={
            "festival_id": festival["id"],
            "name": "Mainstage 1",
            "capacity": 10000,
            "available_equipment": ["Micro", "Guitares"],
        },
    )
    assert s_res.status_code == 201
    stage = s_res.json()

    return {
        "festival": festival,
        "artist1": artist1,
        "artist2": artist2,
        "stage": stage,
    }


def test_defaut_1_(client, setup_festival_data):
    data = setup_festival_data
    fest_id = data["festival"]["id"]
    stage_id = data["stage"]["id"]
    c1_res = client.post(
        "/concerts",
        json={
            "festival_id": fest_id,
            "artist_id": data["artist1"]["id"],
            "stage_id": stage_id,
            "start_time": "2027-06-18T18:00:00",
            "end_time": "2027-06-18T19:00:00",
        },
    )
    assert c1_res.status_code == 201
    c2_res = client.post(
        "/concerts",
        json={
            "festival_id": fest_id,
            "artist_id": data["artist2"]["id"],
            "stage_id": stage_id,
            "start_time": "2027-06-18T19:30:00",
            "end_time": "2027-06-18T20:30:00",
        },
    )
    assert c2_res.status_code == 201
    c2_id = c2_res.json()["id"]
    reschedule_res = client.patch(
        f"/concerts/{c2_id}/reschedule",
        json={"start_time": "2027-06-18T18:30:00", "end_time": "2027-06-18T19:30:00"},
    )

    assert reschedule_res.status_code in (400, 422), (
        f"ÉCHEC NON-RÉGRESSION (Défaut 1) : L'API a accepté le chevauchement avec HTTP {reschedule_res.status_code}"
    )


def test_defaut_2_echec_notification_ne_doit_pas_persister_changement(
    client, setup_festival_data, monkeypatch
):
    data = setup_festival_data
    original_start = "2027-06-18T14:00:00"
    original_end = "2027-06-18T15:00:00"
    c_res = client.post(
        "/concerts",
        json={
            "festival_id": data["festival"]["id"],
            "artist_id": data["artist1"]["id"],
            "stage_id": data["stage"]["id"],
            "start_time": original_start,
            "end_time": original_end,
        },
    )
    assert c_res.status_code == 201
    c_id = c_res.json()["id"]
    monkeypatch.setattr(settings, "fail_notifications", True)
    client.patch(
        f"/concerts/{c_id}/reschedule",
        json={"start_time": "2027-06-18T16:00:00", "end_time": "2027-06-18T17:00:00"},
    )
    get_res = client.get(f"/concerts/{c_id}")
    assert get_res.status_code == 200
    concert_in_db = get_res.json()

    assert concert_in_db["start_time"] == original_start, (
        f"ÉCHEC NON-RÉGRESSION (Défaut 2) : La modification a été persistée en BDD ({concert_in_db['start_time']}) "
        f"malgré l'échec de la notification. Horaire attendu : {original_start}"
    )


def test_defaut_3_deplacement_refuse_si_planning_publie(client, setup_festival_data):
    data = setup_festival_data
    fest_id = data["festival"]["id"]
    c_res = client.post(
        "/concerts",
        json={
            "festival_id": fest_id,
            "artist_id": data["artist1"]["id"],
            "stage_id": data["stage"]["id"],
            "start_time": "2027-06-18T14:00:00",
            "end_time": "2027-06-18T15:00:00",
        },
    )
    assert c_res.status_code == 201
    c_id = c_res.json()["id"]
    pub_res = client.post(f"/festivals/{fest_id}/publish")
    assert pub_res.status_code == 200
    assert pub_res.json()["status"] == "published"
    reschedule_res = client.patch(
        f"/concerts/{c_id}/reschedule",
        json={"start_time": "2027-06-18T16:00:00", "end_time": "2027-06-18T17:00:00"},
    )

    assert reschedule_res.status_code in (400, 403, 409, 422), (
        f"ÉCHEC NON-RÉGRESSION (Défaut 3) : L'API a permis de modifier un concert d'un planning publié "
        f"(statut HTTP reçu : {reschedule_res.status_code})"
    )
