import uuid
from sqlmodel import Session, select
from sqlalchemy import event
from typing import Type
import re


def add_auto_code_listener_withid(
    model: Type, field_name: str, id_field: str, prefix: str
):
    """
    Dynamically adds a SQLAlchemy event listener to auto-generate codes like PREFIX001.

    Args:
        model: The SQLModel table class.
        field_name: The field to auto-generate (e.g., 'chat_code', 'agent_code').
        id_field: The primary key field name dynamically (e.g., 'chat_id', 'agent_id').
        prefix: The prefix for the generated code (e.g., 'CC', 'AG').
    """

    @event.listens_for(model, "before_insert")
    def generate_auto_code(mapper, connection, target):
        try:
            # Only generate if the code is empty
            if not getattr(target, field_name, None):

                session = Session(connection)

                # Dynamically fetch the id field
                id_column = getattr(model, id_field)

                last_code = session.exec(
                    select(getattr(model, field_name)).order_by(id_column.desc())
                ).first()

                session.close()

                # Extract last 3 digits from code
                if last_code:
                    match = re.search(r"(\d+)$", last_code)
                    next_number = int(match.group(1)) + 1 if match else 1
                else:
                    next_number = 1

                # Format: PREFIX + 3-digit number
                new_code = f"{prefix}{next_number:03d}"

                setattr(target, field_name, new_code)
        except Exception as ex:
            print(f"Error generating auto code for {field_name}: {ex}")


def add_auto_code_listener_withoutid(model: Type, field_name: str):
    """
    Automatically generates a UUIDv4 string for the given field.
    Example: 692421bf-5904-8322-91a5-ab415fa6673f
    """

    @event.listens_for(model, "before_insert")
    def generate_uuid(mapper, connection, target):
        if not getattr(target, field_name, None):
            new_uuid = str(uuid.uuid4())
            setattr(target, field_name, new_uuid)
