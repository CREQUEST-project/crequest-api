from fastapi import APIRouter
from sqlmodel import select
from api.deps import SessionDep
from core.config import settings

from models.factors import FactorsListOut, MotifSearch, MotifSearchOut, FactorsOut, QueryCareSearchIn
import api.applications.motif.search_motif_controller as SearchMotifController


router = APIRouter()

@router.post('/search-for-care', response_model=MotifSearchOut)
def search_for_care(*, session: SessionDep, data_in: MotifSearch) :
    return SearchMotifController.search_for_care(session, data_in)

@router.post('/query-care', response_model=FactorsListOut)
def query_care(session: SessionDep, data_in: QueryCareSearchIn, skip: int = 0, limit: int = settings.RECORD_LIMIT) -> FactorsListOut:
    return SearchMotifController.query_care(session, data_in, skip, limit)
    