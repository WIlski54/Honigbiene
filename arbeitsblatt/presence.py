"""Exakte Online-Präsenz aus tatsächlich verbundenen Lernenden-Sockets.

Invarianten (Standard §11):
- Ein Lernplatz ist genau dann online, wenn mindestens ein Lernenden-Socket verbunden ist.
- Mehrere Tabs bleiben online, bis der letzte getrennt wurde.
- Lehrkraft-Sockets werden hier nie eingetragen und ändern den Status nicht.
- `disconnect` wird über die Eigentümerzuordnung aufgelöst, nicht über Session-Cookies.
"""

import threading

_lock = threading.RLock()
student_connections: dict[str, set[str]] = {}
student_connection_owners: dict[str, str] = {}


def add(schueler_id: str, socket_id: str) -> bool:
    """Registriert einen Socket. Liefert True, wenn der Lernplatz dadurch online wurde."""
    with _lock:
        sockets = student_connections.setdefault(schueler_id, set())
        became_online = not sockets
        sockets.add(socket_id)
        student_connection_owners[socket_id] = schueler_id
        return became_online


def remove(socket_id: str) -> tuple[str | None, bool]:
    """Entfernt einen Socket. Liefert (schueler_id, ging_offline)."""
    with _lock:
        schueler_id = student_connection_owners.pop(socket_id, None)
        if not schueler_id:
            return None, False
        sockets = student_connections.get(schueler_id, set())
        sockets.discard(socket_id)
        went_offline = not sockets
        if went_offline:
            student_connections.pop(schueler_id, None)
        return schueler_id, went_offline


def is_online(schueler_id: str) -> bool:
    with _lock:
        return bool(student_connections.get(schueler_id))


def sockets_of(schueler_id: str) -> set[str]:
    with _lock:
        return set(student_connections.get(schueler_id, set()))


def online_ids() -> list[str]:
    with _lock:
        return [sid for sid, sockets in student_connections.items() if sockets]


def drop_student(schueler_id: str) -> set[str]:
    """Entfernt alle Verbindungen eines Lernplatzes (Löschung, Reset, Restore)."""
    with _lock:
        sockets = student_connections.pop(schueler_id, set())
        for socket_id in sockets:
            student_connection_owners.pop(socket_id, None)
        return sockets


def reset() -> None:
    with _lock:
        student_connections.clear()
        student_connection_owners.clear()
