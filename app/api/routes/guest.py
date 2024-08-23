from fastapi import APIRouter
from api.deps import SessionDep

from models.factors import MotifSearch, MotifSearchOut
import api.applications.motif.search_motif_controller as SearchMotifController


router = APIRouter()

@router.post('/search-motif', response_model=MotifSearchOut)
def search_motif(*, session: SessionDep, data_in: MotifSearch) :
    return SearchMotifController.search_motif(session, data_in)