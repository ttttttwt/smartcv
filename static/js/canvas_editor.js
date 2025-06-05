class CanvasEditor {
    constructor(containerId, options = {}) {
        this.containerId = containerId;
        this.options = {
            width: options.width || 800,
            height: options.height || 1000,
            scale: options.scale || 1,
            minZoom: 0.1,
            maxZoom: 5,
            zoomStep: 0.1,
            ...options
        };
        this.stage = null;
        this.layer = null;
        this.currentZoom = 1;
        
        // Store initial state for proper reset
        this.initialState = {
            zoom: 1,
            position: { x: 0, y: 0 },
            centerPosition: null
        };
        
        // Initialize modular components
        this.elementFactory = null;
        this.elementManager = null;
        this.eventHandler = null;
        
        // Add debounce flag to prevent rapid successive calls
        this.isZooming = false;
        
        this.init();
        this.setupEventListeners();
    }
    
    init() {
        // Initialize Konva stage
        this.stage = new Konva.Stage({
            container: this.containerId,
            width: this.options.width,
            height: this.options.height,
            draggable: false // Stage dragging is handled by pan controls or middle mouse
        });
        
        // Create main layer
        this.layer = new Konva.Layer();
        this.stage.add(this.layer);
        
        // Store initial center position after stage is created
        this.calculateInitialCenterPosition(); // This sets this.initialState.position
        
        // Initialize modular components
        this.elementFactory = new ElementFactory();
        this.elementManager = new ElementManager(this.stage, this.layer);
        this.eventHandler = new ElementEventHandler(this.elementManager, this.stage, this.layer);
        
        // Add background
        // this.addBackground();
        
        // Setup stage events
        this.setupStageEvents();
        
        // Setup keyboard movement
        this.eventHandler.setupKeyboardMovement();
        
        console.log('Canvas Editor initialized');
    }

    calculateInitialCenterPosition() {
        // Calculate the initial center position based on container
        const container = this.stage.container(); // This is #canvas-stage div
        // const parentContainer = container.parentElement; // This is .canvas-container
        
        // console.log('Fitting canvas to screen:', parentContainer.offsetWidth, parentContainer.offsetHeight);
        // const parentRect = parentContainer.getBoundingClientRect();
  
        // this.initialState.centerPosition = { // This seems unused
        //     x: parentRect.width / 2,
        //     y: parentRect.height / 2
        // };
        
        // Since #canvas-stage div is centered by its parent grid,
        // Konva stage internal position (pan) should be (0,0)
        // for content to be at top-left of #canvas-stage.
        this.initialState.position = { x: 0, y: 0 };
        this.stage.position(this.initialState.position);

        // Set initial size of the #canvas-stage DOM element
        const canvasStageEl = this.stage.container();
        canvasStageEl.style.width = this.options.width + 'px';
        canvasStageEl.style.height = this.options.height + 'px';
        
        console.log('Initial canvas state calculated:', this.initialState);
    }
    
    setupStageEvents() {
        // Click on empty area to deselect
        this.stage.on('click tap', (e) => {
            if (e.target === this.stage || e.target.getClassName() === 'Rect') {
                this.elementManager.deselectElement();
            }
        });
        
        // Handle element selection
        this.stage.on('click tap', (e) => {
            if (e.target.hasName('cv-element')) {
                this.elementManager.selectElement(e.target);
            }
        });
    }
    
    setupEventListeners() {
        // Element creation buttons
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('element-btn')) {
                const elementType = e.target.dataset.type;
                this.createElement(elementType);
            }
        });
        
        // Property inputs
        document.addEventListener('input', (e) => {
            if (e.target.classList.contains('property-input')) {
                this.updateElementProperty(e.target);
            }
        });
        
        // Color inputs
        document.addEventListener('change', (e) => {
            if (e.target.type === 'color') {
                this.updateElementProperty(e.target);
            }
        });
        
        // Font controls
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('font-btn')) {
                this.eventHandler.handleFontControl(e.target);
            }
        });

        // AI Hint button toggle
        document.addEventListener('click', async (e) => {
            if (e.target.dataset.action === 'toggle-ai-prompt') {
                const button = e.target; // This is the toggle button
                const promptContainer = button.nextElementSibling;
                if (promptContainer && promptContainer.classList.contains('ai-prompt-container')) {
                    promptContainer.classList.toggle('hidden');

                    if (!promptContainer.classList.contains('hidden')) {
                        // Store a reference to the input field this AI prompt is for.
                        // Assuming the input field is the previous sibling of the toggle button.
                        // Adjust if your HTML structure is different.
                        let associatedInput = button.previousElementSibling;
                        // Check if the previous sibling is a label, then the input is before the label
                        if (associatedInput && associatedInput.tagName === 'LABEL') {
                            associatedInput = associatedInput.previousElementSibling;
                        }
                        
                        if (associatedInput && (associatedInput.classList.contains('property-input') || associatedInput.matches('textarea') || associatedInput.matches('input'))) {
                            promptContainer._associatedInput = associatedInput;
                        } else {
                            console.warn('Could not find associated input for AI prompt toggle. Button:', button, 'Attempted input:', associatedInput);
                            promptContainer._associatedInput = null; // Explicitly set to null
                        }
                    }
                }
            } else if (e.target.dataset.action === 'submit-ai-prompt') {
                const submitButton = e.target;
                const promptContainer = submitButton.parentElement;
                const promptTextarea = promptContainer.querySelector('.ai-prompt-textarea');
                const relatedPropertyInput = promptContainer._associatedInput; // Retrieve stored reference

                if (promptTextarea) {
                    const user_message = promptTextarea.value;
                    if (user_message.trim() === "") {
                        if (typeof showNotification === 'function') {
                            showNotification("Vui lòng nhập yêu cầu cho AI.", "error");
                        } else {
                            alert("Vui lòng nhập yêu cầu cho AI.");
                        }
                        return;
                    }

                    if (!this.elementManager || !this.elementManager.selectedElement) {
                        if (typeof showNotification === 'function') {
                            showNotification("Vui lòng chọn một element để nhận gợi ý AI.", "error");
                        } else {
                            alert("Vui lòng chọn một element để nhận gợi ý AI.");
                        }
                        return;
                    }

                    const selectedKonvaElement = this.elementManager.selectedElement;
                    const elementData = this.elementManager.elements.get(selectedKonvaElement.id());
                    
                    if (!elementData) {
                         if (typeof showNotification === 'function') {
                            showNotification("Không tìm thấy dữ liệu element đã chọn.", "error");
                        } else {
                            alert("Không tìm thấy dữ liệu element đã chọn.");
                        }
                        return;
                    }

                    const elementType = elementData.type;
                    let elementContent = "";

                    if (relatedPropertyInput && typeof relatedPropertyInput.value !== 'undefined') {
                        elementContent = relatedPropertyInput.value;
                    } else if (['text', 'heading', 'paragraph', 'list'].includes(elementType)) {
                        elementContent = selectedKonvaElement.text ? selectedKonvaElement.text() : (elementData.properties.text || '');
                    } else {
                        // For non-textual elements, or if text() is not available,
                        // provide a generic context. The AI will primarily use user_message and element_type.
                        elementContent = `Context: Element of type '${elementType}'`; 
                    }
                    
                    const payload = {
                        user_message: user_message,
                        context: {
                            type: elementType,
                            content: elementContent
                        }
                    };

                    console.log('Sending AI Prompt:', payload);
                    submitButton.textContent = 'Đang xử lý...';
                    submitButton.disabled = true;

                    try {
                        const response = await fetch('/cv/api/ai-hint', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                                'X-CSRFToken': getCsrfToken() // Ensure getCsrfToken() is implemented
                            },
                            body: JSON.stringify(payload)
                        });

                        const result = await response.json();

                        if (result.success) {
                            this.displayAISuggestion(result.suggestion, relatedPropertyInput);
                        } else {
                            if (typeof showNotification === 'function') {
                                showNotification(result.error || 'Lỗi khi lấy gợi ý AI.', 'error');
                            } else {
                                alert(result.error || 'Lỗi khi lấy gợi ý AI.');
                            }
                        }
                    } catch (error) {
                        console.error('AI Prompt Error:', error);
                        if (typeof showNotification === 'function') {
                            showNotification('Lỗi kết nối khi gửi yêu cầu AI.', 'error');
                        } else {
                            alert('Lỗi kết nối khi gửi yêu cầu AI.');
                        }
                    } finally {
                        submitButton.textContent = 'Gửi';
                        submitButton.disabled = false;
                    }
                }
            }
        });

        // Handle Enter key for list item text in properties panel
        document.addEventListener('keydown', (e) => {
            if (e.target.matches('textarea.list-text-property-input') && e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                const textarea = e.target;
                
                if (this.elementManager && this.elementManager.selectedElement) {
                    const elementData = this.elementManager.elements.get(this.elementManager.selectedElement.id());
                    if (elementData && elementData.type === 'list') {
                        const bulletStyle = elementData.properties.bulletStyle || '•';
                        const start = textarea.selectionStart;
                        const end = textarea.selectionEnd;
                        let textToInsert = '\n';

                        if (bulletStyle === '1.') {
                            const currentLines = textarea.value.substring(0, start).split('\n');
                             // Find the number of the last actual list item before cursor
                            let lastNumber = 0;
                            for (let i = currentLines.length - 1; i >= 0; i--) {
                                const match = currentLines[i].match(/^(\d+)\.\s*/);
                                if (match) {
                                    lastNumber = parseInt(match[1], 10);
                                    break;
                                }
                            }
                            textToInsert += `${lastNumber + 1}. `;
                        } else {
                            textToInsert += `${bulletStyle} `;
                        }
                        
                        textarea.value = textarea.value.substring(0, start) + textToInsert + textarea.value.substring(end);
                        textarea.selectionStart = textarea.selectionEnd = start + textToInsert.length;
                        
                        // Manually trigger an 'input' event so that ElementManager.updateElementProperty picks up the change
                        const inputEvent = new Event('input', { bubbles: true, cancelable: true });
                        textarea.dispatchEvent(inputEvent);
                        return; // Prevent default handling if it was a list
                    }
                }
                
                // Fallback for non-list or if elementManager is not set (should not happen)
                // This part might be redundant if the outer `if` for list handles it.
                // Kept for safety, but the specific list logic should take precedence.
                const start = textarea.selectionStart;
                const end = textarea.selectionEnd;
                const textToInsert = '\n• '; // Default if not a list or style not found
                
                textarea.value = textarea.value.substring(0, start) + textToInsert + textarea.value.substring(end);
                textarea.selectionStart = textarea.selectionEnd = start + textToInsert.length;
                
                const inputEvent = new Event('input', { bubbles: true, cancelable: true });
                textarea.dispatchEvent(inputEvent);
            }
        });
    }
    
    createElement(type) {
        const element = this.elementFactory.createElement(type);
        
        if (element) {
            const properties = this.elementFactory.getDefaultProperties(type);
            this.eventHandler.setupElementEvents(element);
            this.elementManager.addElement(element, type, properties);
            
            // Update UI and hide empty state
            this.updateCanvasState();
        }
    }

    updateElementProperty(input) {
        if (!this.elementManager.selectedElement) return;
        
        const property = input.dataset.property;
        const value = input.type === 'number' ? parseFloat(input.value) : input.value;
        
        this.elementManager.updateElementProperty(this.elementManager.selectedElement, property, value);
        
        // Update selection border immediately for position changes
        if (property === 'x' || property === 'y') {
            this.elementManager.updateSelectionBorder(true);
        }
    }

    deleteSelectedElement() {
        if (!this.elementManager.selectedElement) return;
        
        const elementId = this.elementManager.selectedElement.id();
        this.elementManager.removeElement(elementId);
        this.updateCanvasState(); // Ensure state is updated after deletion
    }

    copyElement() {
        this.elementManager.copyElement();
    }

    pasteElement() {
        const copiedData = this.elementManager.pasteElement();
        if (copiedData) {
            const element = this.elementFactory.createElement(copiedData.type, 
                { x: copiedData.attrs.x, y: copiedData.attrs.y });
            
            if (element) {
                element.setAttrs(copiedData.attrs);
                this.eventHandler.setupElementEvents(element);
                this.elementManager.addElement(element, copiedData.type, copiedData.properties);
                this.updateCanvasState();
            }
        }
    }

    zoomIn() {
        // Add debounce to prevent rapid successive calls
        if (this.isZooming) return;
        this.isZooming = true;
        
        const currentScale = this.stage.scaleX();
        const newScale = Math.min(currentScale + this.options.zoomStep, this.options.maxZoom);
        this.setZoom(newScale);
        console.log('Zoom in executed');
        
        // Reset debounce flag after a short delay
        setTimeout(() => {
            this.isZooming = false;
        }, 100);
    }
    
    zoomOut() {
        // Add debounce to prevent rapid successive calls
        if (this.isZooming) return;
        this.isZooming = true;
        
        const currentScale = this.stage.scaleX();
        const newScale = Math.max(currentScale - this.options.zoomStep, this.options.minZoom);
        this.setZoom(newScale);
        console.log('Zoom out executed');
        
        // Reset debounce flag after a short delay
        setTimeout(() => {
            this.isZooming = false;
        }, 100);
    }

    resetZoom() {
        this.setZoomToInitialState();
    }
    
    setZoomToInitialState() {
        // Restore to exact initial state
        this.stage.scale({ x: 1, y: 1 });
        this.stage.position(this.initialState.position); // Reset Konva stage pan to {x:0, y:0}
        this.stage.draw();
        
        // Update current zoom
        this.currentZoom = 1;
        
        // Update UI
        this.updateZoomDisplay(1);

        // Update #canvas-stage DOM element size
        const canvasStageEl = this.stage.container();
        canvasStageEl.style.width = this.options.width + 'px';
        canvasStageEl.style.height = this.options.height + 'px';
        
        // REMOVE: Update selection border with reset zoom level
        // if (this.elementManager?.selectedElement) {
        //     this.elementManager.updateSelectionBorder(false);
        // }
        
        // Trigger scale change event
        this.stage.fire('scaleChange', { scale: 1 });
        
        console.log('Canvas reset to initial state');
    }
    
    setZoom(scale) {
        // Clamp scale to allowed range
        scale = Math.max(this.options.minZoom, Math.min(this.options.maxZoom, scale));
        
        console.log('Setting zoom to:', scale);
        // Apply new scale to Konva stage
        this.stage.scale({ x: scale, y: scale });
        
        // Update current zoom
        this.currentZoom = scale;
        
        // Update UI
        this.updateZoomDisplay(scale);

        // Update #canvas-stage DOM element size
        const canvasStageEl = this.stage.container();
        canvasStageEl.style.width = (this.options.width * scale) + 'px';
        canvasStageEl.style.height = (this.options.height * scale) + 'px';
        
        // REMOVE: Update selection border with new zoom level - this is crucial for fixing the selection issue
        // if (this.elementManager?.selectedElement) {
        //     this.elementManager.updateSelectionBorder(false); // Use smooth animation for zoom changes
        // }
        
        // Trigger scale change event
        this.stage.fire('scaleChange', { scale: scale });
        
        console.log('Zoom set to:', Math.round(scale * 100) + '%');
    }

    updateZoomDisplay(scale) {
        const zoomLevel = document.querySelector('.zoom-level');
        if (zoomLevel) {
            zoomLevel.textContent = Math.round(scale * 100) + '%';
        }
    }

    fitToScreen() {
        const parentContainer = this.stage.container().parentElement; // This is .canvas-container
        const containerWidth = parentContainer.offsetWidth;
        const containerHeight = parentContainer.offsetHeight;
        console.log('Fitting canvas to screen:', containerWidth, containerHeight);
        
        // Calculate scale to fit canvas in container with padding
        const scaleX = (containerWidth * 0.9) / this.options.width;
        const scaleY = (containerHeight * 0.9) / this.options.height;
        const scale = Math.min(scaleX, scaleY);
        
        // Center the Konva stage content.
        // Since #canvas-stage div is centered by parent grid,
        // Konva stage internal position (pan) should be {x:0, y:0}.
        this.stage.position(this.initialState.position); 
        this.stage.scale({ x: scale, y: scale });
        this.stage.draw();
        
        // Update current zoom
        this.currentZoom = scale;
        
        // Update UI
        this.updateZoomDisplay(scale);

        // Update #canvas-stage DOM element size
        const canvasStageEl = this.stage.container();
        canvasStageEl.style.width = (this.options.width * scale) + 'px';
        canvasStageEl.style.height = (this.options.height * scale) + 'px';
        
        // REMOVE: Update selection border if element is selected
        // if (this.elementManager?.selectedElement) {
        //     this.elementManager.updateSelectionBorder(true);
        // }
        
        // Trigger scale change event
        this.stage.fire('scaleChange', { scale: scale });
        
        console.log('Canvas fitted to screen with scale:', scale);
    }

    
    getCurrentZoom() {
        return this.currentZoom;
    }

    // Grid functionality
    enableGridSnapping(enabled = true) {
        this.gridSnapping = enabled;
        this.gridSize = 20; // Default grid size
    }

    snapToGrid(value) {
        if (!this.gridSnapping) return value;
        return Math.round(value / this.gridSize) * this.gridSize;
    }


    // Add method to load template data and make elements interactive
    loadTemplateData(templateData) {
        try {
            console.log('Loading template data into canvas:', templateData);
            
            // Clear existing content
            this.layer.destroyChildren(); // This destroys all children, including the old transformer
            this.elementManager.elements.clear();
            
            // CRITICAL: Re-initialize the transformer in ElementManager
            // This creates a new transformer and adds it to the current layer
            if (this.elementManager) {
                this.elementManager.initTransformer();
            }
            
            // Check structure and load accordingly
            if (templateData.children && Array.isArray(templateData.children)) {
                this.loadKonvaStageData(templateData);
            } else if (templateData.elements && Array.isArray(templateData.elements)) {
                this.loadCustomElementsData(templateData);
            } else if (templateData.attrs || templateData.className) {
                this.loadSingleNodeData(templateData);
            }
            
            this.layer.draw();
            this.updateCanvasState();
            
        } catch (error) {
            console.error('Error loading template data:', error);
        }
    }

    loadKonvaStageData(stageData) {
        if (!stageData.children) return;
        
        stageData.children.forEach(layerData => {
            if (layerData.children && Array.isArray(layerData.children)) {
                layerData.children.forEach(nodeData => {
                    this.createInteractiveNodeFromData(nodeData);
                });
            }
        });
    }

    loadCustomElementsData(data) {
        if (!data.elements) return;
        
        data.elements.forEach(elementData => {
            this.createInteractiveElementFromCustomData(elementData);
        });
    }

    loadSingleNodeData(nodeData) {
        this.createInteractiveNodeFromData(nodeData);
    }

    createInteractiveNodeFromData(nodeData) {
        try {
            // Use Konva.Node.create to recreate the node
            const node = Konva.Node.create(nodeData);
            
            if (node) {
                // Make sure the node is draggable and has proper name
                node.setAttrs({
                    draggable: true,
                    name: 'cv-element'
                });
                
                // Add the node to canvas layer
                this.layer.add(node);
                
                // Setup event handlers for interaction
                this.eventHandler.setupElementEvents(node);
                
                // Add to element manager
                const elementType = this.getElementTypeFromNode(node);
                const properties = this.extractPropertiesFromNode(node);
                this.elementManager.addElement(node, elementType, properties);
                
                console.log('Created interactive node:', node.getClassName(), node.getAttrs());
            }
        } catch (error) {
            console.error('Error creating interactive node from data:', error, nodeData);
        }
    }

    createInteractiveElementFromCustomData(elementData) {
        try {
            if (!elementData.type || !elementData.attrs) {
                console.warn('Invalid element data:', elementData);
                return;
            }
            
            // Create element using factory
            const element = this.elementFactory.createElement(
                elementData.type,
                { x: elementData.attrs.x || 0, y: elementData.attrs.y || 0 }
            );
            
            if (element) {
                // Apply all attributes
                element.setAttrs({
                    ...elementData.attrs,
                    draggable: true,
                    name: 'cv-element'
                });
                
                // Setup events
                this.eventHandler.setupElementEvents(element);
                
                // Add to manager
                this.elementManager.addElement(
                    element, 
                    elementData.type, 
                    elementData.properties || {}
                );
                
                console.log('Created interactive custom element:', elementData.type, elementData.attrs);
            }
        } catch (error) {
            console.error('Error creating interactive custom element:', error, elementData);
        }
    }

    // Helper function to determine element type from Konva node
    getElementTypeFromNode(node) {
        const className = node.getClassName();
        const name = node.name(); // e.g., 'cv-element text-element'
        
        // Map Konva class names to our element types
        // More specific checks based on name if available
        if (name && name.includes('heading-element')) return 'heading';
        if (name && name.includes('paragraph-element')) return 'paragraph';
        if (name && name.includes('list-element')) return 'list';
        if (name && name.includes('text-element')) return 'text'; // Generic text
        if (name && name.includes('image-element') && className === 'Group') return 'image';
        if (name && name.includes('avatar-element') && className === 'Group') return 'avatar';
        if (name && name.includes('circle-element') && className === 'Circle') return 'circle';
        if (name && name.includes('line-element') && className === 'Line') return 'line';
        if (name && name.includes('icon-element') && className === 'Group') return 'icon';
        if (name && name.includes('progress-bar-element') && className === 'Group') return 'progress-bar';
        if (name && name.includes('rating-element') && className === 'Group') return 'rating';


        switch (className) {
            case 'Text':
                // Fallback for generic text if specific name isn't set
                return 'text'; 
            case 'Rect':
                return 'rectangle';
            case 'Circle':
                return 'circle'; // Fallback for generic circle if name isn't set
            // case 'Image': // This would be for actual Konva.Image, our placeholder is a Group
            //     return 'image';
            case 'Line':
                return 'line';
            case 'Group':
                // Could be a generic group or our image placeholder
                // The specific check for 'image-element' above handles image groups.
                return 'group'; // Fallback for other groups
            default:
                return 'text'; // fallback
        }
    }

    // Extract properties from Konva node
    extractPropertiesFromNode(node) {
        const attrs = node.getAttrs();
        return {
            x: attrs.x || 0,
            y: attrs.y || 0,
            width: attrs.width || 100,
            height: attrs.height || 50,
            fill: attrs.fill || '#000000',
            fontSize: attrs.fontSize || 16,
            fontFamily: attrs.fontFamily || 'Arial',
            text: attrs.text || '',
            ...attrs
        };
    }

    undo() {
        console.log('Undo not implemented yet');
    }

    redo() {
        console.log('Redo not implemented yet');
    }

    setPreviewMode(isPreview) {
        console.log('Preview mode:', isPreview);
    }

    updateCanvasState() {
        const elementCount = this.elementManager.elements.size;
        const canvasEmpty = document.getElementById('canvas-empty');
        const canvasLoading = document.getElementById('canvas-loading');
        const elementCountDisplay = document.getElementById('element-count');
        
        // Update element count display
        if (elementCountDisplay) {
            elementCountDisplay.textContent = elementCount;
        }
        
        // Show/hide empty state based on element count
        if (elementCount === 0) {
            // Show empty state
            if (canvasEmpty) {
                canvasEmpty.classList.remove('hidden');
            }
            if (canvasLoading) {
                canvasLoading.classList.add('hidden');
            }
        } else {
            // Hide empty state when elements exist
            if (canvasEmpty) {
                canvasEmpty.classList.add('hidden');
            }
            if (canvasLoading) {
                canvasLoading.classList.add('hidden');
            }
        }
        
        // Update last saved status
        const lastSavedDisplay = document.getElementById('last-saved');
        if (lastSavedDisplay) {
            lastSavedDisplay.textContent = 'chưa lưu';
        }
        
        console.log('Canvas state updated - Elements:', elementCount);
    }

    // Add method for updating canvas title programmatically
    updateCanvasTitle(title) {
        const titleElement = document.querySelector('.canvas-title');
        if (titleElement) {
            titleElement.textContent = title || 'CV Mới';
        }
    }
    
    displayAISuggestion(suggestionText, targetInputElement) {
        const existingPopup = document.getElementById('ai-suggestion-popup');
        if (existingPopup) {
            existingPopup.remove();
        }

        const popup = document.createElement('div');
        popup.id = 'ai-suggestion-popup';
        popup.style.cssText = `
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background-color: white;
            border: 1px solid #ccc;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            padding: 20px;
            z-index: 1001; /* Ensure it's above other modals if any */
            border-radius: 8px;
            max-width: 450px;
            width: 90%;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        `;

        const title = document.createElement('h4');
        title.textContent = 'Gợi ý từ AI';
        title.style.marginTop = '0';
        title.style.marginBottom = '15px';
        title.style.fontSize = '16px';
        title.style.fontWeight = '600';
        title.style.color = '#333';

        const suggestionContent = document.createElement('div'); // Use div for better scroll
        suggestionContent.style.maxHeight = '200px';
        suggestionContent.style.overflowY = 'auto';
        suggestionContent.style.marginBottom = '20px';
        suggestionContent.style.paddingRight = '10px'; // For scrollbar spacing
        suggestionContent.style.fontSize = '14px';
        suggestionContent.style.lineHeight = '1.6';
        suggestionContent.style.color = '#555';
        suggestionContent.style.whiteSpace = 'pre-wrap';
        suggestionContent.textContent = suggestionText;


        const actionsDiv = document.createElement('div');
        actionsDiv.style.textAlign = 'right';
        actionsDiv.style.marginTop = '10px';

        const useButton = document.createElement('button');
        useButton.textContent = 'Sử dụng';
        useButton.style.cssText = `
            padding: 8px 16px;
            background-color: #206bc4;
            color: white;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            margin-right: 10px;
            font-size: 14px;
            font-weight: 500;
        `;
        useButton.onmouseover = () => useButton.style.backgroundColor = '#1c63b8';
        useButton.onmouseout = () => useButton.style.backgroundColor = '#206bc4';

        useButton.onclick = () => {
            if (targetInputElement && typeof targetInputElement.value !== 'undefined') {
                targetInputElement.value = suggestionText;
                // Trigger input event for property panel to update element
                const inputEvent = new Event('input', { bubbles: true, cancelable: true });
                targetInputElement.dispatchEvent(inputEvent);
                if (typeof showNotification === 'function') {
                    showNotification('Đã áp dụng gợi ý.', 'success');
                }
            } else {
                console.warn('AI Suggestion: Target input element not found or invalid.');
                if (typeof showNotification === 'function') {
                    showNotification('Không tìm thấy trường để áp dụng gợi ý. Vui lòng sao chép thủ công.', 'warning');
                }
                // Optionally, copy to clipboard:
                // navigator.clipboard.writeText(suggestionText).then(() => {
                //     if (typeof showNotification === 'function') {
                //         showNotification('Gợi ý đã được sao chép vào clipboard.', 'info');
                //     }
                // }).catch(err => console.error('Failed to copy to clipboard:', err));
            }
            popup.remove();
        };

        const closeButton = document.createElement('button');
        closeButton.textContent = 'Đóng';
        closeButton.style.cssText = `
            padding: 8px 16px;
            background-color: #f1f3f4;
            color: #333;
            border: 1px solid #d0d7de;
            border-radius: 6px;
            cursor: pointer;
            font-size: 14px;
            font-weight: 500;
        `;
        closeButton.onmouseover = () => closeButton.style.backgroundColor = '#e1e5e9';
        closeButton.onmouseout = () => closeButton.style.backgroundColor = '#f1f3f4';

        closeButton.onclick = () => {
            popup.remove();
        };

        actionsDiv.appendChild(useButton);
        actionsDiv.appendChild(closeButton);

        popup.appendChild(title);
        popup.appendChild(suggestionContent);
        popup.appendChild(actionsDiv);

        document.body.appendChild(popup);
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = CanvasEditor;
}


// Placeholder for CSRF token retrieval.
// Ensure this function is properly implemented in your project,
// e.g., by reading from a meta tag or a global variable set by the server-side template.
function getCsrfToken() {
    // Try multiple common CSRF token sources
    
    // 1. Check for global CSRF_TOKEN variable
    if (typeof CSRF_TOKEN !== 'undefined') {
        return CSRF_TOKEN;
    }
    
    // 2. Check for meta tag with name="csrf-token"
    const csrfMeta = document.querySelector('meta[name="csrf-token"]');
    if (csrfMeta) {
        return csrfMeta.getAttribute('content');
    }
    
    // 3. Check for meta tag with name="_csrf_token" (Flask-WTF default)
    const flaskCsrfMeta = document.querySelector('meta[name="_csrf_token"]');
    if (flaskCsrfMeta) {
        return flaskCsrfMeta.getAttribute('content');
    }
    
    // 4. Try to get from a hidden input field (common in forms)
    const csrfInput = document.querySelector('input[name="csrf_token"]');
    if (csrfInput) {
        return csrfInput.value;
    }
    
    // 5. Try to get from session storage or local storage
    if (typeof Storage !== 'undefined') {
        const sessionToken = sessionStorage.getItem('csrf_token');
        if (sessionToken) {
            return sessionToken;
        }
        
        const localToken = localStorage.getItem('csrf_token');
        if (localToken) {
            return localToken;
        }
    }
    
    // 6. For Flask applications without CSRF protection, return empty string
    console.warn('CSRF token not found. If your Flask app uses CSRF protection, please ensure the token is available via meta tag or global variable.');
    return "";
}


// Sample template loading functions
function loadModernTemplate() {
    canvasEditor.createElement('heading');
    canvasEditor.createElement('text');
    canvasEditor.createElement('avatar');
    canvasEditor.createElement('text');
    canvasEditor.createElement('text');
    canvasEditor.createElement('heading');
    canvasEditor.createElement('rectangle');
    canvasEditor.createElement('circle');
    canvasEditor.createElement('progress-bar');
    canvasEditor.createElement('rating');
}

function loadCreativeTemplate() {
    canvasEditor.createElement('rectangle');
    canvasEditor.createElement('heading');
    canvasEditor.createElement('icon');
    canvasEditor.createElement('progress-bar');
    canvasEditor.createElement('rating');
}
