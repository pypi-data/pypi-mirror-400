"""
FastAPI endpoints for the envidat-converters-api.
"""
from io import StringIO
from typing import Annotated

from fastapi import HTTPException, APIRouter, Query, Request, Security
from fastapi.security import APIKeyHeader

from starlette import status
from starlette.responses import StreamingResponse

from envidat_converters.logic.constants import EnviDatConverter, ConverterExtension, ConverterFileNames
from envidat_converters.logic.converter_service import converter_logic
from envidat_converters.logic.general_helpers import get_inputtype


router = APIRouter(prefix="/internal-dataset", tags=["internal-dataset"])

authorization_header = APIKeyHeader(
    name="Authorization",
    description="CKAN cookie for logged in user passed in authorization header",
    auto_error=False,
)

# Route for converting EnviDat metadata
@router.get("/convert/{converter}",
            name="Convert EnviDat dataset to other metadata format",
            status_code=status.HTTP_200_OK,
            responses={
                200: {
                    "description": "EnviDat CKAN dataset (package) successfully converted to "
                                   "EnviDat package format. Converted format opens as a "
                                   "streamable download file."
                }
            },
        )
async def convert(
    request: Request,
    converter: EnviDatConverter,
    query: Annotated[
        str | None,
        Query(
            alias="query",
            description="Either a DOI or an EnviDat package id or name",
            openapi_examples={
                "package name": {
                    "summary": "EnviDat package name",
                    "value": "data-reliability-study-avalanche-size-and-outlines",
                },
                "package ID": {
                    "summary": "EnviDat package ID",
                    "value": "64c2ac8a-5ab9-41bf-89b7-b838d3725966",
                },
                "DOI on EnviDat": {
                    "summary": "DOI on EnviDat",
                    "value": "10.16904/envidat.423",
                },
            },
        ),
    ]=None,
    #For backwards compatibility:
    package_id: Annotated[
        str | None,
        Query(
            alias="package-id",
            description="Either a DOI or an EnviDat package id or name. "
                        "For backwards compatibility only, please use 'query' instead. "
                        "If a value for package-id is sent with a query, package-id will be ignored.",
        ),
    ] = None,
    auth: str = Security(authorization_header)
) -> StreamingResponse:
    if not query:
        if package_id:
            query = package_id
        else:
            raise HTTPException(status_code=400, detail=f"Error: Please enter either a query or a package-id")

    # Check if auth passed in Swagger UI
    if auth:
        authorization = auth
    # Check if authorization passed in header, else assign authorization to None
    else:
        authorization = request.headers.get("Authorization", None)

    try:
        inputtype = get_inputtype(query)
        result = converter_logic(converter, inputtype, query, False, authorization, "prod")
        return stream_response_attachment(result, f"{query}_{ConverterFileNames[converter.name].value}.{ConverterExtension[converter.name].value}")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error: {str(e)}")


def stream_response_attachment(data: str, filename: str) -> StreamingResponse:
    """Convert data string to StringIO object and then return it as StreamingResponse
    attachment with specified filename.

    Args:
        data (str): data that will be streamed
        filename (str): name that be assigned to streamed file

    Returns:
        StreamingResponse: streams response as attachment with specified filename

    """
    stream = StringIO(data)
    headers = {"Content-Disposition": f"attachment; filename={filename}"}
    return StreamingResponse(stream, headers=headers)