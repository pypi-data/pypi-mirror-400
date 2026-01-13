"""Copyright 2024 Everlasting Systems and Solutions LLC (www.myeverlasting.net).
All Rights Reserved.

No part of this software or any of its contents may be reproduced, copied, modified or adapted, without the prior written consent of the author, unless otherwise indicated for stand-alone materials.

For permission requests, write to the publisher at the email address below:
office@myeverlasting.net

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

"""
from typing import Type
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

def add_model(model_class: Type, db: Session, **kwargs):
    """
    Persist a SQLAlchemy model to the database.

    Args:
    - model_class (Type): The SQLAlchemy model class to be persisted.
    - db (Session): The database session to use for persistence.
    - **kwargs: Keyword arguments to pass to the model constructor.

    Returns:
    - bool: True if the model is persisted successfully, False otherwise.

    Raises:
    - IntegrityError: If the model cannot be persisted due to an integrity error.
    """
    try:
        new_model = model_class(**kwargs)
        db.add(new_model)
        db.commit()
        db.refresh(new_model)
        return new_model
    except IntegrityError:
        db.rollback()
        return False
def update_model(model_class: Type, db: Session, id: int, **kwargs) -> bool:
    """
    Update a SQLAlchemy model in the database.

    Args:
    - model_class (Type): The SQLAlchemy model class to be updated.
    - db (Session): The database session to use for updating.
    - id (int): The ID of the model instance to be updated.
    - **kwargs: Keyword arguments with the attributes to be updated and their new values.

    Returns:
    - bool: True if the model is updated successfully, False otherwise.

    Raises:
    - Exception: If an error occurs during the update process.
    """
    try:
        model = db.query(model_class).filter_by(id=id).first()
        if model:
            for key, value in kwargs.items():
                setattr(model, key, value)
            db.commit()
            return True
        return False
    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
        return False

def get_model(model_class: Type, db: Session, id: int) -> object:
    """
    Retrieve a SQLAlchemy model instance from the database by ID.

    Args:
    - model_class (Type): The SQLAlchemy model class to be retrieved.
    - db (Session): The database session to use for retrieval.
    - id (int): The ID of the model instance to be retrieved.

    Returns:
    - object: The retrieved model instance, or None if not found.
    """
    return db.query(model_class).filter_by(id=id).first()

def get_all_models(model_class: Type, db: Session) -> list:
    """
    Retrieve all instances of a SQLAlchemy model from the database.

    Args:
    - model_class (Type): The SQLAlchemy model class to be retrieved.
    - db (Session): The database session to use for retrieval.

    Returns:
    - list: A list of all instances of the specified model class.
    """
    return db.query(model_class).all()

def delete_model(model_class: Type, db: Session, id: int) -> bool:
    """
    Delete a SQLAlchemy model instance from the database by ID.

    Args:
    - model_class (Type): The SQLAlchemy model class to be deleted.
    - db (Session): The database session to use for deletion.
    - id (int): The ID of the model instance to be deleted.

    Returns:
    - bool: True if the model is deleted successfully, False otherwise.

    Raises:
    - Exception: If an error occurs during the deletion process.
    """
    try:
        model = db.query(model_class).filter_by(id=id).first()
        if model:
            db.delete(model)
            db.commit()
            return True
        return False
    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
        return False