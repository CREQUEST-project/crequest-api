from fastapi import APIRouter, Depends, File, Form, UploadFile

from api.deps import SessionDep
from models.computational_motif import ComputationalMotifListOut, ComputationalMotifOut
from models.factors import FactorsIn, MotifSamplerResponse
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


@router.post(
    "/motif-sampler",
    response_model=MotifSamplerResponse,
    dependencies=[Depends(get_current_active_biologist)],
)
async def motif_sampler(
    session: SessionDep,
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
    """
    Endpoint for performing motif sampling.

    Args:
        f_file (UploadFile): The input file for motif sampling.
        b_file (UploadFile): The background file for motif sampling.
        output_o (str): The output file for observed motifs.
        output_m (str): The output file for motif occurrences.
        r (int | None): The number of randomizations to perform. Default is 100.
        s (int | None): The seed for random number generation. Default is 0.
        w (int | None): The width of the motifs to search for. Default is 8.
        n (int | None): The number of motifs to search for. Default is 1.
        x (int | None): The number of motifs to report. Default is 1.
        M (int | None): The maximum number of motifs to report. Default is 2.
        p (int | None): The maximum number of positions to report. Default is None.
        Q (int | None): The maximum number of motifs to report per position. Default is 100.
        z (int | None): The number of positions to report per motif. Default is 1.

    Returns:
        MotifSamplerResponse: The response containing the results of motif sampling.
    """
    return await MotifController.motif_sampler(
        session, f_file, b_file, output_o, output_m, r, s, w, n, x, M, p, Q, z, True
    )
