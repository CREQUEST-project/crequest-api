from fastapi import APIRouter, Depends

from api.deps import SessionDep
from models.computational_motif import ComputationalMotifListOut, ComputationalMotifOut
from models.factors import FactorsIn
from models.base import Message
import api.applications.motif.motif_controller as MotifController
from core.config import settings
from api.deps import get_current_active_biologist

router = APIRouter()


@router.get(
    "/computational-motifs/{motif_id}",
    response_model=ComputationalMotifOut,
    dependencies=[Depends(get_current_active_biologist)],
)
def read_computational_motif(
    session: SessionDep, motif_id: int
) -> ComputationalMotifOut:
    return MotifController.read_computational_motif(session, motif_id)


@router.get(
    "/computational-motifs",
    response_model=ComputationalMotifListOut,
    dependencies=[Depends(get_current_active_biologist)],
)
def read_computational_motifs(
    session: SessionDep, skip: int = 0, limit: int = settings.RECORD_LIMIT
) -> ComputationalMotifListOut:
    return MotifController.read_computational_motifs(session, skip, limit)


@router.delete(
    "/computational-motifs/{motif_id}",
    response_model=Message,
    dependencies=[Depends(get_current_active_biologist)],
)
def delete_computational_motif(session: SessionDep, motif_id: int) -> Message:
    return MotifController.delete_computational_motif(session, motif_id)


@router.post(
    "/computational-motifs/{motif_id}/validation",
    response_model=Message,
    dependencies=[Depends(get_current_active_biologist)],
)
def validate_computational_motif(
    session: SessionDep, motif_id: int, data_in: FactorsIn
) -> Message:
    return MotifController.validate_computational_motif(session, motif_id, data_in)
