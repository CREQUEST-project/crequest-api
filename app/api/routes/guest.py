from fastapi import APIRouter, File, Form, UploadFile
from api.deps import SessionDep
from core.config import settings

from models.factors import (
    FactorsListOut,
    MotifSamplerResponse,
    MotifSearch,
    MotifSearchOut,
    QueryCreSearchIn,
)
import api.applications.cre.search_cre_controller as SearchMotifController
import api.applications.motif.motif_controller as MotifController


router = APIRouter()


@router.post("/search-for-cre", response_model=MotifSearchOut)
def search_for_cre(*, session: SessionDep, data_in: MotifSearch):
    return SearchMotifController.search_for_cre(session, data_in)


@router.post("/query-cre", response_model=FactorsListOut)
def query_cre(
    session: SessionDep,
    data_in: QueryCreSearchIn,
    skip: int = 0,
    limit: int = settings.RECORD_LIMIT,
) -> FactorsListOut:
    return SearchMotifController.query_cre(session, data_in, skip, limit)


@router.post("/motif-sampler", response_model=MotifSamplerResponse)
async def motif_sampler(
    f_file: UploadFile = File(...),
    b_file: UploadFile = File(...),
    output_o: str = Form(...),
    output_m: str = Form(...),
    r: int | None = Form(100),
    s: int | None = Form(0),
    w: int | None = Form(8),
    n: int | None = Form(1),
    x: int | None = Form(1),
    M: int | None = Form(2),
    p: int | None = Form(None),
    Q: int | None = Form(100),
    z: int | None = Form(1),
) -> MotifSamplerResponse:
    return await MotifController.motif_sampler(
        f_file, b_file, output_o, output_m, r, s, w, n, x, M, p, Q, z
    )
