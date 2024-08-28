import json
from sqlalchemy import func
from sqlmodel import Session, create_engine, select

from utils import random_color
from core.config import settings

engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))


def init_db(session: Session) -> None:
    from models.users import User, UserBase
    from models.factors_function_labels import FactorsFunctionLabels
    from models.factors import Factors

    # users
    user = session.exec(
        select(User).where(User.user_name == settings.FIRST_SUPERUSER)
    ).first()
    if not user:
        user_in = UserBase(
            user_name=settings.FIRST_SUPERUSER,
            user_role_id=1,
            hashed_password=settings.DEFAULT_PW_FOR_DEV,
        )
        db_obj = User.model_validate(user_in)
        session.add(db_obj)
        session.commit()
        session.refresh(db_obj)

    # factors function labels
    db_factors_function_labels = session.exec(
        select(func.count(FactorsFunctionLabels.id)).select_from(FactorsFunctionLabels)
    ).one()
    if not db_factors_function_labels:
        # load data from JSON file
        with open("./app/init_data/factors_function_labels.json") as f:
            data = json.load(f)

        data_in = []
        for item in data:
            data_in.append(FactorsFunctionLabels(**item))

        session.add_all(data_in)
        session.commit()

    # factors
    db_factors = session.exec(select(func.count(Factors.id)).select_from(Factors)).one()
    if not db_factors:
        # load data from JSON file
        with open("./app/init_data/factors.json") as f:
            data = json.load(f)

        data_in = []
        for item in data:
            color = random_color()
            data_in.append(Factors(**item["fields"], color=color))

        session.add_all(data_in)
        session.commit()
