"""
Drag-and-drop field selector component for BI Dashboard.
Replaces dropdown menus with interactive drag-and-drop field selection.
"""
from dash import html, dcc
import pandas as pd
from typing import List, Optional, Dict, Any


class DragDropFieldSelector:
    """Component for drag-and-drop field selection for chart axes."""
    
    def __init__(self):
        """Initialize the drag-and-drop field selector."""
        pass
    
    def create_field_selector(
        self,
        available_fields: List[str],
        x_axis_field: Optional[str] = None,
        y_axis_field: Optional[str] = None,
        field_types: Optional[Dict[str, str]] = None,
        component_id_prefix: str = "field-selector"
    ) -> html.Div:
        """
        Create a drag-and-drop field selector component.
        
        Args:
            available_fields: List of available field names
            x_axis_field: Currently selected X-axis field
            y_axis_field: Currently selected Y-axis field
            field_types: Dictionary mapping field names to types (number, date, text)
            component_id_prefix: Prefix for component IDs
        
        Returns:
            Div containing the drag-and-drop field selector UI
        """
        field_types = field_types or {}
        
        # Create draggable and clickable field items
        field_items = []
        for field in available_fields:
            field_type = field_types.get(field, 'text')
            type_class = f"field-type-{field_type}"
            
            # Create field icon based on type
            icon_map = {
                'number': '🔢',
                'date': '📅',
                'text': '📝'
            }
            icon = icon_map.get(field_type, '📋')
            
            field_items.append(
                html.Div([
                    html.Span(icon, className="me-2"),
                    html.Span(field, className="field-name"),
                    html.Div([
                        html.Button("X", className="btn-field-assign btn-xs me-1", 
                                   id={"type": "field-to-x", "field": field},
                                   n_clicks=0, title="Assign to X-axis"),
                        html.Button("Y", className="btn-field-assign btn-xs", 
                                   id={"type": "field-to-y", "field": field},
                                   n_clicks=0, title="Assign to Y-axis")
                    ], className="field-actions")
                ],
                    className=f"draggable-field {type_class}",
                    id={"type": "draggable-field", "index": field},
                    draggable=True,
                    **{"data-field": field, "data-type": field_type},
                    title=f"Click X/Y buttons or drag to drop zone"
                )
            )
        
        # Create drop zone content
        x_display = html.Div(
            x_axis_field if x_axis_field else "Drag field here",
            className="dropped-field" if x_axis_field else "drop-zone-placeholder",
            id={"type": "x-axis-field-display", "index": "display"}
        )
        
        y_display = html.Div(
            y_axis_field if y_axis_field else "Drag field here",
            className="dropped-field" if y_axis_field else "drop-zone-placeholder",
            id={"type": "y-axis-field-display", "index": "display"}
        )
        
        return html.Div([
            # Hidden stores for selected fields (updated via callbacks)
            dcc.Store(id=f"{component_id_prefix}-x-axis-store", data=x_axis_field),
            dcc.Store(id=f"{component_id_prefix}-y-axis-store", data=y_axis_field),
            
            # Hidden buttons to trigger store updates via JavaScript
            html.Button(
                id={"type": "field-assign-btn", "axis": "x"},
                style={"display": "none"},
                n_clicks=0
            ),
            html.Button(
                id={"type": "field-assign-btn", "axis": "y"},
                style={"display": "none"},
                n_clicks=0
            ),
            
            html.Div([
                # Available Fields Panel
                html.Div([
                    html.H6("📋 Available Fields", className="mb-2"),
                    html.Small(
                        "Drag fields or click X/Y buttons to assign",
                        className="text-muted d-block mb-3"
                    ),
                    html.Div(
                        id=f"{component_id_prefix}-available-fields",
                        className="available-fields-container",
                        children=field_items if field_items else [
                            html.Div("No fields available", className="text-muted text-center p-3")
                        ]
                    )
                ], className="col-md-4 available-fields-panel"),
                
                # X-Axis Drop Zone
                html.Div([
                    html.H6("X-Axis", className="mb-2"),
                    html.Div(
                        id=f"{component_id_prefix}-x-axis-dropzone",
                        className="drop-zone",
                        children=[x_display],
                        **{"data-axis": "x"}
                    )
                ], className="col-md-4 axis-dropzone"),
                
                # Y-Axis Drop Zone
                html.Div([
                    html.H6("Y-Axis", className="mb-2"),
                    html.Div(
                        id=f"{component_id_prefix}-y-axis-dropzone",
                        className="drop-zone",
                        children=[y_display],
                        **{"data-axis": "y"}
                    )
                ], className="col-md-4 axis-dropzone")
            ], className="row drag-drop-field-selector"),
            
            # Include JavaScript for drag-and-drop
            self._create_drag_drop_script(component_id_prefix)
        ], className="drag-drop-container")
    
    def _create_drag_drop_script(self, component_id_prefix: str) -> html.Div:
        """Create JavaScript for drag-and-drop functionality."""
        return html.Div([
            html.Script(f"""
            (function() {{
                function initDragDrop() {{
                    const prefix = '{component_id_prefix}';
                    const xDropZone = document.getElementById(prefix + '-x-axis-dropzone');
                    const yDropZone = document.getElementById(prefix + '-y-axis-dropzone');
                    
                    if (!xDropZone || !yDropZone) {{
                        setTimeout(initDragDrop, 500);
                        return;
                    }}
                    
                    function setupDraggableFields() {{
                        const fields = document.querySelectorAll('.draggable-field');
                        fields.forEach(field => {{
                            field.addEventListener('dragstart', function(e) {{
                                e.dataTransfer.setData('text/plain', this.getAttribute('data-field'));
                                e.dataTransfer.effectAllowed = 'move';
                                this.classList.add('dragging');
                            }});
                            
                            field.addEventListener('dragend', function(e) {{
                                this.classList.remove('dragging');
                            }});
                        }});
                    }}
                    
                    function setupDropZone(zone, axis) {{
                        zone.addEventListener('dragover', function(e) {{
                            e.preventDefault();
                            e.dataTransfer.dropEffect = 'move';
                            this.classList.add('drag-over');
                        }});
                        
                        zone.addEventListener('dragleave', function(e) {{
                            this.classList.remove('drag-over');
                        }});
                        
                        zone.addEventListener('drop', function(e) {{
                            e.preventDefault();
                            this.classList.remove('drag-over');
                            
                            const fieldName = e.dataTransfer.getData('text/plain');
                            if (fieldName) {{
                                const display = this.querySelector('.drop-zone-placeholder, .dropped-field');
                                if (display) {{
                                    display.textContent = fieldName;
                                    display.className = 'dropped-field';
                                    display.setAttribute('data-field', fieldName);
                                    
                                    // Store field name in data attribute and trigger button click
                                    const btn = document.querySelector('[data-axis="' + axis + '"]');
                                    if (btn) {{
                                        btn.setAttribute('data-field-name', fieldName);
                                        btn.click();
                                    }}
                                }}
                            }}
                        }});
                        
                        // Double-click to remove
                        zone.addEventListener('dblclick', function() {{
                            const display = this.querySelector('.dropped-field');
                            if (display) {{
                                display.textContent = 'Drag field here';
                                display.className = 'drop-zone-placeholder';
                                display.removeAttribute('data-field');
                                
                                const btn = document.querySelector('[data-axis="' + axis + '"]');
                                if (btn) {{
                                    btn.removeAttribute('data-field-name');
                                    btn.click();
                                }}
                            }}
                        }});
                    }}
                    
                    setupDraggableFields();
                    setupDropZone(xDropZone, 'x');
                    setupDropZone(yDropZone, 'y');
                    
                    // Watch for new fields
                    const observer = new MutationObserver(setupDraggableFields);
                    const availableFields = document.getElementById(prefix + '-available-fields');
                    if (availableFields) {{
                        observer.observe(availableFields, {{ childList: true, subtree: true }});
                    }}
                }}
                
                if (document.readyState === 'loading') {{
                    document.addEventListener('DOMContentLoaded', initDragDrop);
                }} else {{
                    initDragDrop();
                }}
            }})();
            """)
        ], id=f"{component_id_prefix}-script-container", style={"display": "none"})
