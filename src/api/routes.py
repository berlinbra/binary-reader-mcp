from fastapi import APIRouter, HTTPException
from .schemas import BinaryAnalysisRequest, BinaryAnalysisResponse
from ..binary_reader import UnrealAssetReader

router = APIRouter()

@router.post("/analyze", response_model=BinaryAnalysisResponse)
async def analyze_binary_file(request: BinaryAnalysisRequest):
    try:
        with UnrealAssetReader(request.file_path) as reader:
            header = reader.read_header()
            metadata = reader.read_metadata()
            
            return BinaryAnalysisResponse(
                file_path=request.file_path,
                header=header,
                metadata=metadata,
                format="unreal"
            )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))