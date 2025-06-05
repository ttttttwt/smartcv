class ElementEventHandler {
    constructor(elementManager, stage, layer) {
        this.elementManager = elementManager;
        this.stage = stage;
        this.layer = layer;
        this.isDragging = false;
        this.dragStartPos = null;
        this.transformStartAttrs = null; // To store attributes at transform start
    }

    setupElementEvents(element) {
        // Clear any existing events to avoid duplicates
        element.off('dragstart dragmove dragend click tap mouseenter mouseleave contextmenu transformstart transform transformend dblclick dbltap');
        
        this.setupDragEvents(element);
        this.setupMouseEvents(element);
        this.setupTransformEvents(element); // Renamed from setupTransformEvents to a more generic name
        this.setupSpecialEvents(element);
        
        // Ensure element is properly configured for interaction
        element.setAttrs({
            draggable: true,
            name: 'cv-element'
        });
        
        console.log('Events setup for element:', element.id(), element.getClassName());
    }

    setupDragEvents(element) {
        // Ensure element is draggable
        element.draggable(true);
        
        element.on('dragstart', (e) => {
            this.isDragging = true;
            this.dragStartPos = { ...element.position() }; // Store initial position
            
            // If the element is part of a transformer, dragging the element itself should work
            // No need to move to top if transformer handles it or if it's already selected
            // element.moveToTop(); 
            element.opacity(0.8);
            
            const canvasContainer = document.querySelector('.canvas-stage');
            if (canvasContainer) {
                canvasContainer.classList.add('dragging');
            }
            
            if (this.elementManager.selectedElement !== element) {
                this.elementManager.selectElement(element);
            }
            
            element.getStage().container().style.cursor = 'grabbing';
            
            console.log('Drag started for element:', element.id());
        });
        
        element.on('dragmove', (e) => {
            const newPos = element.position();
            
            // REMOVE: this.elementManager.updateSelectionBorder(true);
            this.showPositionFeedback(newPos);
            
            // Update properties panel with new position
            this.updatePropertiesPanelPosition(newPos);
        });
        
        element.on('dragend', (e) => {
            this.isDragging = false;
            
            element.opacity(1);
            
            const canvasContainer = document.querySelector('.canvas-stage');
            if (canvasContainer) {
                canvasContainer.classList.remove('dragging');
            }
            
            element.getStage().container().style.cursor = 'move';
            
            // REMOVE: this.elementManager.updateSelectionBorder();
            this.elementManager.updatePropertiesPanel(); // Update panel with final position
            this.hidePositionFeedback();
            
            const finalPos = element.position();
            console.log('Drag ended. New position:', finalPos);
            
            // Add to history only if position actually changed
            if (this.dragStartPos.x !== finalPos.x || this.dragStartPos.y !== finalPos.y) {
                this.elementManager.addToHistory('move', {
                    elementId: element.id(),
                    oldPosition: this.dragStartPos,
                    newPosition: { ...finalPos }
                });
            }
        });
    }

    setupMouseEvents(element) {
        // Click selection
        element.on('click tap', (e) => {
            e.cancelBubble = true;
            this.elementManager.selectElement(element);
            console.log('Element clicked and selected:', element.id());
        });
        
        element.on('mouseenter', () => {
            if (!this.isDragging) {
                element.getStage().container().style.cursor = 'move';
                
                element.to({
                    scaleX: element.scaleX() * 1.02,
                    scaleY: element.scaleY() * 1.02,
                    duration: 0.1
                });
            }
        });
        
        element.on('mouseleave', () => {
            if (!this.isDragging) {
                element.getStage().container().style.cursor = 'default';
                
                element.to({
                    scaleX: element.scaleX() / 1.02,
                    scaleY: element.scaleY() / 1.02,
                    duration: 0.1
                });
            }
        });

        element.on('contextmenu', (e) => {
            e.evt.preventDefault();
            this.elementManager.selectElement(element);
            this.showContextMenu(e.evt.clientX, e.evt.clientY);
        });
    }

    setupTransformEvents(element) {
        // Listen for transform events on the element itself
        element.on('transformstart', (e) => {
            console.log('Transform started for element:', element.id());
            this.transformStartAttrs = { ...element.getAttrs() };
            // Store relevant attributes like x, y, width, height, scaleX, scaleY, rotation
            // Konva automatically updates these, so we capture the state *before* transformation.
            // For width/height of text, it's tricky. Let's capture scale and fontSize.
            this.transformStartAttrs.width = element.width();
            this.transformStartAttrs.height = element.height();
            if (element.getClassName() === 'Line') {
                this.transformStartAttrs.points = [...element.points()];
            }
        });

        element.on('transform', (e) => {
            // If the element is a text type that should not be scaled:
            const elementData = this.elementManager.elements.get(element.id());
            const type = elementData?.type;
            const textTypes = ['text', 'heading', 'paragraph', 'list'];

            if (textTypes.includes(type)) {
                const oldScaleX = element.scaleX();
                const oldScaleY = element.scaleY();

                // Check if scale has actually changed to avoid unnecessary updates
                // and potential floating point issues if it's already 1.
                // This ensures that width/height are adjusted according to the scale change,
                // and then scale is reset to 1.
                if (oldScaleX !== 1 || oldScaleY !== 1) {
                    element.setAttrs({
                        width: element.width() * oldScaleX,
                        height: element.height() * oldScaleY,
                        scaleX: 1,
                        scaleY: 1,
                    });
                }
            }
            // console.log('Transforming element:', element.id()); // Optional: real-time update
        });

        element.on('transformend', (e) => {
            console.log('Transform ended for element:', element.id());
            this.elementManager.updatePropertiesPanel();
            
            const currentAttrs = { ...element.getAttrs() };
            currentAttrs.width = element.width(); // Get current width after transform
            currentAttrs.height = element.height(); // Get current height after transform
            if (element.getClassName() === 'Line') {
                currentAttrs.points = [...element.points()];
            }


            this.elementManager.addToHistory('transform', {
                elementId: element.id(),
                oldAttrs: this.transformStartAttrs,
                newAttrs: currentAttrs
            });
            this.transformStartAttrs = null; // Reset
        });
    }

    setupSpecialEvents(element) {
        if (element.getClassName() === 'Text') {
            element.on('dblclick dbltap', () => {
                this.editTextElement(element);
            });
        }
        
        // Add interactive rating functionality
        if (element.hasName('rating-element')) {
            element.on('click tap', (e) => {
                this.handleRatingClick(element, e);
            });
        }
    }

    handleRatingClick(ratingElement, e) {
        const elementData = this.elementManager.elements.get(ratingElement.id());
        if (!elementData || elementData.type !== 'rating') return;

        // Get click position relative to the rating element
        const pos = ratingElement.getRelativePointerPosition();
        const stars = ratingElement.find('Text');
        
        if (stars.length === 0) return;

        // Calculate which star was clicked
        const starSize = stars[0].fontSize();
        const spacing = 5; // Default spacing
        const starIndex = Math.floor(pos.x / (starSize + spacing));
        
        if (starIndex >= 0 && starIndex < stars.length) {
            const newRating = starIndex + 1;
            
            // Update the rating
            this.elementManager.updateElementProperty(ratingElement, 'ratingValue', newRating);
            
            // Update properties panel
            this.elementManager.updatePropertiesPanel();
        }
    }

    editTextElement(textElement) {
        const textPosition = textElement.getAbsolutePosition();
        const stageBox = this.stage.container().getBoundingClientRect();
        
        const elementData = this.elementManager.elements.get(textElement.id()); // Get element data
        const isListElement = elementData && elementData.type === 'list'; // Check if it's a list element
        const bulletStyle = isListElement ? (elementData.properties.bulletStyle || '•') : '';

        const textarea = document.createElement('textarea');
        textarea.value = textElement.text();
        textarea.style.position = 'absolute';
        textarea.style.top = (stageBox.top + textPosition.y) + 'px';
        textarea.style.left = (stageBox.left + textPosition.x) + 'px';
        textarea.style.width = Math.max(textElement.width(), 200) + 'px';
        textarea.style.height = Math.max(textElement.height(), 50) + 'px';
        textarea.style.fontSize = textElement.fontSize() + 'px';
        textarea.style.fontFamily = textElement.fontFamily();
        textarea.style.border = '2px solid #667eea';
        textarea.style.padding = '5px';
        textarea.style.margin = '0';
        textarea.style.overflow = 'hidden';
        textarea.style.background = 'white';
        textarea.style.outline = 'none';
        textarea.style.resize = 'none';
        textarea.style.zIndex = '1000';
        
        document.body.appendChild(textarea);
        textarea.focus();
        textarea.select();
        
        const removeTextarea = () => {
            textElement.text(textarea.value);
            this.layer.draw();
            document.body.removeChild(textarea);
            this.elementManager.updatePropertiesPanel();
        };
        
        textarea.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                if (isListElement) {
                    const start = textarea.selectionStart;
                    const end = textarea.selectionEnd;
                    let textToInsert = '\n';
                    
                    if (bulletStyle === '1.') {
                        // Count existing lines to determine next number
                        const currentLines = textarea.value.substring(0, start).split('\n');
                        const lastLine = currentLines[currentLines.length - 1];
                        const match = lastLine.match(/^(\d+)\.\s*/);
                        const nextNumber = match ? parseInt(match[1], 10) + 1 : 1;
                        textToInsert += `${nextNumber}. `;
                    } else {
                        textToInsert += `${bulletStyle} `;
                    }
                    
                    textarea.value = textarea.value.substring(0, start) + textToInsert + textarea.value.substring(end);
                    textarea.selectionStart = textarea.selectionEnd = start + textToInsert.length;
                } else {
                    removeTextarea();
                }
            } else if (e.key === 'Escape') {
                removeTextarea();
            }
        });
        
        textarea.addEventListener('blur', removeTextarea);
    }

    handleFontControl(button) {
        if (!this.elementManager.selectedElement) return;
        
        const element = this.elementManager.selectedElement;
        const style = button.dataset.style;
        const isActive = button.classList.contains('active');
        
        if (style === 'bold') {
            const currentStyle = element.fontStyle();
            let newStyle = currentStyle.replace('bold', '').trim();
            if (!isActive) {
                newStyle = newStyle ? `${newStyle} bold` : 'bold';
            }
            element.fontStyle(newStyle);
        } else if (style === 'italic') {
            const currentStyle = element.fontStyle();
            let newStyle = currentStyle.replace('italic', '').trim();
            if (!isActive) {
                newStyle = newStyle ? `${newStyle} italic` : 'italic';
            }
            element.fontStyle(newStyle);
        } else if (style === 'underline') {
            element.textDecoration(isActive ? '' : 'underline');
        }
        
        button.classList.toggle('active');
        this.layer.draw();
    }

    showPositionFeedback(position) {
        let feedback = document.getElementById('position-feedback');
        if (!feedback) {
            feedback = document.createElement('div');
            feedback.id = 'position-feedback';
            feedback.style.cssText = `
                position: fixed;
                background: rgba(0, 0, 0, 0.8);
                color: white;
                padding: 4px 8px;
                border-radius: 4px;
                font-size: 12px;
                font-family: monospace;
                z-index: 1000;
                pointer-events: none;
                white-space: nowrap;
            `;
            document.body.appendChild(feedback);
        }
        
        feedback.textContent = `X: ${Math.round(position.x)}, Y: ${Math.round(position.y)}`;
        feedback.style.display = 'block';
        
        // Calculate feedback position accounting for current zoom and stage position
        const stage = this.stage;
        const scale = stage.scaleX();
        const stagePosition = stage.position();
        const rect = stage.container().getBoundingClientRect();
        
        // Transform stage coordinates to screen coordinates
        const screenX = rect.left + (position.x * scale) + stagePosition.x;
        const screenY = rect.top + (position.y * scale) + stagePosition.y;
        
        feedback.style.left = (screenX + 10) + 'px';
        feedback.style.top = (screenY - 30) + 'px';
    }

    hidePositionFeedback() {
        const feedback = document.getElementById('position-feedback');
        if (feedback) {
            feedback.style.display = 'none';
        }
    }

    showContextMenu(x, y) {
        // TODO: Implement context menu
        console.log('Context menu at:', x, y);
    }

    setupKeyboardMovement() {
        document.addEventListener('keydown', (e) => {
            if (!this.elementManager.selectedElement || this.isEditingText()) return; // Add check for text editing
            
            // Calculate movement step based on current zoom level for consistent movement
            const stage = this.stage;
            const scale = stage.scaleX();
            const baseStep = e.shiftKey ? 10 : 1;
            const step = baseStep / scale; // Adjust step size based on zoom
            
            const currentPos = this.elementManager.selectedElement.position();
            let newPos = { ...currentPos };
            
            switch (e.key) {
                case 'ArrowUp':
                    e.preventDefault();
                    newPos.y -= step;
                    break;
                case 'ArrowDown':
                    e.preventDefault();
                    newPos.y += step;
                    break;
                case 'ArrowLeft':
                    e.preventDefault();
                    newPos.x -= step;
                    break;
                case 'ArrowRight':
                    e.preventDefault();
                    newPos.x += step;
                    break;
                default:
                    return;
            }
            
            // Apply new position
            this.elementManager.selectedElement.position(newPos);
            
            // REMOVE: this.elementManager.updateSelectionBorder(true);
            // Transformer should update its position automatically as it's attached to the node.
            this.elementManager.updatePropertiesPanel();
            this.showPositionFeedback(newPos);
            this.layer.batchDraw(); // Use batchDraw for better performance
            
            // Hide feedback after a delay
            setTimeout(() => this.hidePositionFeedback(), 1000);
        });
    }

    // Helper to check if a textarea is focused
    isEditingText() {
        return document.activeElement && document.activeElement.tagName === 'TEXTAREA';
    }

    updatePropertiesPanelPosition(position) {
        // Update position inputs in properties panel during drag
        const xInput = document.querySelector('.property-input[data-property="x"]');
        const yInput = document.querySelector('.property-input[data-property="y"]');
        
        if (xInput) {
            xInput.value = Math.round(position.x);
        }
        if (yInput) {
            yInput.value = Math.round(position.y);
        }
    }
}

export default ElementEventHandler;
