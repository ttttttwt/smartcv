import ElementFactory from './elements/elementFactory.js';
import ElementManager from './elements/elementManager.js';
import ElementEventHandler from './elements/elementEventHandler.js';

// Export all element-related classes
export {
    ElementFactory,
    ElementManager,
    ElementEventHandler
};

// For backward compatibility, also attach to window
if (typeof window !== 'undefined') {
    window.ElementFactory = ElementFactory;
    window.ElementManager = ElementManager;
    window.ElementEventHandler = ElementEventHandler;
}
