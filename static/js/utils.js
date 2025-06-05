// Debounce function for search input
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Search functionality for CV list
class CVSearchFilter {
    constructor() {
        this.searchInput = document.querySelector('#cvSearchInput');
        this.templateFilter = document.querySelector('#templateFilter'); // Renamed from statusFilter
        this.editorTypeFilter = document.querySelector('#editorTypeFilter'); // Added
        this.sortFilter = document.querySelector('#sortFilter');
        this.cvCards = document.querySelectorAll('.cv-card');
        this.createCard = document.querySelector('.create-cv-card');
        this.noResultsMessage = document.querySelector('#noResults');
        
        this.init();
    }

    init() {
        if (this.searchInput) {
            this.searchInput.addEventListener('input', debounce((e) => {
                this.performSearch();
            }, 300));
        }

        if (this.templateFilter) { // Renamed from statusFilter
            this.templateFilter.addEventListener('change', () => { // Renamed from statusFilter
                this.performSearch();
            });
        }

        if (this.editorTypeFilter) { // Added
            this.editorTypeFilter.addEventListener('change', () => { // Added
                this.performSearch(); // Added
            }); // Added
        } // Added

        if (this.sortFilter) {
            this.sortFilter.addEventListener('change', () => {
                this.performSearch();
            });
        }
    }

    performSearch() {
        const searchTerm = this.searchInput ? this.searchInput.value.toLowerCase() : '';
        const templateFilterValue = this.templateFilter ? this.templateFilter.value.toLowerCase() : ''; // Renamed from statusFilter
        const editorTypeFilterValue = this.editorTypeFilter ? this.editorTypeFilter.value : ''; // Added
        const sortBy = this.sortFilter ? this.sortFilter.value : 'newest';

        let visibleCards = [];
        const hasActiveFilters = searchTerm || templateFilterValue || editorTypeFilterValue; // Updated

        this.cvCards.forEach(card => {
            const cvTitle = card.dataset.cvTitle ? card.dataset.cvTitle.toLowerCase() : '';
            const cvFullName = card.dataset.cvFullName ? card.dataset.cvFullName.toLowerCase() : '';
            const cvPosition = card.dataset.cvPosition ? card.dataset.cvPosition.toLowerCase() : '';
            const cvTemplateName = card.dataset.cvTemplate ? card.dataset.cvTemplate.toLowerCase() : ''; // Using display name for filtering
            const cvIsCanvasEditor = card.dataset.cvIsCanvasEditor === 'true'; // Added

            // Search filter - search in title, full_name, position, and template name
            const matchesSearch = !searchTerm || 
                cvTitle.includes(searchTerm) || 
                cvFullName.includes(searchTerm) ||
                cvPosition.includes(searchTerm) ||
                cvTemplateName.includes(searchTerm);

            // Template filter
            const matchesTemplate = !templateFilterValue || templateFilterValue === 'all' || cvTemplateName.includes(templateFilterValue); // Updated logic

            // Editor type filter // Added
            let matchesEditorType = true; // Added
            if (editorTypeFilterValue) { // Added
                matchesEditorType = (editorTypeFilterValue === 'canvas' && cvIsCanvasEditor) || // Added
                                    (editorTypeFilterValue === 'form' && !cvIsCanvasEditor); // Added
            } // Added

            if (matchesSearch && matchesTemplate && matchesEditorType) { // Updated condition
                card.style.display = 'block';
                visibleCards.push(card);
            } else {
                card.style.display = 'none';
            }
        });

        // Hide/show create new CV card based on active filters
        this.toggleCreateCard(!hasActiveFilters);

        // Sort visible cards
        this.sortCards(visibleCards, sortBy);

        // Show/hide no results message
        this.toggleNoResults(visibleCards.length === 0 && hasActiveFilters);
    }

    sortCards(cards, sortBy) {
        const container = document.querySelector('#cvCardsContainer');
        if (!container) return;

        cards.sort((a, b) => {
            switch (sortBy) {
                case 'name':
                    return (a.dataset.cvTitle || '').localeCompare(b.dataset.cvTitle || '');
                case 'oldest':
                    return new Date(a.dataset.cvCreated || 0) - new Date(b.dataset.cvCreated || 0);
                case 'views':
                    return (parseInt(b.dataset.cvViews) || 0) - (parseInt(a.dataset.cvViews) || 0);
                case 'downloads':
                    return (parseInt(b.dataset.cvDownloads) || 0) - (parseInt(a.dataset.cvDownloads) || 0);
                default: // newest
                    return new Date(b.dataset.cvUpdated || 0) - new Date(a.dataset.cvUpdated || 0);
            }
        });

        // Reorder DOM elements (but keep create card at the end)
        cards.forEach(card => {
            container.appendChild(card);
        });

        // Always append create card at the end if it's visible
        if (this.createCard && this.createCard.style.display !== 'none') {
            container.appendChild(this.createCard);
        }
    }

    toggleCreateCard(show) {
        if (this.createCard) {
            this.createCard.style.display = show ? 'block' : 'none';
        }
    }

    toggleNoResults(show) {
        if (this.noResultsMessage) {
            this.noResultsMessage.style.display = show ? 'block' : 'none';
        }
    }
}

// Dropdown functionality
function toggleDropdown(dropdownId) {
    // Close all other dropdowns
    document.querySelectorAll('[id^="dropdown"]').forEach((dropdown) => {
        if (dropdown.id !== dropdownId) {
            dropdown.classList.add("hidden");
        }
    });

    // Toggle current dropdown
    const dropdown = document.getElementById(dropdownId);
    if (dropdown) {
        dropdown.classList.toggle("hidden");
    }
}

// Close dropdowns when clicking outside
function initDropdownListeners() {
    document.addEventListener("click", function (e) {
        if (!e.target.closest("button")) {
            document.querySelectorAll('[id^="dropdown"]').forEach((dropdown) => {
                dropdown.classList.add("hidden");
            });
        }
    });
}

// Modal functionality
class Modal {
    constructor(modalId) {
        this.modal = document.getElementById(modalId);
        this.isOpen = false;
    }

    open() {
        if (this.modal) {
            this.modal.classList.remove('hidden');
            this.isOpen = true;
        }
    }

    close() {
        if (this.modal) {
            this.modal.classList.add('hidden');
            this.isOpen = false;
        }
    }

    toggle() {
        if (this.isOpen) {
            this.close();
        } else {
            this.open();
        }
    }
}

// CV Delete functionality
class CVDeleteManager {
    constructor() {
        this.modal = new Modal('deleteModal');
        this.cvToDelete = null;
        this.init();
    }

    init() {
        const confirmBtn = document.getElementById('confirmDelete');
        const cancelBtn = document.getElementById('cancelDelete');

        if (confirmBtn) {
            confirmBtn.addEventListener('click', () => this.confirmDelete());
        }

        if (cancelBtn) {
            cancelBtn.addEventListener('click', () => this.cancelDelete());
        }
    }

    deleteCV(cvId, cvTitle) {
        this.cvToDelete = cvId;
        this.cvTitle = cvTitle || 'CV';
        
        // Update modal content
        const modalTitle = document.querySelector('#deleteModal h3');
        const modalDescription = document.querySelector('#deleteModal p');
        
        if (modalTitle) {
            modalTitle.textContent = 'Xác nhận xóa CV';
        }
        if (modalDescription) {
            modalDescription.textContent = `Bạn có chắc chắn muốn xóa CV "${this.cvTitle}"? Hành động này không thể hoàn tác.`;
        }
        
        this.modal.open();
    }

    async confirmDelete() {
        if (!this.cvToDelete) return;

        const confirmBtn = document.getElementById('confirmDelete');
        if (confirmBtn) {
            confirmBtn.disabled = true;
            confirmBtn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Đang xóa...';
        }

        try {
            // Updated URL to match backend route pattern
            const response = await fetch(`/cv/${this.cvToDelete}/delete`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                },
            });

            const data = await response.json();

            if (data.success) {
                // Remove CV card from DOM with animation
                const cvCard = document.querySelector(`[data-cv-id="${this.cvToDelete}"]`);
                if (cvCard) {
                    cvCard.style.transform = 'scale(0.8)';
                    cvCard.style.opacity = '0';
                    setTimeout(() => {
                        cvCard.remove();
                    }, 300);
                }
                this.showNotification(data.message || `CV "${this.cvTitle}" đã được xóa thành công!`, 'success');
            } else {
                this.showNotification(data.error || 'Có lỗi xảy ra khi xóa CV', 'error');
            }
        } catch (error) {
            console.error('Error:', error);
            this.showNotification('Có lỗi xảy ra khi xóa CV', 'error');
        } finally {
            // Reset button state
            if (confirmBtn) {
                confirmBtn.disabled = false;
                confirmBtn.innerHTML = 'Xóa';
            }
            this.modal.close();
            this.cvToDelete = null;
            this.cvTitle = null;
        }
    }

    cancelDelete() {
        this.modal.close();
        this.cvToDelete = null;
        this.cvTitle = null;
    }

    showNotification(message, type = 'info') {
        // Enhanced notification with better styling
        const notification = document.createElement('div');
        notification.className = `fixed top-4 right-4 p-4 rounded-2xl shadow-lg z-50 max-w-sm transform transition-all duration-300 translate-x-full ${
            type === 'success' ? 'bg-green-600 text-white' : 
            type === 'error' ? 'bg-red-600 text-white' :
            'bg-blue-600 text-white'
        }`;
        
        notification.innerHTML = `
            <div class="flex items-center">
                <i class="fas ${
                    type === 'success' ? 'fa-check-circle' : 
                    type === 'error' ? 'fa-exclamation-circle' : 
                    'fa-info-circle'
                } mr-3"></i>
                <span>${message}</span>
                <button onclick="this.parentElement.parentElement.remove()" class="ml-4 text-white/80 hover:text-white">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;
        
        document.body.appendChild(notification);
        
        // Animate in
        setTimeout(() => {
            notification.style.transform = 'translateX(0)';
        }, 100);
        
        // Auto remove after 5 seconds
        setTimeout(() => {
            notification.style.transform = 'translateX(100%)';
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.remove();
                }
            }, 300);
        }, 5000);
    }
}

// Initialize utilities when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize search filter for CV list
    if (document.querySelector('#cvSearchInput')) {
        new CVSearchFilter();
    }

    // Initialize dropdown listeners
    initDropdownListeners();

    // Initialize delete manager
    if (document.querySelector('#deleteModal')) {
        window.cvDeleteManager = new CVDeleteManager();
    }
});

// Global functions for backward compatibility
window.toggleDropdown = toggleDropdown;
window.deleteCV = function(cvId, cvTitle) {
    if (window.cvDeleteManager) {
        window.cvDeleteManager.deleteCV(cvId, cvTitle);
    }
};
