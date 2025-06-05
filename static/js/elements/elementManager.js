class ElementManager {
    constructor(stage, layer) {
        this.stage = stage;
        this.layer = layer;
        this.selectedElement = null;
        this.elements = new Map();
        this.copiedElement = null;
        this.history = [];
        this.historyIndex = -1;

        // Initialize Konva Transformer
        this.initTransformer();
    }

    initTransformer() {
        // If an old transformer exists, detach from nodes and destroy it
        if (this.transformer) {
            this.transformer.nodes([]);
            this.transformer.destroy();
        }

        this.transformer = new Konva.Transformer({
            keepRatio: false, // Allow independent width/height resizing
            rotateEnabled: false, // Disable rotation for now
            borderDash: [8, 4],
            borderStroke: '#667eea',
            anchorStroke: '#667eea',
            anchorFill: '#ffffff',
            anchorSize: 10,
            // Consider making anchorSize responsive to zoom later if needed
        });
        if (this.layer) { // Ensure layer exists before adding
            this.layer.add(this.transformer);
        }
    }

    addElement(element, type, properties) {
        // Ensure element has proper configuration
        element.setAttrs({
            draggable: true,
            name: 'cv-element'
        });
        
        // Store in elements map
        this.elements.set(element.id(), {
            konvaObject: element,
            type: type,
            properties: { ...properties } // Store a copy of properties
        });

        // Add to layer only if not already added
        if (!element.getParent()) {
            this.layer.add(element);
        }
        
        this.layer.draw();
        this.selectElement(element);
        
        console.log('Element added to manager:', element.id(), type);
        
        // Notify canvas editor to update state if available
        if (window.canvasEditor && typeof window.canvasEditor.updateCanvasState === 'function') {
            window.canvasEditor.updateCanvasState();
        }
    }

    removeElement(elementId) {
        const element = this.elements.get(elementId);
        if (element) {
            if (this.selectedElement && this.selectedElement.id() === elementId) {
                this.deselectElement(); // Deselect before destroying
            }
            element.konvaObject.destroy();
            this.elements.delete(elementId);
            
            this.layer.draw();
            
            // Notify canvas editor to update state if available
            if (window.canvasEditor && typeof window.canvasEditor.updateCanvasState === 'function') {
                window.canvasEditor.updateCanvasState();
            }
        }
    }

    selectElement(element) {
        this.deselectElement();
        
        this.selectedElement = element;
        
        // Attach transformer to the selected element
        if (this.transformer) { // Check if transformer exists
            this.transformer.nodes([element]);
            this.transformer.moveToTop(); // Ensure transformer is on top
        }
        
        // Move element to top for better visibility if needed (transformer might handle this)
        element.moveToTop();

        // Configure transformer based on element type
        if (element.getClassName() === 'Line') {
            this.transformer.enabledAnchors(['middle-left', 'middle-right', 'top-left', 'top-right', 'bottom-left', 'bottom-right']);
            this.transformer.keepRatio(false); // Allow changing length independently of theoretical "height"
            // For lines, rotation is usually around the center or ends. Default is fine.
        } else {
            this.transformer.enabledAnchors(null); // null enables all anchors
            // Reset keepRatio if it was changed for other types, or set as needed
            // Example: this.transformer.keepRatio(false); 
        }
        
        this.layer.draw(); // Or use batchDraw for performance
        this.updatePropertiesPanel();
        this.showElementInfo(element);
        
        console.log('Element selected:', element.id());
    }

    deselectElement() {
        if (this.selectedElement) {
            // Detach transformer
            if (this.transformer) { // Check if transformer exists
                this.transformer.nodes([]);
            }
            
            this.selectedElement = null;
            this.layer.draw(); // Or use batchDraw
            this.clearPropertiesPanel();
        }
    }

    copyElement() {
        if (!this.selectedElement) return;
        
        const elementData = this.elements.get(this.selectedElement.id());
        if (elementData) {
            this.copiedElement = {
                type: elementData.type,
                attrs: this.selectedElement.getAttrs(),
                properties: { ...elementData.properties }
            };
        }
    }

    pasteElement() {
        if (!this.copiedElement) return null;
        
        const position = {
            x: this.copiedElement.attrs.x + 20,
            y: this.copiedElement.attrs.y + 20
        };
        
        return {
            type: this.copiedElement.type,
            attrs: { ...this.copiedElement.attrs, x: position.x, y: position.y },
            properties: { ...this.copiedElement.properties }
        };
    }

    updateElementProperty(element, property, value) {
        if (element && property && value !== undefined) {
            const elementData = this.elements.get(element.id());
            const type = elementData?.type;

            if (type === 'list') {
                if (property === 'bulletStyle') {
                    elementData.properties.bulletStyle = value;
                    this.reformatListText(element, value);
                    // Update properties panel to reflect change if needed (e.g. select dropdown)
                    this.updatePropertiesPanel(); // Re-render to show new selection
                } else if (property === 'text') {
                    // Text from textarea is raw, reformat it with current bullet style
                    this.reformatListText(element, elementData.properties.bulletStyle, value);
                } else {
                    this.applyStandardProperty(element, property, value);
                }
            } else if (type === 'image') {
                const group = element; // The image element is a group
                if (property === 'placeholderText') {
                    const textNode = group.findOne('.image-placeholder-text');
                    if (textNode) {
                        textNode.text(value);
                        // Recenter text if its width changes
                        textNode.offsetX(textNode.width() / 2);
                        textNode.offsetY(textNode.height() / 2);
                    }
                } else if (property === 'placeholderFill') {
                    const rectNode = group.findOne('.image-placeholder-rect');
                    if (rectNode) {
                        rectNode.fill(value);
                    }
                } else {
                    // Handle common properties like x, y, width, height for the group
                    this.applyStandardProperty(element, property, value);
                    // If radius is changed for avatar, update group width/height and circle radius
                    // THIS LOGIC IS MOVED TO THE 'avatar' BLOCK
                }
            } else if (type === 'avatar') { // Dedicated block for avatar properties
                const group = element; // Avatar is a group
                if (property === 'radius') {
                    const newRadius = parseFloat(value);
                    if (!isNaN(newRadius) && newRadius > 0) {
                        group.width(newRadius * 2);
                        group.height(newRadius * 2);
                        const circleNode = group.findOne('.avatar-placeholder-circle');
                        if (circleNode) {
                            circleNode.radius(newRadius);
                            // Update circle position to center of new group size
                            circleNode.x(newRadius);
                            circleNode.y(newRadius);
                            
                            // Adjust placeholder text position and size
                            const textNode = group.findOne('.avatar-placeholder-text');
                            if (textNode) {
                                // Calculate new font size based on radius
                                const newFontSize = Math.max(10, newRadius / 4);
                                textNode.fontSize(newFontSize);
                                
                                // Position text at center of circle
                                textNode.x(newRadius);
                                textNode.y(newRadius);
                                
                                // Re-center text after font size change
                                textNode.offsetX(textNode.width() / 2);
                                textNode.offsetY(textNode.height() / 2);
                            }
                        }
                        // Update stored properties
                        elementData.properties.radius = newRadius;
                    }
                } else if (property === 'placeholderText') {
                    const textNode = group.findOne('.avatar-placeholder-text');
                    if (textNode) {
                        textNode.text(value);
                        // Get current radius for proper positioning
                        const circleNode = group.findOne('.avatar-placeholder-circle');
                        const currentRadius = circleNode ? circleNode.radius() : parseFloat(group.width()) / 2;
                        
                        // Position at center and recenter based on new text dimensions
                        textNode.x(currentRadius);
                        textNode.y(currentRadius);
                        textNode.offsetX(textNode.width() / 2);
                        textNode.offsetY(textNode.height() / 2);
                    }
                } else if (property === 'placeholderFill') { // Fill for the avatar's circle
                    const circleNode = group.findOne('.avatar-placeholder-circle');
                    if (circleNode) {
                        circleNode.fill(value);
                    }
                } else if (property === 'stroke') { // Stroke for the avatar's circle border
                    const circleNode = group.findOne('.avatar-placeholder-circle');
                    if (circleNode) {
                        circleNode.stroke(value);
                    }
                } else {
                    // Handle common properties like x, y, scaleX, scaleY for the group
                    // Avoid direct width/height setting as it's controlled by radius for avatars
                    if (property === 'x' || property === 'y' || property === 'scaleX' || property === 'scaleY') {
                        this.applyStandardProperty(element, property, value);
                    }
                }
            } else if (type === 'line') {
                if (property === 'stroke' || property === 'strokeWidth') {
                    this.applyStandardProperty(element, property, value);
                    if (property === 'strokeWidth') {
                        elementData.properties.strokeWidth = parseFloat(value);
                    } else {
                        elementData.properties.stroke = value;
                    }
                } else if (property === 'lineStyle') {
                    elementData.properties.lineStyle = value;
                    let dashArray = [];
                    if (value === 'dashed') {
                        dashArray = [10, 5];
                    } else if (value === 'dotted') {
                        dashArray = [2, 5];
                    }
                    element.dash(dashArray);
                }
            } else if (type === 'icon') {
                const group = element;
                if (property === 'iconType') {
                    const textNode = group.findOne('.icon-text');
                    if (textNode) {
                        textNode.text(value);
                        textNode.offsetX(textNode.width() / 2);
                        textNode.offsetY(textNode.height() / 2);
                    }
                } else if (property === 'iconSize') {
                    const textNode = group.findOne('.icon-text');
                    if (textNode) {
                        textNode.fontSize(parseFloat(value));
                        textNode.offsetX(textNode.width() / 2);
                        textNode.offsetY(textNode.height() / 2);
                    }
                } else if (property === 'iconColor') {
                    const textNode = group.findOne('.icon-text');
                    if (textNode) {
                        textNode.fill(value);
                    }
                } else {
                    this.applyStandardProperty(element, property, value);
                }
            } else if (type === 'progress-bar') {
                const group = element;
                if (property === 'progressValue') {
                    const backgroundNode = group.findOne('.progress-background');
                    const fillNode = group.findOne('.progress-fill');
                    const textNode = group.findOne('.progress-text');
                    
                    if (backgroundNode && fillNode && textNode) {
                        const newWidth = backgroundNode.width() * (parseFloat(value) / 100);
                        fillNode.width(newWidth);
                        textNode.text(`${value}%`);
                        textNode.offsetX(textNode.width() / 2);
                    }
                } else if (property === 'fillColor') {
                    const fillNode = group.findOne('.progress-fill');
                    if (fillNode) {
                        fillNode.fill(value);
                    }
                } else if (property === 'backgroundColor') {
                    const backgroundNode = group.findOne('.progress-background');
                    if (backgroundNode) {
                        backgroundNode.fill(value);
                    }
                } else if (property === 'textColor') {
                    const textNode = group.findOne('.progress-text');
                    if (textNode) {
                        textNode.fill(value);
                    }
                } else {
                    this.applyStandardProperty(element, property, value);
                }
            } else if (type === 'rating') {
                const group = element;
                if (property === 'ratingValue') {
                    const stars = group.find('Text');
                    const rating = parseInt(value);
                    stars.forEach((star, index) => {
                        star.text(index < rating ? '★' : '☆');
                    });
                } else if (property === 'totalStars') {
                    // This would require recreating the rating element
                    // For now, just update existing stars
                    console.log('Total stars change requires element recreation');
                } else if (property === 'filledColor') {
                    const stars = group.find('Text');
                    stars.forEach(star => {
                        if (star.text() === '★') {
                            star.fill(value);
                        }
                    });
                } else if (property === 'emptyColor') {
                    const stars = group.find('Text');
                    stars.forEach(star => {
                        if (star.text() === '☆') {
                            star.fill(value);
                        }
                    });
                } else {
                    this.applyStandardProperty(element, property, value);
                }
            } else {
                this.applyStandardProperty(element, property, value);
            }

            this.layer.draw();
        }
    }

    applyStandardProperty(element, property, value) {
        // Special handling for scale if transformer modifies it directly
        if (property === 'scaleX' || property === 'scaleY') {
             element[property](value);
        } else if (typeof element[property] === 'function') {
            element[property](value);
        } else {
            // Fallback for other attributes if needed
            const attrs = {};
            attrs[property] = value;
            element.setAttrs(attrs);
        }
    }


    reformatListText(element, bulletStyle, rawText = null) {
        const currentText = rawText !== null ? rawText : element.text();
        const lines = currentText.split('\n')
            .map(line => {
                // Remove existing common bullet prefixes more robustly
                let cleanedLine = line.trimStart();
                cleanedLine = cleanedLine.replace(/^[\•\-\*\+]|^\d+\.\s*/, '').trim();
                return cleanedLine;
            })
            .filter(line => line.length > 0); // Remove empty lines that might result from just bullets

        const formattedLines = lines.map((line, index) => {
            if (bulletStyle === '1.') {
                return `${index + 1}. ${line}`;
            }
            return `${bulletStyle} ${line}`;
        });

        element.text(formattedLines.join('\n'));
    }


    updatePropertiesPanel() {
        if (!this.selectedElement) return;
        
        const elementData = this.elements.get(this.selectedElement.id());
        if (!elementData) return;
        
        const propertiesContent = document.querySelector('.properties-content');
        if (!propertiesContent) return;
        
        propertiesContent.innerHTML = this.generatePropertiesHTML(elementData);
    }

    generateBasePropertiesHTML(element) {
        return `
            <div class="property-group">
                <label class="property-label">Vị trí</label>
                <div class="property-row">
                    <input type="number" class="property-input" data-property="x" value="${Math.round(element.x())}" placeholder="X">
                    <input type="number" class="property-input" data-property="y" value="${Math.round(element.y())}" placeholder="Y">
                </div>
            </div>
        `;
    }

    generateDimensionPropertiesHTML(element) {
        // Note: For Konva.Text, height is often auto-calculated. Setting it explicitly can lead to clipping or extra space.
        // Width is used for text wrapping.
        // The transformer will scale the node. We read the scaled width/height.
        const width = Math.round(element.width() * element.scaleX());
        const height = Math.round(element.height() * element.scaleY());
        return `
            <div class="property-group">
                <label class="property-label">Kích thước</label>
                <div class="property-row">
                    <input type="number" class="property-input" data-property="width" value="${width}" placeholder="Rộng">
                    <input type="number" class="property-input" data-property="height" value="${height}" placeholder="Cao">
                </div>
            </div>
            <div class="property-group">
                <label class="property-label">Tỷ lệ (Scale)</label>
                <div class="property-row">
                    <input type="number" step="0.1" class="property-input" data-property="scaleX" value="${element.scaleX().toFixed(2)}" placeholder="Scale X">
                    <input type="number" step="0.1" class="property-input" data-property="scaleY" value="${element.scaleY().toFixed(2)}" placeholder="Scale Y">
                </div>
            </div>
        `;
    }

    generatePropertiesHTML(elementData) {
        const element = elementData.konvaObject;
        const type = elementData.type;
        
        let html = this.generateBasePropertiesHTML(element);

        // For groups (like our image element), width/height are on the group itself
        // For other shapes like rectangle, width/height are direct attributes.
        // The transformer interacts with the node's width(), height(), scaleX(), scaleY().
        // Do not show dimension properties for lines, as length is visual.
        if (['rectangle', 'image', 'paragraph', 'list'].includes(type) || (element instanceof Konva.Group && type !== 'image' && type !== 'avatar')) {
            html += this.generateDimensionPropertiesHTML(element);
        } else if (type === 'image') { 
             html += this.generateDimensionPropertiesHTML(element);
        }
        
        if (type === 'text' || type === 'heading' || type === 'paragraph' || type === 'list') {
            html += this.generateTextStylingPropertiesHTML(element);
        }
        
        if (type === 'rectangle') {
            html += this.generateShapeStylingPropertiesHTML(element);
        }

        if (type === 'image') {
            html += this.generateImagePropertiesHTML(element);
        }

        if (type === 'line') {
            html += this.generateLineStylingPropertiesHTML(elementData);
        }

        if (type === 'avatar') {
            html += this.generateAvatarPropertiesHTML(element);
        }

        if (type === 'circle') {
            html += this.generateCirclePropertiesHTML(element);
        }

        if (type === 'icon') {
            html += this.generateIconPropertiesHTML(element);
        }

        if (type === 'progress-bar') {
            html += this.generateProgressBarPropertiesHTML(element);
        }

        if (type === 'rating') {
            html += this.generateRatingPropertiesHTML(element);
        }
        
        return html;
    }

    generateTextStylingPropertiesHTML(element) {
        const elementData = this.elements.get(element.id());
        const isListType = elementData && elementData.type === 'list';
        const currentBulletStyle = isListType ? (elementData.properties.bulletStyle || '•') : '';

        let html = `
            <div class="property-group">
                <label class="property-label">Nội dung</label>
                <textarea class="property-input ${isListType ? 'list-text-property-input' : ''}" data-property="text" rows="3">${element.text()}</textarea>
                <button type="button" class="ai-hint-btn" data-action="toggle-ai-prompt">AI Gợi ý</button>
                <div class="ai-prompt-container hidden">
                    <textarea class="property-input ai-prompt-textarea" data-property="aiPrompt" placeholder="Nhập yêu cầu cho AI..." rows="2"></textarea>
                    <button type="button" class="ai-submit-btn" data-action="submit-ai-prompt">Gửi</button>
                </div>
            </div>
            <div class="property-group">
                <label class="property-label">Kích thước font</label>
                <input type="number" class="property-input" data-property="fontSize" value="${element.fontSize()}" min="8" max="72">
            </div>
            <div class="property-group">
                <label class="property-label">Màu chữ</label>
                <div class="color-picker">
                    <input type="color" class="color-input" data-property="fill" value="${element.fill()}">
                    <span>${element.fill()}</span>
                </div>
            </div>
            <div class="property-group">
                <label class="property-label">Font chữ</label>
                <select class="property-input" data-property="fontFamily">
                    <option value="Arial" ${element.fontFamily() === 'Arial' ? 'selected' : ''}>Arial</option>
                    <option value="Times New Roman" ${element.fontFamily() === 'Times New Roman' ? 'selected' : ''}>Times New Roman</option>
                    <option value="Helvetica" ${element.fontFamily() === 'Helvetica' ? 'selected' : ''}>Helvetica</option>
                </select>
            </div>`;

        if (isListType) {
            html += `
            <div class="property-group">
                <label class="property-label">Kiểu danh sách</label>
                <select class="property-input" data-property="bulletStyle">
                    <option value="•" ${currentBulletStyle === '•' ? 'selected' : ''}>• (Chấm tròn)</option>
                    <option value="-" ${currentBulletStyle === '-' ? 'selected' : ''}>- (Gạch ngang)</option>
                    <option value="1." ${currentBulletStyle === '1.' ? 'selected' : ''}>1. (Số)</option>
                </select>
            </div>`;
        }

        html += `
            <div class="property-group">
                <label class="property-label">Định dạng</label>
                <div class="font-controls">
                    <button class="font-btn ${element.fontStyle().includes('bold') ? 'active' : ''}" data-style="bold">
                        <i class="fas fa-bold"></i>
                    </button>
                    <button class="font-btn ${element.fontStyle().includes('italic') ? 'active' : ''}" data-style="italic">
                        <i class="fas fa-italic"></i>
                    </button>
                    <button class="font-btn ${element.textDecoration() === 'underline' ? 'active' : ''}" data-style="underline">
                        <i class="fas fa-underline"></i>
                    </button>
                </div>
            </div>
        `;
        return html;
    }

    generateShapeStylingPropertiesHTML(element) {
        // This method now specifically handles styling for shapes like rectangles (e.g., fill, stroke)
        // Dimensions are handled by generateDimensionPropertiesHTML
        let html = '';
        
        // Example for rectangle specific properties (fill, stroke)
        // This previously was part of generateShapePropertiesHTML
        html += `
            <div class="property-group">
                <label class="property-label">Màu nền</label>
                <div class="color-picker">
                    <input type="color" class="color-input" data-property="fill" value="${element.fill()}">
                    <span>${element.fill()}</span>
                </div>
            </div>
            <div class="property-group">
                <label class="property-label">Màu viền</label>
                <div class="color-picker">
                    <input type="color" class="color-input" data-property="stroke" value="${element.stroke()}">
                    <span>${element.stroke()}</span>
                </div>
            </div>
        `;
        
        return html;
    }

    generateLineStylingPropertiesHTML(elementData) {
        const element = elementData.konvaObject;
        const currentLineStyle = elementData.properties.lineStyle || 'solid';
        const currentStrokeWidth = elementData.properties.strokeWidth || 2;

        return `
            <div class="property-group">
                <label class="property-label">Màu đường kẻ</label>
                <div class="color-picker">
                    <input type="color" class="color-input" data-property="stroke" value="${element.stroke()}">
                    <span>${element.stroke()}</span>
                </div>
            </div>
            <div class="property-group">
                <label class="property-label">Độ dày</label>
                <input type="number" class="property-input" data-property="strokeWidth" value="${currentStrokeWidth}" min="1" max="50">
            </div>
            <div class="property-group">
                <label class="property-label">Kiểu đường kẻ</label>
                <select class="property-input" data-property="lineStyle">
                    <option value="solid" ${currentLineStyle === 'solid' ? 'selected' : ''}>Nét liền</option>
                    <option value="dashed" ${currentLineStyle === 'dashed' ? 'selected' : ''}>Nét đứt</option>
                    <option value="dotted" ${currentLineStyle === 'dotted' ? 'selected' : ''}>Nét chấm</option>
                </select>
            </div>
        `;
    }

    generateImagePropertiesHTML(element) {
        // element is the Konva.Group representing the image
        const rectNode = element.findOne('.image-placeholder-rect');
        const textNode = element.findOne('.image-placeholder-text');

        const placeholderText = textNode ? textNode.text() : 'Hình ảnh';
        const placeholderFill = rectNode ? rectNode.fill() : '#f0f0f0';

        return `
            <div class="property-group">
                <label class="property-label">Nội dung Placeholder</label>
                <input type="text" class="property-input" data-property="placeholderText" value="${placeholderText}">
            </div>
            <div class="property-group">
                <label class="property-label">Màu nền Placeholder</label>
                <div class="color-picker">
                    <input type="color" class="color-input" data-property="placeholderFill" value="${placeholderFill}">
                    <span>${placeholderFill}</span>
                </div>
            </div>
            <div class="property-group">
                <label class="property-label">Nguồn ảnh (URL)</label>
                <input type="text" class="property-input" data-property="imageSrc" value="" placeholder="Dán URL ảnh..." disabled>
                <button class="property-input mt-10" data-action="uploadImage" disabled>Tải ảnh lên</button>
            </div>
        `;
    }

    generateAvatarPropertiesHTML(element) {
        // element is the Konva.Group representing the avatar
        const circleNode = element.findOne('.avatar-placeholder-circle');
        const textNode = element.findOne('.avatar-placeholder-text');

        const radius = circleNode ? circleNode.radius() : 50;
        const placeholderText = textNode ? textNode.text() : 'Avatar';
        const placeholderFill = circleNode ? circleNode.fill() : '#e9ecef';
        const placeholderStroke = circleNode ? circleNode.stroke() : '#adb5bd';

        return `
            <div class="property-group">
                <label class="property-label">Bán kính</label>
                <input type="number" class="property-input" data-property="radius" value="${radius}" min="10">
            </div>
            <div class="property-group">
                <label class="property-label">Nội dung Placeholder</label>
                <input type="text" class="property-input" data-property="placeholderText" value="${placeholderText}">
            </div>
            <div class="property-group">
                <label class="property-label">Màu nền Placeholder</label>
                <div class="color-picker">
                    <input type="color" class="color-input" data-property="placeholderFill" value="${placeholderFill}">
                    <span>${placeholderFill}</span>
                </div>
            </div>
             <div class="property-group">
                <label class="property-label">Màu viền Placeholder</label>
                <div class="color-picker">
                    <input type="color" class="color-input" data-property="stroke" value="${placeholderStroke}">
                    <span>${placeholderStroke}</span>
                </div>
            </div>
            <div class="property-group">
                <label class="property-label">Nguồn ảnh (URL)</label>
                <input type="text" class="property-input" data-property="imageSrc" value="" placeholder="Dán URL ảnh..." disabled>
                <button class="property-input mt-10" data-action="uploadImage" disabled>Tải ảnh lên</button>
            </div>
        `;
    }

    generateCirclePropertiesHTML(element) {
        // element is the Konva.Circle
        return `
            <div class="property-group">
                <label class="property-label">Bán kính</label>
                <input type="number" class="property-input" data-property="radius" value="${element.radius()}" min="5">
            </div>
            <div class="property-group">
                <label class="property-label">Màu nền</label>
                <div class="color-picker">
                    <input type="color" class="color-input" data-property="fill" value="${element.fill()}">
                    <span>${element.fill()}</span>
                </div>
            </div>
            <div class="property-group">
                <label class="property-label">Màu viền</label>
                <div class="color-picker">
                    <input type="color" class="color-input" data-property="stroke" value="${element.stroke()}">
                    <span>${element.stroke()}</span>
                </div>
            </div>
            <div class="property-group">
                <label class="property-label">Độ dày viền</label>
                <input type="number" class="property-input" data-property="strokeWidth" value="${element.strokeWidth()}" min="0">
            </div>
        `;
    }

    generateIconPropertiesHTML(element) {
        const textNode = element.findOne('.icon-text');

        const iconColor = textNode ? textNode.fill() : '#667eea';
        const iconChar = textNode ? textNode.text() : '★';
        const iconSize = textNode ? textNode.fontSize() : 30;

        return `
            <div class="property-group">
                <label class="property-label">Biểu tượng</label>
                <select class="property-input" data-property="iconType">
                    <option value="★" ${iconChar === '★' ? 'selected' : ''}>★ Ngôi sao</option>
                    <option value="♥" ${iconChar === '♥' ? 'selected' : ''}>♥ Trái tim</option>
                    <option value="●" ${iconChar === '●' ? 'selected' : ''}>● Chấm tròn</option>
                    <option value="▲" ${iconChar === '▲' ? 'selected' : ''}>▲ Tam giác</option>
                    <option value="■" ${iconChar === '■' ? 'selected' : ''}>■ Hình vuông</option>
                    <option value="♦" ${iconChar === '♦' ? 'selected' : ''}>♦ Kim cương</option>
                    <option value="✓" ${iconChar === '✓' ? 'selected' : ''}>✓ Dấu tick</option>
                    <option value="✗" ${iconChar === '✗' ? 'selected' : ''}>✗ Dấu X</option>
                    <option value="→" ${iconChar === '→' ? 'selected' : ''}>→ Mũi tên phải</option>
                    <option value="↑" ${iconChar === '↑' ? 'selected' : ''}>↑ Mũi tên lên</option>
                </select>
            </div>
            <div class="property-group">
                <label class="property-label">Kích thước biểu tượng</label>
                <input type="number" class="property-input" data-property="iconSize" value="${iconSize}" min="10" max="100">
            </div>
            <div class="property-group">
                <label class="property-label">Màu biểu tượng</label>
                <div class="color-picker">
                    <input type="color" class="color-input" data-property="iconColor" value="${iconColor}">
                    <span>${iconColor}</span>
                </div>
            </div>
        `;
    }

    generateProgressBarPropertiesHTML(element) {
        const backgroundNode = element.findOne('.progress-background');
        const fillNode = element.findOne('.progress-fill');
        const textNode = element.findOne('.progress-text');

        const backgroundColor = backgroundNode ? backgroundNode.fill() : '#e9ecef';
        const fillColor = fillNode ? fillNode.fill() : '#28a745';
        const textColor = textNode ? textNode.fill() : '#212529';
        
        // Calculate current value from fill width vs background width
        const currentValue = fillNode && backgroundNode ? 
            Math.round((fillNode.width() / backgroundNode.width()) * 100) : 75;

        return `
            <div class="property-group">
                <label class="property-label">Giá trị (%)</label>
                <input type="number" class="property-input" data-property="progressValue" value="${currentValue}" min="0" max="100">
            </div>
            <div class="property-group">
                <label class="property-label">Màu thanh tiến độ</label>
                <div class="color-picker">
                    <input type="color" class="color-input" data-property="fillColor" value="${fillColor}">
                    <span>${fillColor}</span>
                </div>
            </div>
            <div class="property-group">
                <label class="property-label">Màu nền</label>
                <div class="color-picker">
                    <input type="color" class="color-input" data-property="backgroundColor" value="${backgroundColor}">
                    <span>${backgroundColor}</span>
                </div>
            </div>
            <div class="property-group">
                <label class="property-label">Màu chữ</label>
                <div class="color-picker">
                    <input type="color" class="color-input" data-property="textColor" value="${textColor}">
                    <span>${textColor}</span>
                </div>
            </div>
        `;
    }

    generateRatingPropertiesHTML(element) {
        const elementData = this.elements.get(element.id());
        const stars = element.find('Text');
        
        let filledStars = 0;
        let totalStars = stars.length;
        let filledColor = '#ffd700';
        let emptyColor = '#e9ecef';
        
        stars.forEach(star => {
            if (star.text() === '★') {
                filledStars++;
                filledColor = star.fill();
            } else {
                emptyColor = star.fill();
            }
        });

        return `
            <div class="property-group">
                <label class="property-label">Đánh giá</label>
                <input type="number" class="property-input" data-property="ratingValue" value="${filledStars}" min="0" max="${totalStars}">
            </div>
            <div class="property-group">
                <label class="property-label">Tổng số sao</label>
                <input type="number" class="property-input" data-property="totalStars" value="${totalStars}" min="3" max="10">
            </div>
            <div class="property-group">
                <label class="property-label">Màu sao đầy</label>
                <div class="color-picker">
                    <input type="color" class="color-input" data-property="filledColor" value="${filledColor}">
                    <span>${filledColor}</span>
                </div>
            </div>
            <div class="property-group">
                <label class="property-label">Màu sao rỗng</label>
                <div class="color-picker">
                    <input type="color" class="color-input" data-property="emptyColor" value="${emptyColor}">
                    <span>${emptyColor}</span>
                </div>
            </div>
        `;
    }

    clearPropertiesPanel() {
        const propertiesContent = document.querySelector('.properties-content');
        if (propertiesContent) {
            propertiesContent.innerHTML = '<p class="text-center">Chọn một phần tử để chỉnh sửa</p>';
        }
    }

    showElementInfo(element) {
        const elementType = this.elements.get(element.id())?.type || 'unknown';
        const position = element.position();
        
        const statusElement = document.querySelector('.element-status');
        if (statusElement) {
            statusElement.textContent = `${elementType} - X: ${Math.round(position.x)}, Y: ${Math.round(position.y)}`;
        }
    }

    addToHistory(action, data) {
        this.history = this.history.slice(0, this.historyIndex + 1);
        
        this.history.push({
            action: action,
            data: data,
            timestamp: Date.now()
        });
        
        this.historyIndex++;
        
        if (this.history.length > 50) {
            this.history.shift();
            this.historyIndex--;
        }
        
        console.log('Action added to history:', action, data);
    }

    exportToJSON() {
        const data = {
            elements: []
        };
        
        this.elements.forEach((elementData, id) => {
            const element = elementData.konvaObject;
            data.elements.push({
                id: id,
                type: elementData.type,
                attrs: element.getAttrs(),
                properties: elementData.properties
            });
        });
        
        return JSON.stringify(data, null, 2);
    }
}

export default ElementManager;
