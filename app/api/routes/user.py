from fastapi import APIRouter, Depends, File, Form, UploadFile
from fastapi.responses import StreamingResponse

from api.deps import SessionDep, get_current_active_user, verify_user_id
from models.base import Message
from models.search_for_cre_history import (
    SearchForCreHistoryListOut,
    SearchForCreHistoryOut,
)
from models.factors import (
    CreResultSendEmail,
    FactorsListOut,
    MotifSamplerResponse,
    MotifSearch,
    MotifSearchAndSaveHistoryOut,
    QueryCreSearchIn,
)
from core.config import settings

import api.applications.cre.search_cre_controller as SearchMotifController
import api.applications.history.history_controller as HistoryController
import api.applications.motif.motif_controller as MotifController
import api.applications.cre.export_cre_controller as ExportCreController

router = APIRouter()


@router.post(
    "/query-cre",
    response_model=FactorsListOut,
    dependencies=[Depends(get_current_active_user)],
)
def query_cre(
    session: SessionDep,
    data_in: QueryCreSearchIn,
    skip: int = 0,
    limit: int = settings.RECORD_LIMIT,
) -> FactorsListOut:
    """
    Query cre based on the provided search criteria.

    Args:
        session (SessionDep): The database session.
        data_in (QueryCreSearchIn): The input data containing the search criteria.
        skip (int, optional): The number of records to skip. Defaults to 0.
        limit (int, optional): The maximum number of records to return. Defaults to settings.RECORD_LIMIT.

    Returns:
        FactorsListOut: The list of factors matching the search criteria.
    """
    return SearchMotifController.query_cre(session, data_in, skip, limit)


@router.post(
    "/{user_id}/search-for-cre",
    response_model=MotifSearchAndSaveHistoryOut,
    dependencies=[Depends(get_current_active_user), Depends(verify_user_id)],
)
def search_for_cre_and_save_history(
    session: SessionDep, data_in: MotifSearch, user_id: int
):
    """
    Search for cre and save search history.

    Parameters:
    - session: The database session.
    - data_in: The input data for the motif search.

    Returns:
    - The result of the motif search.

    """
    return SearchMotifController.search_for_cre_and_save_history(
        session, data_in, user_id
    )


@router.get(
    "/{user_id}/search-for-cre/histories",
    response_model=SearchForCreHistoryListOut,
    dependencies=[Depends(get_current_active_user), Depends(verify_user_id)],
)
def read_search_for_cre_histories(*, session: SessionDep, user_id: int):
    """
    Get the search history for the user.

    Parameters:
    - session: The database session.
    - user_id: The user ID.

    Returns:
    - The search history for the user.

    """
    return HistoryController.read_search_for_cre_histories(session, user_id)


@router.get(
    "/{user_id}/search-for-cre/histories/{history_id}",
    response_model=SearchForCreHistoryOut,
    dependencies=[Depends(get_current_active_user), Depends(verify_user_id)],
)
def read_search_for_cre_history(*, session: SessionDep, user_id: int, history_id: int):
    """
    Get the search history for the user.

    Parameters:
    - session: The database session.
    - user_id: The user ID.

    Returns:
    - The search history for the user.

    """
    return HistoryController.read_search_for_cre_history(session, user_id, history_id)


@router.delete(
    "/{user_id}/search-for-cre/histories/{history_id}",
    response_model=Message,
    dependencies=[Depends(get_current_active_user), Depends(verify_user_id)],
)
def delete_search_for_cre_history(
    *, session: SessionDep, user_id: int, history_id: int
):
    """
    Delete the search history for the user.

    Parameters:
    - session: The database session.
    - user_id: The user ID.

    Returns:
    - The search history for the user.

    """
    return HistoryController.delete_search_for_cre_history(session, user_id, history_id)


@router.post(
    "/motif-sampler",
    response_model=MotifSamplerResponse,
    dependencies=[Depends(get_current_active_user)],
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
        session, f_file, b_file, output_o, output_m, r, s, w, n, x, M, p, Q, z, False
    )


@router.post("/cre/export-excel", dependencies=[Depends(get_current_active_user)])
def export_cre_excel(session: SessionDep, data_in: MotifSearch):
    """
    Export CRE data to an Excel file.

    Returns:
    - The Excel file containing the CRE data.

    """
    output = ExportCreController.export_excel(session, data_in)

    # Return byte stream as StreamingResponse
    headers = {
        "Content-Disposition": "attachment; filename=cre.xlsx",
        "Content-Type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    }

    return StreamingResponse(output, headers=headers)


@router.post(
    "/cre/export-excel/send-email", dependencies=[Depends(get_current_active_user)]
)
def send_cre_excel_email(session: SessionDep, data_in: CreResultSendEmail):
    """
    Export CRE data to an Excel file and send it via email.

    Returns:
    - The Excel file containing the CRE data.

    """
    return ExportCreController.send_cre_excel_email(session, data_in)
