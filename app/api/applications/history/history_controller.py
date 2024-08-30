from sqlalchemy import func
from sqlmodel import Session, select
from models.search_for_cre_history import (
    SearchForCreHistory,
    SearchForCreHistoryListOut,
    SearchForCreHistoryOut,
)
from models.users import User
from models.base import Message
from fastapi import HTTPException, status


def read_search_for_cre_histories(
    session: Session, user_id: int
) -> SearchForCreHistoryListOut:
    db_user = session.get(User, user_id)
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    count_statement = select(func.count(SearchForCreHistory.id)).where(
        SearchForCreHistory.user_id == user_id
    )
    count = session.exec(count_statement).one()
    db_search_for_cre_histories = session.exec(
        select(SearchForCreHistory).where(SearchForCreHistory.user_id == user_id)
    ).all()

    return SearchForCreHistoryListOut(data=db_search_for_cre_histories, count=count)


def read_search_for_cre_history(
    session: Session, user_id: int, history_id: int
) -> SearchForCreHistoryOut:
    db_user = session.get(User, user_id)
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    db_search_for_cre_history = session.get(SearchForCreHistory, history_id)
    if db_search_for_cre_history is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Search for cre history not found",
        )

    return db_search_for_cre_history


def delete_search_for_cre_history(
    session: Session, user_id: int, history_id: int
) -> Message:
    db_user = session.get(User, user_id)
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    db_search_for_cre_history = session.get(SearchForCreHistory, history_id)
    if db_search_for_cre_history is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Search for cre history not found",
        )

    session.delete(db_search_for_cre_history)
    session.commit()

    return Message(status_code=status.HTTP_200_OK, message="Item deleted")
