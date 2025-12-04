// Drag-and-drop functionality for field selection
(function() {
    function initDragDrop() {
        const xDropZone = document.getElementById('field-selector-x-axis-dropzone');
        const yDropZone = document.getElementById('field-selector-y-axis-dropzone');
        const xTrigger = document.getElementById('field-selector-x-axis-trigger');
        const yTrigger = document.getElementById('field-selector-y-axis-trigger');
        
        if (!xDropZone || !yDropZone) {
            setTimeout(initDragDrop, 500);
            return;
        }
        
        function setupDraggableFields() {
            const fields = document.querySelectorAll('.draggable-field');
            fields.forEach(field => {
                // Skip if already has listeners (check for a marker)
                if (field.hasAttribute('data-initialized')) {
                    return;
                }
                field.setAttribute('data-initialized', 'true');
                
                const fieldName = field.getAttribute('data-field');
                
                // Drag functionality
                field.addEventListener('dragstart', function(e) {
                    e.dataTransfer.setData('text/plain', fieldName);
                    e.dataTransfer.effectAllowed = 'move';
                    this.classList.add('dragging');
                    e.stopPropagation();
                });
                
                field.addEventListener('dragend', function(e) {
                    this.classList.remove('dragging');
                });
                
                // Click to highlight
                field.addEventListener('click', function(e) {
                    // Don't trigger if clicking on buttons
                    if (e.target.classList.contains('btn-field-assign')) {
                        return;
                    }
                    // Highlight the field
                    this.style.transform = 'scale(1.05)';
                    setTimeout(() => {
                        this.style.transform = '';
                    }, 200);
                });
            });
        }
        
        function setupDropZone(zone, trigger, axis) {
            if (!zone) return;
            
            zone.addEventListener('dragover', function(e) {
                e.preventDefault();
                e.dataTransfer.dropEffect = 'move';
                this.classList.add('drag-over');
            });
            
            zone.addEventListener('dragleave', function(e) {
                // Only remove if actually leaving the zone
                if (!this.contains(e.relatedTarget)) {
                    this.classList.remove('drag-over');
                }
            });
            
            zone.addEventListener('drop', function(e) {
                e.preventDefault();
                this.classList.remove('drag-over');
                
                const fieldName = e.dataTransfer.getData('text/plain');
                if (fieldName) {
                    let display = this.querySelector('.drop-zone-placeholder, .dropped-field');
                    if (!display) {
                        display = document.createElement('div');
                        display.className = 'dropped-field';
                        this.appendChild(display);
                    }
                    
                    display.textContent = fieldName;
                    display.className = 'dropped-field';
                    display.setAttribute('data-field', fieldName);
                    
                    // Update the Dash store via display element ID
                    const displayId = axis === 'x' ? 
                        '{"type":"x-axis-field-display","index":"display"}' :
                        '{"type":"y-axis-field-display","index":"display"}';
                    
                    // Trigger a custom event that Dash can catch
                    window.dispatchEvent(new CustomEvent('fieldDropped', {
                        detail: { axis: axis, field: fieldName }
                    }));
                }
            });
            
            // Double-click to remove field
            zone.addEventListener('dblclick', function() {
                const display = this.querySelector('.dropped-field');
                if (display) {
                    display.textContent = 'Drag field here';
                    display.className = 'drop-zone-placeholder';
                    display.removeAttribute('data-field');
                    
                    window.dispatchEvent(new CustomEvent('fieldRemoved', {
                        detail: { axis: axis }
                    }));
                }
            });
        }
        
        setupDraggableFields();
        setupDropZone(xDropZone, xTrigger, 'x');
        setupDropZone(yDropZone, yTrigger, 'y');
        
        // Watch for new fields being added
        const observer = new MutationObserver(function(mutations) {
            setupDraggableFields();
        });
        
        const availableFields = document.getElementById('field-selector-available-fields');
        if (availableFields) {
            observer.observe(availableFields, { childList: true, subtree: true });
        }
    }
    
    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initDragDrop);
    } else {
        initDragDrop();
    }
    
    // Re-initialize after Dash updates
    if (window.dash_clientside) {
        document.addEventListener('dash:beforeUpdate', function() {
            setTimeout(initDragDrop, 100);
        });
    }
})();

