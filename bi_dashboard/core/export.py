"""
Chart export functionality for BI Dashboard.
Supports exporting charts as images (PNG, JPEG) and PDF.
"""
import plotly.graph_objects as go
from pathlib import Path
from typing import Dict, Any, Optional
import base64
import io

try:
    import kaleido
    KALEIDO_AVAILABLE = True
except ImportError:
    KALEIDO_AVAILABLE = False

try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib.units import inch
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

from ..utils.helpers import get_logger


logger = get_logger("ChartExport")


class ChartExporter:
    """Export charts to various formats."""
    
    def __init__(self):
        """Initialize the chart exporter."""
        if not KALEIDO_AVAILABLE:
            logger.warning("Kaleido not installed. Image export may not work. Install with: pip install kaleido")
    
    def export_image(self, fig: go.Figure, output_path: Path, 
                    format: str = "png", width: int = 1200, height: int = 800,
                    scale: float = 1.0) -> Dict[str, Any]:
        """
        Export chart to image file.
        
        Args:
            fig: Plotly figure object
            output_path: Path to save the image
            format: Image format (png, jpeg, svg, webp)
            width: Image width in pixels
            height: Image height in pixels
            scale: Scale factor for higher resolution
        
        Returns:
            Dictionary with export status and file path
        """
        if not KALEIDO_AVAILABLE:
            raise ImportError("Kaleido is required for image export. Install with: pip install kaleido")
        
        try:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Update figure layout
            fig.update_layout(width=width, height=height)
            
            # Export using kaleido
            fig.write_image(
                str(output_path),
                format=format,
                width=width,
                height=height,
                scale=scale
            )
            
            logger.info(f"Chart exported to {output_path}")
            
            return {
                "status": "success",
                "format": format,
                "path": str(output_path),
                "size": output_path.stat().st_size
            }
        except Exception as e:
            logger.error(f"Failed to export image: {e}")
            raise
    
    def export_pdf(self, fig: go.Figure, output_path: Path,
                  title: Optional[str] = None,
                  width: int = 1200, height: int = 800) -> Dict[str, Any]:
        """
        Export chart to PDF file.
        
        Args:
            fig: Plotly figure object
            output_path: Path to save the PDF
            title: Optional title for the PDF
            width: Chart width in pixels
            height: Chart height in pixels
        
        Returns:
            Dictionary with export status and file path
        """
        if not KALEIDO_AVAILABLE:
            raise ImportError("Kaleido is required for PDF export. Install with: pip install kaleido")
        
        if not REPORTLAB_AVAILABLE:
            # Fallback: Export as image first, then convert
            logger.warning("ReportLab not available. Using image-based PDF export.")
            return self._export_pdf_via_image(fig, output_path, title, width, height)
        
        try:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # First export as image
            temp_image = output_path.parent / f"{output_path.stem}_temp.png"
            self.export_image(fig, temp_image, format="png", width=width, height=height)
            
            # Create PDF with ReportLab
            doc = SimpleDocTemplate(str(output_path), pagesize=A4)
            story = []
            styles = getSampleStyleSheet()
            
            if title:
                story.append(Paragraph(title, styles['Title']))
                story.append(Spacer(1, 0.2*inch))
            
            # Add image
            img = Image(str(temp_image), width=6*inch, height=4.5*inch)
            story.append(img)
            
            doc.build(story)
            
            # Clean up temp file
            temp_image.unlink()
            
            logger.info(f"Chart exported to PDF: {output_path}")
            
            return {
                "status": "success",
                "format": "pdf",
                "path": str(output_path),
                "size": output_path.stat().st_size
            }
        except Exception as e:
            logger.error(f"Failed to export PDF: {e}")
            raise
    
    def _export_pdf_via_image(self, fig: go.Figure, output_path: Path,
                            title: Optional[str], width: int, height: int) -> Dict[str, Any]:
        """Export PDF using image conversion (fallback method)."""
        # Export as PNG first
        temp_png = output_path.parent / f"{output_path.stem}_temp.png"
        self.export_image(fig, temp_png, format="png", width=width, height=height)
        
        # For now, just copy the PNG (in production, use a proper PDF library)
        # This is a simplified version
        logger.warning("PDF export via image conversion - using PNG as fallback")
        return {
            "status": "partial",
            "format": "png",
            "path": str(temp_png),
            "message": "PDF export requires ReportLab. PNG exported instead."
        }
    
    def export_html(self, fig: go.Figure, output_path: Path,
                   title: Optional[str] = None,
                   include_plotlyjs: str = "cdn") -> Dict[str, Any]:
        """
        Export chart to standalone HTML file.
        
        Args:
            fig: Plotly figure object
            output_path: Path to save the HTML
            title: Optional title for the HTML page
            include_plotlyjs: How to include Plotly.js ('cdn', 'inline', 'directory')
        
        Returns:
            Dictionary with export status and file path
        """
        try:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Export HTML
            fig.write_html(
                str(output_path),
                include_plotlyjs=include_plotlyjs,
                config={'displayModeBar': True}
            )
            
            logger.info(f"Chart exported to HTML: {output_path}")
            
            return {
                "status": "success",
                "format": "html",
                "path": str(output_path),
                "size": output_path.stat().st_size
            }
        except Exception as e:
            logger.error(f"Failed to export HTML: {e}")
            raise
    
    def export_base64(self, fig: go.Figure, format: str = "png",
                     width: int = 1200, height: int = 800) -> str:
        """
        Export chart as base64 encoded string.
        
        Args:
            fig: Plotly figure object
            format: Image format (png, jpeg)
            width: Image width
            height: Image height
        
        Returns:
            Base64 encoded string
        """
        if not KALEIDO_AVAILABLE:
            raise ImportError("Kaleido is required for base64 export")
        
        try:
            # Export to bytes
            img_bytes = fig.to_image(format=format, width=width, height=height)
            
            # Encode to base64
            b64_string = base64.b64encode(img_bytes).decode('utf-8')
            
            return b64_string
        except Exception as e:
            logger.error(f"Failed to export base64: {e}")
            raise

