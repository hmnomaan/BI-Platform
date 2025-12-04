#!/usr/bin/env python3
"""
Test script to verify field selector functionality.
"""
import pandas as pd
import sys
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from bi_dashboard.components.drag_drop_field_selector import DragDropFieldSelector
from bi_dashboard.core.data_connector import DataSourceManager
from bi_dashboard.utils.auto_chart_generator import AutoChartGenerator


def test_field_selector():
    """Test field selector component."""
    print("=" * 60)
    print("Testing Field Selector Component")
    print("=" * 60)
    
    # Create sample data
    print("\n1. Creating sample data...")
    df = pd.DataFrame({
        "date": pd.date_range("2023-01-01", periods=100, freq="D"),
        "sales": [1000 + i * 10 for i in range(100)],
        "region": ["North", "South", "East", "West"] * 25,
        "product": ["Product A", "Product B", "Product C"] * 33 + ["Product A"],
        "revenue": [5000 + i * 50 for i in range(100)]
    })
    print(f"   ✓ Created sample data with {len(df)} rows")
    print(f"   ✓ Columns: {list(df.columns)}")
    
    # Create components
    print("\n2. Initializing components...")
    selector = DragDropFieldSelector()
    data_manager = DataSourceManager()
    auto_chart_gen = AutoChartGenerator(data_manager)
    print("   ✓ Selector, DataManager, and AutoChartGenerator initialized")
    
    # Get schema
    print("\n3. Inferring schema...")
    schema = data_manager.infer_schema(df)
    print(f"   ✓ Schema: {schema}")
    
    # Get auto-selected fields
    print("\n4. Getting auto-selected fields...")
    x_field, y_field = auto_chart_gen.get_auto_selected_fields(df)
    print(f"   ✓ Auto-selected X-axis: {x_field}")
    print(f"   ✓ Auto-selected Y-axis: {y_field}")
    
    # Create field selector
    print("\n5. Creating field selector component...")
    selector_component = selector.create_field_selector(
        available_fields=list(df.columns),
        x_axis_field=x_field,
        y_axis_field=y_field,
        field_types=schema,
        component_id_prefix="field-selector"
    )
    print("   ✓ Field selector component created")
    
    # Verify component structure
    print("\n6. Verifying component structure...")
    
    # Check if it's a Div
    from dash import html
    assert isinstance(selector_component, html.Div), "Selector should be a Div"
    print("   ✓ Component is a Div")
    
    # Verify children exist
    assert selector_component.children is not None, "Component should have children"
    print(f"   ✓ Component has {len(selector_component.children) if isinstance(selector_component.children, list) else 1} child elements")
    
    # Check for available fields container
    children_str = str(selector_component.children)
    assert "available-fields-container" in children_str or "draggable-field" in children_str, \
        "Component should contain available fields"
    print("   ✓ Component contains available fields")
    
    # Verify all fields are included
    fields_str = str(selector_component.children)
    for col in df.columns:
        assert col in fields_str, f"Field '{col}' not found in selector"
    print(f"   ✓ All {len(df.columns)} fields are included in selector")
    
    # Test with different data
    print("\n7. Testing with different data...")
    df2 = pd.DataFrame({
        "name": ["Alice", "Bob", "Charlie"],
        "age": [25, 30, 35],
        "salary": [50000, 60000, 70000],
        "department": ["Sales", "Engineering", "Sales"]
    })
    
    schema2 = data_manager.infer_schema(df2)
    x_field2, y_field2 = auto_chart_gen.get_auto_selected_fields(df2)
    
    selector_component2 = selector.create_field_selector(
        available_fields=list(df2.columns),
        x_axis_field=x_field2,
        y_axis_field=y_field2,
        field_types=schema2,
        component_id_prefix="field-selector"
    )
    
    fields_str2 = str(selector_component2.children)
    for col in df2.columns:
        assert col in fields_str2, f"Field '{col}' not found in second selector"
    print(f"   ✓ All {len(df2.columns)} fields are included in second selector")
    
    # Summary
    print("\n" + "=" * 60)
    print("✓ All tests passed!")
    print("=" * 60)
    print("\nField Selector Features:")
    print("  • Shows all available fields from dataset")
    print("  • Supports drag-and-drop to axes")
    print("  • Click X/Y buttons to assign fields")
    print("  • Auto-selects best fields for initial chart")
    print("  • Displays field types (number, date, text)")
    print("  • Double-click drop zone to clear selection")
    print("\n")


if __name__ == "__main__":
    try:
        test_field_selector()
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
