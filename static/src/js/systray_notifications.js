/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { MessagingMenu } from "@mail/core/web/messaging_menu";

// Patch the MessagingMenu to customize notification icons
patch(MessagingMenu.prototype, {
    setup() {
        super.setup();
        // Set up observer to replace KANI notification icons
        this._setupKaniIconReplacer();
    },

    _setupKaniIconReplacer() {
        const replaceKaniNotificationIcons = () => {
            // Target the systray dropdown notifications
            const systrayDropdown = document.querySelector('.o_mail_systray_dropdown');
            if (!systrayDropdown) return;

            // Find all notification previews
            const notifications = systrayDropdown.querySelectorAll('.o_mail_preview');
            
            notifications.forEach(notification => {
                // Get the notification text content
                const textContent = notification.textContent || '';
                const resModel = notification.getAttribute('data-res-model');
                
                // Check if this is a KANI quality control notification
                const isKaniNotification = 
                    textContent.includes('Control de Calidad') ||
                    textContent.includes('KANI') ||
                    textContent.includes('Configuración de Tareas Recurrentes') ||
                    resModel === 'quality.control.recurring.task';
                
                if (isKaniNotification) {
                    // Find the preview image/icon
                    const previewImage = notification.querySelector('.o_mail_preview_image');
                    
                    if (previewImage && !previewImage.classList.contains('kani-customized')) {
                        // Mark as customized to avoid re-processing
                        previewImage.classList.add('kani-customized');
                        
                        // Apply KANI logo styling
                        previewImage.style.backgroundImage = 'url("/kani_factory_quality_control/static/src/img/kani_logo.png")';
                        previewImage.style.backgroundSize = 'contain';
                        previewImage.style.backgroundRepeat = 'no-repeat';
                        previewImage.style.backgroundPosition = 'center';
                        previewImage.style.backgroundColor = 'white';
                        previewImage.style.border = '1px solid #64b9b0';
                        previewImage.style.borderRadius = '4px';
                        previewImage.style.width = '32px';
                        previewImage.style.height = '32px';
                        
                        // Hide any child elements (original icons)
                        const children = previewImage.querySelectorAll('*');
                        children.forEach(child => {
                            child.style.display = 'none';
                        });
                    }
                    
                    // Add KANI branding to the notification item
                    if (!notification.classList.contains('kani-branded')) {
                        notification.classList.add('kani-branded');
                        notification.style.borderLeft = '3px solid #64b9b0';
                    }
                }
            });
        };

        // Run immediately
        replaceKaniNotificationIcons();

        // Set up observer for dynamic content
        const observer = new MutationObserver((mutations) => {
            let shouldReplace = false;
            mutations.forEach((mutation) => {
                if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {
                    shouldReplace = true;
                }
            });
            
            if (shouldReplace) {
                setTimeout(replaceKaniNotificationIcons, 100);
            }
        });

        // Observe the systray area for changes
        const systrayArea = document.querySelector('.o_mail_systray_item');
        if (systrayArea) {
            observer.observe(document.body, {
                childList: true,
                subtree: true
            });
        }

        // Also run when the messaging menu is clicked/opened
        const messagingButton = document.querySelector('.o_mail_systray_item');
        if (messagingButton) {
            messagingButton.addEventListener('click', () => {
                setTimeout(replaceKaniNotificationIcons, 300);
            });
        }
    }
});

// Alternative approach: Direct DOM manipulation
document.addEventListener('DOMContentLoaded', function() {
    let iconReplacementInterval;

    const startIconReplacement = () => {
        iconReplacementInterval = setInterval(() => {
            const systrayDropdown = document.querySelector('.o_mail_systray_dropdown');
            if (!systrayDropdown) return;

            const notifications = systrayDropdown.querySelectorAll('.o_mail_preview');
            
            notifications.forEach(notification => {
                const textContent = notification.textContent || '';
                const resModel = notification.getAttribute('data-res-model');
                
                const isKaniNotification = 
                    textContent.includes('Control de Calidad') ||
                    textContent.includes('KANI') ||
                    textContent.includes('Configuración de Tareas') ||
                    resModel === 'quality.control.recurring.task';
                
                if (isKaniNotification) {
                    const previewImage = notification.querySelector('.o_mail_preview_image');
                    
                    if (previewImage && !previewImage.dataset.kaniCustomized) {
                        previewImage.dataset.kaniCustomized = 'true';
                        
                        // Replace with KANI logo
                        previewImage.style.cssText = `
                            background-image: url("/kani_factory_quality_control/static/src/img/kani_logo.png") !important;
                            background-size: contain !important;
                            background-repeat: no-repeat !important;
                            background-position: center !important;
                            background-color: white !important;
                            border: 1px solid #64b9b0 !important;
                            border-radius: 4px !important;
                            width: 32px !important;
                            height: 32px !important;
                        `;
                        
                        // Hide original content
                        Array.from(previewImage.children).forEach(child => {
                            child.style.display = 'none';
                        });
                    }
                    
                    // Add KANI branding
                    if (!notification.dataset.kaniBranded) {
                        notification.dataset.kaniBranded = 'true';
                        notification.style.borderLeft = '3px solid #64b9b0';
                    }
                }
            });
        }, 1000);
    };

    const stopIconReplacement = () => {
        if (iconReplacementInterval) {
            clearInterval(iconReplacementInterval);
        }
    };

    // Start monitoring when messaging menu is likely to be opened
    document.addEventListener('click', (e) => {
        if (e.target.closest('.o_mail_systray_item')) {
            startIconReplacement();
            // Stop after 10 seconds to avoid performance issues
            setTimeout(stopIconReplacement, 10000);
        }
    });
});