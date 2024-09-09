import uuid

from fastapi import HTTPException, status
from sqlmodel import Session, select, func

from models.factors import FactorsOut, CreUpdateIn, Factors, FactorsListOut

from models.factors_function_labels import (
    FactorsFunctionLabels,
    FactorsFunctionLabelsListOut,
)

from core.config import settings
from models.base import Message


def read_all_cre(
    session: Session, skip: int = 0, limit: int = settings.RECORD_LIMIT
) -> FactorsListOut:
    count_statement = select(func.count(Factors.id)).select_from(Factors)
    count = session.exec(count_statement).one()

    db_factors = session.exec(select(Factors).offset(skip).limit(limit)).all()

    response_data = []
    ft_list_id = [factor.ft_id for factor in db_factors if factor.ft_id]
    db_function_labels = session.exec(
        select(FactorsFunctionLabels).where(FactorsFunctionLabels.id.in_(ft_list_id))
    ).all()

    function_labels_map = {
        function_label.id: function_label for function_label in db_function_labels
    }

    for factor in db_factors:
        if factor.ft_id:
            response_data.append(
                {
                    **factor.model_dump(),
                    "function_label": function_labels_map[factor.ft_id].model_dump(),
                }
            )
            print(response_data)
        else:
            response_data.append(factor.model_dump())

    return FactorsListOut(data=response_data, count=count)


def read_cre(session: Session, factor_id: uuid.UUID) -> FactorsOut:
    db_factors = session.exec(select(Factors).where(Factors.id == factor_id)).first()
    if db_factors is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Factor not found",
        )

    response_data = {**db_factors.model_dump()}
    if db_factors.ft_id:
        db_function_label = session.exec(
            select(FactorsFunctionLabels).where(
                FactorsFunctionLabels.id == db_factors.ft_id
            )
        ).first()
        response_data = {
            **response_data,
            "function_label": db_function_label.model_dump(),
        }

    return response_data


def update_cre(
    session: Session, factor_id: uuid.UUID, data_in: CreUpdateIn
) -> FactorsOut:
    db_factors = session.exec(select(Factors).where(Factors.id == factor_id)).first()
    if db_factors is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Factor not found",
        )

    db_factors.sqlmodel_update(data_in.model_dump(exclude_unset=True))
    session.add(db_factors)
    session.commit()
    session.refresh(db_factors)

    return db_factors


def delete_cre(session: Session, factor_id: uuid.UUID) -> Message:
    db_factors = session.exec(select(Factors).where(Factors.id == factor_id)).first()
    if db_factors is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Factor not found",
        )

    session.delete(db_factors)
    session.commit()

    return Message(status_code=status.HTTP_200_OK, message="Item deleted")


def read_function_labels(
    session: Session, skip: int = 0, limit: int = settings.RECORD_LIMIT
) -> FactorsFunctionLabelsListOut:
    count_statement = select(func.count(FactorsFunctionLabels.id)).select_from(
        FactorsFunctionLabels
    )
    count = session.exec(count_statement).one()

    db_function_labels = session.exec(
        select(FactorsFunctionLabels).offset(skip).limit(limit)
    ).all()

    return FactorsFunctionLabelsListOut(data=db_function_labels, count=count)


def read_function_label(session: Session, ft_id: uuid.UUID) -> FactorsFunctionLabels:
    db_function_label = session.exec(
        select(FactorsFunctionLabels).where(FactorsFunctionLabels.id == ft_id)
    ).first()
    if db_function_label is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Function label not found",
        )

    return db_function_label


def update_function_label(
    session: Session, ft_id: uuid.UUID, data_in: FactorsFunctionLabels
) -> FactorsFunctionLabels:
    db_function_label = session.exec(
        select(FactorsFunctionLabels).where(FactorsFunctionLabels.id == ft_id)
    ).first()
    if db_function_label is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Function label not found",
        )

    db_function_label.sqlmodel_update(data_in.model_dump(exclude_unset=True))
    session.add(db_function_label)
    session.commit()
    session.refresh(db_function_label)

    return db_function_label


def delete_function_label(session: Session, ft_id: uuid.UUID) -> Message:
    db_function_label = session.exec(
        select(FactorsFunctionLabels).where(FactorsFunctionLabels.id == ft_id)
    ).first()
    if db_function_label is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Function label not found",
        )

    session.delete(db_function_label)
    session.commit()

    return Message(status_code=status.HTTP_200_OK, message="Item deleted")
