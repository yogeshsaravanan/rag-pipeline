"""
Change-Data-Capture (CDC) synchronisation layer.

SQLAlchemy after_insert / after_update / after_delete hooks call these
helpers to keep the ChromaDB user_data_stream collection in lockstep with
the relational Orders table.
"""
from sqlalchemy import event

from app.db.database import Order
from app.db.vector_store import get_user_collection
from app.services.ollama_service import get_embedding


# ── Serialise an Order row into a human-readable sentence ────────────────────
def _serialise_order(order: Order) -> str:
    return (
        f"Order ID {order.id} for User {order.user_id} contains a {order.product_name}. "
        f"The current order transaction status is: {order.status}. "
        f"Extra details: {order.details}"
    )


# ── Public sync functions ─────────────────────────────────────────────────────
def upsert_order_vector(order: Order) -> None:
    """Embed the order and upsert into the user_data_stream collection."""
    text   = _serialise_order(order)
    vector = get_embedding(text)

    get_user_collection().upsert(
        ids        = [f"order_{order.id}"],
        embeddings = [vector],
        documents  = [text],
        metadatas  = [{"user_id": order.user_id, "type": "order_history"}],
    )
    print(f"[CDC SYNC] Upserted Order {order.id} into vector store.")


def delete_order_vector(order_id: int) -> None:
    """Remove the corresponding vector when an order is deleted from SQL."""
    try:
        get_user_collection().delete(ids=[f"order_{order_id}"])
        print(f"[CDC PURGE] Removed vector for Order {order_id}.")
    except Exception as exc:
        print(f"[CDC PURGE ERROR] {exc}")


# ── SQLAlchemy ORM event hooks ────────────────────────────────────────────────
@event.listens_for(Order, "after_insert")
@event.listens_for(Order, "after_update")
def _on_save(mapper, connection, target: Order) -> None:   # noqa: ARG001
    upsert_order_vector(target)


@event.listens_for(Order, "after_delete")
def _on_delete(mapper, connection, target: Order) -> None:  # noqa: ARG001
    delete_order_vector(target.id)
