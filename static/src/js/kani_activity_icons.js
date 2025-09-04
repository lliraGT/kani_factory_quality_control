/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { ActivityMenu } from "@mail/core/web/activity_menu";

// Patch the ActivityMenu to customize KANI activity icons
patch(ActivityMenu.prototype, {
    setup() {
        super.setup();
        this._replaceKaniIcons();
    },

    _replaceKaniIcons() {
        // Function to replace cube icons with KANI logo
        const replaceIcons = () => {
            // Target all activity items in the notification tray
            const activityItems = document.querySelectorAll('.o_mail_systray_dropdown .o_mail_preview, .o_mail_activity_preview');
            
            activityItems.forEach(item => {
                // Check if this is a KANI quality control activity
                const resModel = item.dataset.resModel || item.getAttribute('data-res-model');
                const activityText = item.textContent || '';
                
                if (resModel === 'quality.control.recurring.task' || 
                    activityText.includes('Control de Calidad') ||
                    activityText.includes('KANI')) {
                    
                    // Find the icon element
                    const iconElement = item.querySelector('.o_mail_preview_image, .o_activity_type_icon, .fa-cube');
                    
                    if (iconElement) {
                        // Replace with KANI logo
                        iconElement.style.backgroundImage = 'url("/kani_factory_quality_control/static/src/img/kani_logo.png")';
                        iconElement.style.backgroundSize = 'contain';
                        iconElement.style.backgroundRepeat = 'no-repeat';
                        iconElement.style.backgroundPosition = 'center';
                        iconElement.style.backgroundColor = 'white';
                        iconElement.style.border = '1px solid #64b9b0';
                        iconElement.style.borderRadius = '4px';
                        iconElement.style.width = '32px';
                        iconElement.style.height = '32px';
                        
                        // Hide any child elements (like FA icons)
                        const childIcons = iconElement.querySelectorAll('.fa, i');
                        childIcons.forEach(child => {
                            child.style.display = 'none';
                        });
                    }
                    
                    // Add KANI branding to the item
                    item.style.borderLeft = '3px solid #64b9b0';
                }
            });

            // Also target cube icons specifically
            const cubeIcons = document.querySelectorAll('.o_mail_systray_dropdown .fa-cube');
            cubeIcons.forEach(icon => {
                const activityItem = icon.closest('.o_mail_preview, .o_mail_activity_preview');
                if (activityItem) {
                    const activityText = activityItem.textContent || '';
                    if (activityText.includes('Control de Calidad') || activityText.includes('KANI')) {
                        icon.style.backgroundImage = 'url("/kani_factory_quality_control/static/src/img/kani_logo.png")';
                        icon.style.backgroundSize = 'contain';
                        icon.style.backgroundRepeat = 'no-repeat';
                        icon.style.backgroundPosition = 'center';
                        icon.style.backgroundColor = 'white';
                        icon.style.border = '1px solid #64b9b0';
                        icon.style.borderRadius = '3px';
                        icon.style.color = 'transparent';
                        icon.style.fontSize = '0';
                        icon.style.width = '24px';
                        icon.style.height = '24px';
                    }
                }
            });
        };

        // Replace icons immediately
        replaceIcons();

        // Set up observer for dynamic content
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {
                    // Small delay to ensure DOM is ready
                    setTimeout(replaceIcons, 100);
                }
            });
        });

        // Observe the notification area for changes
        const notificationArea = document.querySelector('.o_mail_systray_dropdown');
        if (notificationArea) {
            observer.observe(notificationArea, {
                childList: true,
                subtree: true
            });
        }

        // Also replace icons when the menu is opened
        setTimeout(replaceIcons, 500);
    }
});

// Alternative approach: Direct DOM manipulation when activities are loaded
document.addEventListener('DOMContentLoaded', function() {
    const replaceKaniActivityIcons = () => {
        // Target all elements that might contain KANI activities
        const selectors = [
            '.o_mail_systray_dropdown .o_mail_preview',
            '.o_mail_activity_preview',
            '.o_activity'
        ];

        selectors.forEach(selector => {
            const elements = document.querySelectorAll(selector);
            elements.forEach(element => {
                const text = element.textContent || '';
                const resModel = element.dataset.resModel || element.getAttribute('data-res-model');
                
                if (resModel === 'quality.control.recurring.task' || 
                    text.includes('Control de Calidad') ||
                    text.includes('KANI') ||
                    text.includes('Configuración de Tareas Recurrentes')) {
                    
                    // Find and replace the icon
                    const iconSelectors = [
                        '.o_mail_preview_image',
                        '.o_activity_type_icon', 
                        '.fa-cube',
                        'i.fa'
                    ];
                    
                    iconSelectors.forEach(iconSelector => {
                        const icon = element.querySelector(iconSelector);
                        if (icon) {
                            // Apply KANI logo styling
                            icon.style.backgroundImage = 'url("/kani_factory_quality_control/static/src/img/kani_logo.png")';
                            icon.style.backgroundSize = 'contain';
                            icon.style.backgroundRepeat = 'no-repeat';
                            icon.style.backgroundPosition = 'center';
                            icon.style.backgroundColor = 'white';
                            icon.style.border = '1px solid #64b9b0';
                            icon.style.borderRadius = '4px';
                            icon.style.color = 'transparent';
                            icon.style.fontSize = '0';
                            
                            // Hide child icons
                            const childIcons = icon.querySelectorAll('*');
                            childIcons.forEach(child => {
                                child.style.display = 'none';
                            });
                        }
                    });
                    
                    // Add KANI border
                    element.style.borderLeft = '3px solid #64b9b0';
                }
            });
        });
    };

    // Run immediately and set up periodic replacement
    replaceKaniActivityIcons();
    setInterval(replaceKaniActivityIcons, 2000);

    // Also run when clicking on the activity menu
    document.addEventListener('click', function(e) {
        if (e.target.closest('.o_mail_systray_item')) {
            setTimeout(replaceKaniActivityIcons, 300);
        }
    });
});