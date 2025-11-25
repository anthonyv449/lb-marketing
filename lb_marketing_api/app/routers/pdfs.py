"""
PDF download endpoints
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
import logging

from ..services.storage import storage_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/pdfs", tags=["pdfs"])

# PDF file names in Azure Storage
PDF_FILES = {
    "business": "30-day-plan-boost-engagement-business.pdf",
    "affiliate": "30-day-plan-boost-engagement-affiliate.pdf"
}


@router.get("/download/business")
async def download_business_plan():
    """
    Download the 30 Day Plan To Boost Engagement for your Business PDF
    """
    return _download_pdf("business", PDF_FILES["business"])


@router.get("/download/affiliate")
async def download_affiliate_plan():
    """
    Download the 30 Day Plan To Boost Engagement for your Affiliate Marketing Business PDF
    """
    return _download_pdf("affiliate", PDF_FILES["affiliate"])


@router.get("/info")
async def get_pdf_info():
    """
    Get information about PDF files in storage (for debugging)
    """
    if not storage_service.blob_service_client:
        raise HTTPException(
            status_code=503,
            detail="Azure Storage is not configured"
        )
    
    info = {}
    for plan_type, blob_name in PDF_FILES.items():
        try:
            blob_client = storage_service.blob_service_client.get_blob_client(
                container=storage_service.container_name,
                blob=blob_name
            )
            
            if blob_client.exists():
                props = blob_client.get_blob_properties()
                # Try to download a small chunk to verify
                download_stream = blob_client.download_blob()
                full_data = download_stream.readall()
                
                info[plan_type] = {
                    "exists": True,
                    "size_in_storage": props.size,
                    "size_downloaded": len(full_data),
                    "content_type": props.content_settings.content_type if props.content_settings else None,
                    "pdf_header": full_data[:20].decode('latin-1', errors='ignore') if len(full_data) >= 20 else None,
                    "pdf_footer": full_data[-20:].decode('latin-1', errors='ignore') if len(full_data) >= 20 else None,
                    "is_valid_pdf": full_data.startswith(b'%PDF') and b'%%EOF' in full_data[-100:],
                }
            else:
                info[plan_type] = {
                    "exists": False,
                }
        except Exception as e:
            info[plan_type] = {
                "exists": "unknown",
                "error": str(e)
            }
    
    return info


def _download_pdf(plan_type: str, blob_name: str) -> Response:
    """
    Helper function to download a PDF from Azure Storage
    
    Args:
        plan_type: Type of plan (for error messages)
        blob_name: Name of the blob in Azure Storage
        
    Returns:
        Response with PDF content
    """
    if not storage_service.blob_service_client:
        logger.error("Azure Storage not configured")
        raise HTTPException(
            status_code=503,
            detail="PDF download service is not available. Azure Storage is not configured."
        )
    
    logger.info(f"Attempting to download PDF: {blob_name}")
    pdf_data = storage_service.get_blob(blob_name)
    
    if pdf_data is None:
        logger.warning(f"PDF not found in storage: {blob_name}")
        raise HTTPException(
            status_code=404,
            detail=f"PDF file not found. Please ensure '{blob_name}' is uploaded to Azure Storage."
        )
    
    if len(pdf_data) == 0:
        logger.error(f"PDF data is empty for: {blob_name}")
        raise HTTPException(
            status_code=500,
            detail=f"PDF file is empty or corrupted: {blob_name}"
        )
    
    # Verify PDF structure
    pdf_str = pdf_data.decode('latin-1', errors='ignore')
    if not pdf_str.startswith('%PDF'):
        logger.error(f"PDF does not start with %PDF header: {blob_name}")
        raise HTTPException(
            status_code=500,
            detail=f"PDF file appears to be corrupted (missing PDF header): {blob_name}"
        )
    
    if not pdf_str.rstrip().endswith('%%EOF'):
        logger.warning(f"PDF does not end with %%EOF: {blob_name}. Last 20 bytes: {pdf_data[-20:]}")
        # Don't fail here, as some PDFs might have trailing whitespace
    
    logger.info(f"Successfully retrieved PDF: {blob_name} ({len(pdf_data)} bytes)")
    logger.info(f"PDF header: {pdf_data[:20]}")
    logger.info(f"PDF footer: {pdf_data[-20:]}")
    
    # Return as Response with PDF bytes directly
    # For binary file downloads, Response with content=bytes is the correct approach
    # The media_type parameter automatically sets the Content-Type header
    return Response(
        content=pdf_data,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{blob_name}"',
            "Content-Length": str(len(pdf_data)),
        }
    )

