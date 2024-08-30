import os
import subprocess
from fastapi import File, Form, HTTPException, UploadFile, status

from models.factors import MotifSamplerResponse


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
    # handle file upload
    f_file_path = await save_upload_file(f_file)
    b_file_path = await save_upload_file(b_file) if b_file else None

    parameters = {
        "r": r,
        "s": s,
        "w": w,
        "n": n,
        "x": x,
        "M": M,
        "p": p,
        "Q": Q,
        "z": z,
    }

    try:
        motifs = await run_motif_sampler(
            f_file_path, b_file_path, output_o, output_m, **parameters
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )

    return MotifSamplerResponse(
        status="success",
        message="Motif sampler completed successfully.",
        results=motifs,
    )


async def save_upload_file(uploaded_file: UploadFile):
    # Create media_motifsampler directory if not exists
    save_dir = "./app/media_motifsampler"
    os.makedirs(save_dir, exist_ok=True)

    file_path = os.path.join(save_dir, uploaded_file.filename)

    # Save file into media_motifsampler
    with open(file_path, "wb") as f:
        content = await uploaded_file.read()
        f.write(content)

    return uploaded_file.filename

async def run_motif_sampler(
    f_file_path: str,
    b_file_path: str | None = None,
    output_o: str = "output.txt",
    output_m: str = "output.mtrx",
    **parameters,
) -> list[str]:
    """
    Runs the motif sampler tool with the given parameters.

    Args:
        f_file_path (str): The file path of the input file.
        b_file_path (str, optional): The file path of the background file. Defaults to None.
        output_o (str, optional): The output file path for the motifs. Defaults to "output.txt".
        output_m (str, optional): The output file path for the motif matrix. Defaults to "output.mtrx".
        **parameters: Additional parameters to be passed to the motif sampler tool.

    Returns:
        list[str]: A list of motifs extracted by the motif sampler tool.

    Raises:
        Exception: If the motif sampler fails with an error.

    """
    # Construct command line
    command = [
        "cd",
        "./app/media_motifsampler",
        "&&",
        "./motif-sampler",
        "-f",
        f_file_path,
    ]
    if b_file_path:
        command.extend(["-b", b_file_path])
    command.extend(["-o", output_o, "-m", output_m])
    for key, value in parameters.items():
        if value is not None:
            command.extend([f"-{key}", str(value)])

    # Execute command line
    command = " ".join(command)
    process = subprocess.run(command, capture_output=True, text=True, shell=True)

    # Handle reusults
    if process.returncode == 0:
        motifs = []
        for line in process.stdout.splitlines():
            if line.startswith("#Consensus"):
                motif = line.split(":")[1].strip()
                motifs.append(motif)
        return motifs
    else:
        error_message = process.stderr.strip()
        raise Exception(f"Motif sampler failed with error: {error_message}")