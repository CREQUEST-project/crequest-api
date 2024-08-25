from sqlalchemy import func
from sqlmodel import Session, select
from models.search_for_care_history import SearchForCareHistory, SearchForCareHistoryListOut, SearchForCareHistoryOut
from models.users import User
from models.base import Message
from fastapi import HTTPException, status

def read_search_for_care_histories(session: Session, user_id: int) -> SearchForCareHistoryListOut:
    db_user = session.get(User, user_id)
    if db_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    count_statement = select(func.count(SearchForCareHistory.id)).where(SearchForCareHistory.user_id == user_id)
    count = session.exec(count_statement).one()
    db_search_for_care_histories = session.exec(select(SearchForCareHistory).where(SearchForCareHistory.user_id == user_id)).all()
    
    return SearchForCareHistoryListOut(data=db_search_for_care_histories, count=count)
    
def read_search_for_care_history(session: Session, user_id: int, history_id: int) -> SearchForCareHistoryOut:
    db_user = session.get(User, user_id)
    if db_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    db_search_for_care_history = session.get(SearchForCareHistory, history_id)
    if db_search_for_care_history is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Search for care history not found")
    
    return db_search_for_care_history

def delete_search_for_care_history(session: Session, user_id: int, history_id: int) -> Message:
    db_user = session.get(User, user_id)
    if db_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    db_search_for_care_history = session.get(SearchForCareHistory, history_id)
    if db_search_for_care_history is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Search for care history not found")
    
    session.delete(db_search_for_care_history)
    session.commit()
    
    return Message(status_code=status.HTTP_200_OK, message="Item deleted")