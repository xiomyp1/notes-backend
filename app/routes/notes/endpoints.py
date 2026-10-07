from fastapi import APIRouter, HTTPException
from app.schemas.note import Note, CreateNote, UpdateNote
from app.clients.firestore import get_firestore_client
from typing import Dict, List
from google.cloud import firestore


#Instancia una clase router para manejar las rutas relacionadas con las notas
router = APIRouter(prefix="/notes", tags=["notes"])


@router.get("", status_code=200)
async def get_notes() -> Dict[str, List[Note]]:
    db = get_firestore_client()
    collection_ref = db.collection("notes").order_by("updated_at", direction=firestore.Query.DESCENDING)

    notes = []
    docs = collection_ref.stream()
    for doc in docs:
        note_data = doc.to_dict()

        #Convertir firestore Timestamp a string en formato ISO 8601 para que sea compatible con JSON
        note_data["created_at"] = note_data["created_at"].isoformat()
        note_data["updated_at"] = note_data["updated_at"].isoformat()
        notes.append(note_data) 
    return {"notes": notes} 

#Si esta request es bien sale 201, una entidad se crea correctamente. Si no, sale 400, bad request
@router.post("", status_code=201)
async def create_note(note_data: CreateNote) -> Dict[str, Note]:
    db = get_firestore_client()
    collection_ref = db.collection("notes")

    # Crea un nuevo documento en la colección "test-notes"
    doc_ref = collection_ref.document()
    now = firestore.SERVER_TIMESTAMP

    new_note = {
        "id": doc_ref.id,
        "title": note_data.title,
        "content": note_data.content,
        "created_at": now,
        "updated_at": now
    }

    doc_ref.set(new_note)
    doc = doc_ref.get()
    note_stored = doc.to_dict()

    return {"note": {
        "id": note_stored["id"],
        "title": note_stored["title"],
        "content": note_stored["content"],
        "created_at": note_stored["created_at"].isoformat(),
        "updated_at": note_stored["updated_at"].isoformat()
    }
}

@router.get("/{note_id}", status_code=200)
async def get_note_by_id(note_id: str) -> Dict[str, Note]:
    db = get_firestore_client()
    collection_ref = db.collection("notes")
    doc_ref = collection_ref.document(note_id)
    doc = doc_ref.get()

    if not doc.exists:
        raise HTTPException(status_code=404, detail="Note not found")

    note_data = doc.to_dict()
    return {"note": {
        "id": note_data["id"],
        "title": note_data["title"],
        "content": note_data["content"],    
    "created_at": note_data["created_at"].isoformat(),
    "updated_at": note_data["updated_at"].isoformat()
    }
}

#Actualiza una nota existente en la base de datos Firestore. Si la nota no existe, devuelve un error 404. Si la actualización es exitosa, devuelve la nota actualizada con un código de estado 200.
@router.patch("/{note_id}", status_code=200)
async def update_note(note_id: str, note_data: UpdateNote) -> Dict[str, Note]:
    db = get_firestore_client()
    collection_ref = db.collection("notes")
    doc_ref = collection_ref.document(note_id)
    doc = doc_ref.get()

    if not doc.exists:
        raise HTTPException(status_code=404, detail="Note not found")

    update_data = {}

    if note_data.title is not None:
        update_data["title"] = note_data.title
    if note_data.content is not None:
        update_data["content"] = note_data.content

    update_data["updated_at"] = firestore.SERVER_TIMESTAMP
# Guarda en firestore los cambios realizados en la nota, actualizando los campos proporcionados y estableciendo la marca de tiempo de actualización. Luego, obtiene la nota actualizada y la devuelve en formato JSON.
    doc_ref.update(update_data)
    updated_doc = doc_ref.get()
    updated_note = updated_doc.to_dict()

    return {"note": {
        "id": updated_note["id"],
        "title": updated_note["title"],
        "content": updated_note["content"],
        "created_at": updated_note["created_at"].isoformat(),
        "updated_at": updated_note["updated_at"].isoformat()
    }
}

#Eliminar una nota identificada por su ID.
@router.delete("/{note_id}", status_code=200)
async def delete_note(note_id: str) -> Dict[str, str]:
    db = get_firestore_client()
    collection_ref = db.collection("notes")
    doc_ref = collection_ref.document(note_id)
    doc = doc_ref.get()

    if not doc.exists:
        raise HTTPException(status_code=404, detail="Note not found")

    doc_ref.delete()
    return {"message": f"Note with id: {note_id} deleted successfully"}