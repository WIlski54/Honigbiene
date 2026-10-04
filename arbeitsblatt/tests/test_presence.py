import app as appmodule
import db as dbmod
import presence
from conftest import session_werte


def _socket(flask_client):
    return appmodule.socketio.test_client(appmodule.app, flask_test_client=flask_client)


def test_praesenz_reine_datenstruktur():
    presence.reset()
    assert presence.add("s1", "a") is True
    assert presence.add("s1", "b") is False
    assert presence.is_online("s1") and presence.online_ids() == ["s1"]
    assert presence.remove("a") == ("s1", False)
    assert presence.is_online("s1")
    assert presence.remove("b") == ("s1", True)
    assert not presence.is_online("s1")
    assert presence.remove("unbekannt") == (None, False)
    presence.add("s2", "c")
    assert presence.drop_student("s2") == {"c"}
    assert presence.student_connection_owners == {}


def test_zwei_tabs_bleiben_online_bis_zum_letzten_disconnect(student):
    sid = session_werte(student)["schueler_id"]
    s1 = _socket(student)
    s1.emit("schueler_join", {})
    assert presence.is_online(sid)
    s2 = _socket(student)
    s2.emit("schueler_join", {})
    assert len(presence.sockets_of(sid)) == 2
    s1.disconnect()
    assert presence.is_online(sid)
    s2.disconnect()
    assert not presence.is_online(sid)
    row = dbmod.get_db().execute("SELECT socket_id FROM schueler WHERE id=?", (sid,)).fetchone()
    assert row["socket_id"] is None


def test_lehrer_socket_im_selben_profil_aendert_praesenz_nicht(teacher, teacher_token):
    from conftest import anmelden
    anmelden(teacher, "Doppelt", "9c")
    sid = session_werte(teacher)["schueler_id"]
    st = _socket(teacher)
    st.emit("schueler_join", {})
    assert presence.is_online(sid)
    le = _socket(teacher)
    le.emit("lehrer_join", {"token": teacher_token})
    empfangen = [e["name"] for e in le.get_received()]
    assert "alle_schueler" in empfangen and "fortsetzung_update" in empfangen
    le.disconnect()
    assert presence.is_online(sid)  # Lehrkraft-Disconnect ändert Lernendenpräsenz nicht
    st.disconnect()
    assert not presence.is_online(sid)


def test_lehrer_join_ohne_gueltiges_token_wird_ignoriert(client):
    le = _socket(client)
    le.emit("lehrer_join", {"token": "falsch"})
    assert [e["name"] for e in le.get_received()] == []
    le.disconnect()


def test_alte_socket_id_macht_nach_neustart_niemanden_online(student):
    sid = session_werte(student)["schueler_id"]
    with dbmod.get_db() as db:
        db.execute("UPDATE schueler SET socket_id='veraltet' WHERE id=?", (sid,))
        db.commit()
    presence.reset()
    dbmod.init_db()
    assert not appmodule.get_schueler_info(sid)["online"]
    assert dbmod.get_db().execute("SELECT socket_id FROM schueler WHERE id=?", (sid,)).fetchone()["socket_id"] is None
