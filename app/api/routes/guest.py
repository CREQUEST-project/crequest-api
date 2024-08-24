from fastapi import APIRouter
from api.deps import SessionDep

from models.factors import MotifSearch, MotifSearchOut
import api.applications.motif.search_motif_controller as SearchMotifController


router = APIRouter()

@router.post('/search-for-care', response_model=MotifSearchOut)
def search_for_care(*, session: SessionDep, data_in: MotifSearch) :
    return SearchMotifController.search_for_care(session, data_in)