from fastapi import APIRouter

from api.deps import SessionDep
from models.computational_motif import ComputationalMotifListOut, SearchComputationalMotif
from core.config import settings
from fastapi.params import Depends
from models.factors import FactorsListOut, CreUpdateIn, FactorsOut, MotifSearch, MotifSearchOut

import api.applications.cre.cre_controller as CreController
import api.applications.cre.search_cre_controller as SearchMotifController
import api.applications.motif.motif_controller as MotifController

import uuid

from api.deps import get_current_active_admin

from models.factors_function_labels import (
    FactorsFunctionLabelsListOut,
    FactorsFunctionLabelsItemOut,
    FactorsFunctionLabelsUpdate,
)

from models.base import Message

router = APIRouter()


@router.get(
    "/cre",
    response_model=FactorsListOut,
    dependencies=[Depends(get_current_active_admin)],
)
def read_all_cre(
    session: SessionDep, skip: int = 0, limit: int = settings.RECORD_LIMIT
) -> FactorsListOut:
    return CreController.read_all_cre(session, skip, limit)


@router.get(
    "/cre/{factor_id}",
    response_model=FactorsOut,
    dependencies=[Depends(get_current_active_admin)],
)
def read_cre(session: SessionDep, factor_id: uuid.UUID) -> FactorsOut:
    return CreController.read_cre(session, factor_id)


@router.put(
    "/cre/{factor_id}",
    response_model=FactorsOut,
    dependencies=[Depends(get_current_active_admin)],
)
def update_cre(
    session: SessionDep, factor_id: uuid.UUID, data_in: CreUpdateIn
) -> FactorsOut:
    return CreController.update_cre(session, factor_id, data_in)


@router.delete(
    "/cre/{factor_id}",
    response_model=Message,
    dependencies=[Depends(get_current_active_admin)],
)
def delete_cre(session: SessionDep, factor_id: uuid.UUID) -> Message:
    return CreController.delete_cre(session, factor_id)


@router.get(
    "/function-labels",
    response_model=FactorsFunctionLabelsListOut,
    dependencies=[Depends(get_current_active_admin)],
)
def read_function_labels(
    session: SessionDep, skip: int = 0, limit: int = settings.RECORD_LIMIT
) -> FactorsFunctionLabelsListOut:
    return CreController.read_function_labels(session, skip, limit)


@router.get(
    "/function-labels/{ft_id}",
    response_model=FactorsFunctionLabelsItemOut,
    dependencies=[Depends(get_current_active_admin)],
)
def read_function_label(
    session: SessionDep, ft_id: uuid.UUID
) -> FactorsFunctionLabelsItemOut:
    return CreController.read_function_label(session, ft_id)


@router.put(
    "/function-labels/{ft_id}",
    response_model=FactorsFunctionLabelsItemOut,
    dependencies=[Depends(get_current_active_admin)],
)
def update_function_label(
    session: SessionDep, ft_id: uuid.UUID, data_in: FactorsFunctionLabelsUpdate
) -> FactorsFunctionLabelsItemOut:
    return CreController.update_function_label(session, ft_id, data_in)


@router.delete(
    "/function-labels/{ft_id}",
    response_model=Message,
    dependencies=[Depends(get_current_active_admin)],
)
def delete_function_label(session: SessionDep, ft_id: uuid.UUID) -> Message:
    return CreController.delete_function_label(session, ft_id)


@router.post("/search-for-cre", response_model=MotifSearchOut, dependencies=[Depends(get_current_active_admin)])
def search_for_cre(*, session: SessionDep, data_in: MotifSearch):
    return SearchMotifController.search_for_cre(session, data_in)

@router.post(
    "/computational-motifs/search",
    response_model=ComputationalMotifListOut,
    dependencies=[Depends(get_current_active_admin)],
)
def search_computational_motif(
    session: SessionDep,
    data_in: SearchComputationalMotif,
    skip: int = 0,
    limit: int = settings.RECORD_LIMIT,
) -> ComputationalMotifListOut:
    return MotifController.search_computational_motif(session, data_in, skip, limit)