class ElementFactory {
    constructor() {
        this.elementCounter = 0;
    }

    createElement(type, position = null) {
        const id = `element_${++this.elementCounter}`;
        const defaultPosition = position || {
            x: 50 + (this.elementCounter * 20),
            y: 50 + (this.elementCounter * 20)
        };
        const defaultProps = this.getDefaultProperties(type);

        switch (type) {
            case 'text':
                return this.createTextElement(id, defaultPosition);
            case 'heading':
                return this.createHeadingElement(id, defaultPosition);
            case 'paragraph':
                return this.createParagraphElement(id, defaultPosition);
            case 'list':
                return this.createListElement(id, defaultPosition, defaultProps.bulletStyle);
            case 'image':
                return this.createImageElement(id, defaultPosition);
            case 'rectangle':
                return this.createRectangleElement(id, defaultPosition);
            case 'line':
                return this.createLineElement(id, defaultPosition);
            case 'avatar':
                return this.createAvatarElement(id, defaultPosition);
            case 'circle':
                return this.createCircleElement(id, defaultPosition);
            case 'icon':
                return this.createIconElement(id, defaultPosition);
            case 'progress-bar':
                return this.createProgressBarElement(id, defaultPosition);
            case 'rating':
                return this.createRatingElement(id, defaultPosition);
            default:
                console.warn('Unknown element type:', type);
                return null;
        }
    }

    createTextElement(id, position) {
        const text = new Konva.Text({
            id: id,
            x: position.x,
            y: position.y,
            text: 'Nhập văn bản...',
            fontSize: 14,
            fontFamily: 'Arial',
            fill: '#333333',
            draggable: true,
            name: 'cv-element text-element' // Added specific class name
        });

        return text;
    }

    createHeadingElement(id, position) {
        const heading = new Konva.Text({
            id: id,
            x: position.x,
            y: position.y,
            text: 'Tiêu đề',
            fontSize: 24,
            fontFamily: 'Arial',
            fontStyle: 'bold',
            fill: '#2c3e50',
            draggable: true,
            name: 'cv-element heading-element' // Added specific class name
        });

        return heading;
    }

    createParagraphElement(id, position) {
        const paragraph = new Konva.Text({
            id: id,
            x: position.x,
            y: position.y,
            text: 'Đây là một đoạn văn mẫu. Bạn có thể chỉnh sửa nội dung này để phù hợp với CV của mình. Hãy cung cấp thông tin chi tiết và rõ ràng.',
            fontSize: 14,
            fontFamily: 'Arial',
            fill: '#333333',
            width: 300, // Default width for wrapping
            lineHeight: 1.5,
            draggable: true,
            name: 'cv-element paragraph-element'
        });
        return paragraph;
    }

    createListElement(id, position, bulletStyle = '•') {
        const items = ['Mục 1', 'Mục 2', 'Mục 3'];
        const listText = items.map((item, index) => {
            if (bulletStyle === '1.') {
                return `${index + 1}. ${item}`;
            }
            return `${bulletStyle} ${item}`;
        }).join('\n');

        const list = new Konva.Text({
            id: id,
            x: position.x,
            y: position.y,
            text: listText,
            fontSize: 14,
            fontFamily: 'Arial',
            fill: '#333333',
            width: 200, // Default width
            lineHeight: 1.6,
            draggable: true,
            name: 'cv-element list-element'
        });
        return list;
    }

    createImageElement(id, position) {
        const defaultProps = this.getDefaultProperties('image');
        const rect = new Konva.Rect({
            // id: id, // ID should be on the group
            x: 0, // Position relative to group
            y: 0, // Position relative to group
            width: defaultProps.width,
            height: defaultProps.height,
            fill: defaultProps.fill,
            stroke: defaultProps.stroke,
            strokeWidth: 2,
            name: 'image-placeholder-rect' // Specific name for inner rect
        });

        const placeholderText = new Konva.Text({
            x: defaultProps.width / 2, // Centered
            y: defaultProps.height / 2, // Centered
            text: defaultProps.placeholderText,
            fontSize: 14,
            fill: '#6c757d',
            listening: false,
            name: 'image-placeholder-text', // Specific name for inner text
            align: 'center',
            verticalAlign: 'middle',
        });
        // Adjust text position to be truly centered
        placeholderText.offsetX(placeholderText.width() / 2);
        placeholderText.offsetY(placeholderText.height() / 2);


        const group = new Konva.Group({
            id: id,
            x: position.x,
            y: position.y,
            width: defaultProps.width, // Set group width for transformer
            height: defaultProps.height, // Set group height for transformer
            draggable: true,
            name: 'cv-element image-element' // Specific name for image group
        });

        group.add(rect);
        group.add(placeholderText);

        // Ensure group's width/height are set for the transformer
        // Konva.Group width/height are not automatically derived from children for transforms.
        // We can set them explicitly or rely on transformer to scale.
        // For consistency with other elements, let's set them.
        group.width(defaultProps.width);
        group.height(defaultProps.height);


        return group;
    }

    createRectangleElement(id, position) {
        const rectangle = new Konva.Rect({
            id: id,
            x: position.x,
            y: position.y,
            width: 200,
            height: 100,
            fill: '#667eea',
            stroke: '#5a67d8',
            strokeWidth: 2,
            draggable: true,
            name: 'cv-element'
        });

        return rectangle;
    }

    createLineElement(id, position) {
        const defaultProps = this.getDefaultProperties('line');
        const line = new Konva.Line({
            id: id,
            points: [position.x, position.y, position.x + 200, position.y],
            stroke: defaultProps.stroke,
            strokeWidth: defaultProps.strokeWidth,
            draggable: true,
            name: 'cv-element line-element', // Specific name for line element
            hitStrokeWidth: 15, // Increased hit area for easier selection
            dash: defaultProps.dashArray || [] // e.g. [] for solid, [10, 5] for dashed
        });

        return line;
    }

    createAvatarElement(id, position) {
        const defaultProps = this.getDefaultProperties('avatar');
        const group = new Konva.Group({
            id: id,
            x: position.x,
            y: position.y,
            width: defaultProps.radius * 2, // Group width for transformer
            height: defaultProps.radius * 2, // Group height for transformer
            draggable: true,
            name: 'cv-element avatar-element' // Specific name for avatar group
        });

        const circlePlaceholder = new Konva.Circle({
            x: defaultProps.radius, // Center of the group
            y: defaultProps.radius, // Center of the group
            radius: defaultProps.radius,
            fill: defaultProps.fill,
            stroke: defaultProps.stroke,
            strokeWidth: 2,
            name: 'avatar-placeholder-circle'
        });

        const placeholderText = new Konva.Text({
            x: defaultProps.radius, // Centered
            y: defaultProps.radius, // Centered
            text: defaultProps.placeholderText,
            fontSize: Math.max(10, defaultProps.radius / 4), // Dynamic font size
            fill: '#6c757d',
            listening: false,
            name: 'avatar-placeholder-text',
            align: 'center',
            verticalAlign: 'middle',
        });
        // Adjust text position to be truly centered
        placeholderText.offsetX(placeholderText.width() / 2);
        placeholderText.offsetY(placeholderText.height() / 2);

        group.add(circlePlaceholder);
        group.add(placeholderText);

        // Set group width/height for transformer consistency
        group.width(defaultProps.radius * 2);
        group.height(defaultProps.radius * 2);

        return group;
    }

    createCircleElement(id, position) {
        const defaultProps = this.getDefaultProperties('circle');
        const circle = new Konva.Circle({
            id: id,
            x: position.x,
            y: position.y,
            radius: defaultProps.radius,
            fill: defaultProps.fill,
            stroke: defaultProps.stroke,
            strokeWidth: 2,
            draggable: true,
            name: 'cv-element circle-element' // Specific name for circle element
        });
        return circle;
    }

    createIconElement(id, position) {
        const defaultProps = this.getDefaultProperties('icon');
        const group = new Konva.Group({
            id: id,
            x: position.x,
            y: position.y,
            width: defaultProps.size,
            height: defaultProps.size,
            draggable: true,
            name: 'cv-element icon-element'
        });

        // Create icon text only (removed background circle)
        const iconText = new Konva.Text({
            x: defaultProps.size / 2,
            y: defaultProps.size / 2,
            text: defaultProps.iconChar, // Unicode character for the icon
            fontSize: defaultProps.iconSize,
            fontFamily: 'Arial', // Changed from Font Awesome to Arial for better compatibility
            fill: defaultProps.iconColor,
            align: 'center',
            verticalAlign: 'middle',
            name: 'icon-text'
        });
        
        // Center the icon text
        iconText.offsetX(iconText.width() / 2);
        iconText.offsetY(iconText.height() / 2);

        group.add(iconText);
        group.width(defaultProps.size);
        group.height(defaultProps.size);

        return group;
    }

    createProgressBarElement(id, position) {
        const defaultProps = this.getDefaultProperties('progress-bar');
        const group = new Konva.Group({
            id: id,
            x: position.x,
            y: position.y,
            width: defaultProps.width,
            height: defaultProps.height,
            draggable: true,
            name: 'cv-element progress-bar-element'
        });

        // Background bar
        const background = new Konva.Rect({
            x: 0,
            y: 0,
            width: defaultProps.width,
            height: defaultProps.height,
            fill: defaultProps.backgroundColor,
            stroke: defaultProps.borderColor,
            strokeWidth: 1,
            cornerRadius: defaultProps.height / 2,
            name: 'progress-background'
        });

        // Progress fill
        const progress = new Konva.Rect({
            x: 0,
            y: 0,
            width: defaultProps.width * (defaultProps.value / 100),
            height: defaultProps.height,
            fill: defaultProps.fillColor,
            cornerRadius: defaultProps.height / 2,
            name: 'progress-fill'
        });

        // Progress text
        const progressText = new Konva.Text({
            x: defaultProps.width / 2,
            y: defaultProps.height / 2,
            text: `${defaultProps.value}%`,
            fontSize: defaultProps.fontSize,
            fontFamily: 'Arial',
            fill: defaultProps.textColor,
            align: 'center',
            verticalAlign: 'middle',
            name: 'progress-text'
        });
        
        progressText.offsetX(progressText.width() / 2);
        progressText.offsetY(progressText.height() / 2);

        group.add(background);
        group.add(progress);
        group.add(progressText);
        group.width(defaultProps.width);
        group.height(defaultProps.height);

        return group;
    }

    createRatingElement(id, position) {
        const defaultProps = this.getDefaultProperties('rating');
        const group = new Konva.Group({
            id: id,
            x: position.x,
            y: position.y,
            width: defaultProps.totalStars * (defaultProps.starSize + defaultProps.spacing),
            height: defaultProps.starSize,
            draggable: true,
            name: 'cv-element rating-element'
        });

        // Create stars
        for (let i = 0; i < defaultProps.totalStars; i++) {
            const star = new Konva.Text({
                x: i * (defaultProps.starSize + defaultProps.spacing),
                y: 0,
                text: i < defaultProps.rating ? '★' : '☆',
                fontSize: defaultProps.starSize,
                fill: i < defaultProps.rating ? defaultProps.filledColor : defaultProps.emptyColor,
                fontFamily: 'Arial',
                name: `star-${i}`
            });
            
            group.add(star);
        }

        group.width(defaultProps.totalStars * (defaultProps.starSize + defaultProps.spacing));
        group.height(defaultProps.starSize);

        return group;
    }

    getDefaultProperties(type) {
        const defaults = {
            text: { fontSize: 14, fontFamily: 'Arial', fill: '#333333' },
            heading: { fontSize: 24, fontFamily: 'Arial', fill: '#2c3e50', fontStyle: 'bold' },
            paragraph: { fontSize: 14, fontFamily: 'Arial', fill: '#333333', width: 300, lineHeight: 1.5 },
            list: { fontSize: 14, fontFamily: 'Arial', fill: '#333333', width: 200, lineHeight: 1.6, bulletStyle: '•' },
            rectangle: { width: 200, height: 100, fill: '#667eea', stroke: '#5a67d8' },
            image: { width: 150, height: 150, fill: '#f8f9fa', stroke: '#dee2e6', placeholderText: 'Hình ảnh' },
            line: { stroke: '#333333', strokeWidth: 2, lineStyle: 'solid', dashArray: [] },
            avatar: { radius: 50, fill: '#e9ecef', stroke: '#adb5bd', placeholderText: 'Avatar' },
            circle: { radius: 50, fill: '#ff6b6b', stroke: '#c92a2a' },
            icon: { 
                size: 40, // Reduced size since no background circle
                iconChar: '★', 
                iconSize: 30, 
                iconColor: '#667eea' // Changed default color
            },
            'progress-bar': { 
                width: 200, 
                height: 20, 
                value: 75, 
                backgroundColor: '#e9ecef', 
                fillColor: '#28a745', 
                borderColor: '#dee2e6', 
                textColor: '#212529', 
                fontSize: 12 
            },
            rating: { 
                totalStars: 5, 
                rating: 4, 
                starSize: 20, 
                spacing: 5, 
                filledColor: '#ffd700', 
                emptyColor: '#e9ecef' 
            }
        };

        return defaults[type] || {};
    }

    createElementFromData(elementData) {
        // Create element from saved data (for loading from JSON)
        const id = elementData.id || `element_${++this.elementCounter}`;
        
        let element;
        
        // Handle different data formats
        if (elementData.className) {
            // Handle Konva node data
            element = this.createFromKonvaData(elementData);
        } else if (elementData.type) {
            // Handle custom element data
            element = this.createElement(elementData.type, {
                x: elementData.attrs?.x || 0,
                y: elementData.attrs?.y || 0
            });
            
            if (element && elementData.attrs) {
                element.setAttrs({
                    ...elementData.attrs,
                    id: id,
                    draggable: true,
                    name: 'cv-element'
                });
            }
        }
        
        return element;
    }

    createFromKonvaData(nodeData) {
        try {
            // Use Konva.Node.create to recreate from Konva JSON
            const node = Konva.Node.create(nodeData);
            
            if (node) {
                // Ensure the node is interactive
                node.setAttrs({
                    draggable: true,
                    name: 'cv-element',
                    id: nodeData.attrs?.id || `element_${++this.elementCounter}`
                });
            }
            
            return node;
        } catch (error) {
            console.error('Error creating from Konva data:', error);
            return null;
        }
    }

    // Create a text element from Konva text data
    createTextFromKonvaData(textData) {
        const attrs = textData.attrs || {};
        return new Konva.Text({
            id: attrs.id || `element_${++this.elementCounter}`,
            x: attrs.x || 0,
            y: attrs.y || 0,
            text: attrs.text || 'Text',
            fontSize: attrs.fontSize || 14,
            fontFamily: attrs.fontFamily || 'Arial',
            fill: attrs.fill || '#000000',
            fontStyle: attrs.fontStyle || 'normal',
            textDecoration: attrs.textDecoration || '',
            align: attrs.align || 'left',
            draggable: true,
            name: 'cv-element',
            ...attrs
        });
    }

    // Create a rectangle from Konva rect data
    createRectFromKonvaData(rectData) {
        const attrs = rectData.attrs || {};
        return new Konva.Rect({
            id: attrs.id || `element_${++this.elementCounter}`,
            x: attrs.x || 0,
            y: attrs.y || 0,
            width: attrs.width || 100,
            height: attrs.height || 50,
            fill: attrs.fill || '#cccccc',
            stroke: attrs.stroke || '#000000',
            strokeWidth: attrs.strokeWidth || 0,
            cornerRadius: attrs.cornerRadius || 0,
            draggable: true,
            name: 'cv-element',
            ...attrs
        });
    }
}

export default ElementFactory;
