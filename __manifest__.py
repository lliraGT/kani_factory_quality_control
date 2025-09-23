{
    'name': 'KANI - Factory Quality Control',
    'version': '17.0.1.0.0',
    'category': 'Manufacturing/Quality',
    'summary': 'Quality Control System for Factory Operations',
    'description': """
        Factory Quality Control Module for TKANI
        ==========================================
        
        This module provides:
        * Freeze Room and Pallets Cleaning Control
        * Vegetable Pallet Cleaning Control
        * Pediluvios Control and Sterbac Application
        * Pest Control for Plant KANI
        * Detailed Pest Control Management
        * Digital forms with signatures
        * PDF report generation
        * Audit trail and compliance tracking
        * Recurring task configuration and automation
        * Automatic task generation for quality controls
        * Dashboard for monitoring recurring tasks
        * Personal task management interface
        * Custom KANI branding for activity notifications
    """,
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'depends': [
        'base',
        'web',
        'mail',  # For tracking and chatter
        'sign',  # For digital signatures
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/sequence_data.xml',
        'data/activity_type_data.xml',
        'data/cron_data.xml',
        'views/quality_control_views.xml',
        'views/vegetable_pallet_views.xml',
        'views/pediluvios_views.xml',
        'views/pest_control_views.xml',
        'views/pest_control_detail_views.xml',
        'views/recurring_task_views.xml',
        'views/dashboard_views.xml',
        'views/quality_control_menu.xml',
        'reports/quality_control_report.xml',
        'reports/vegetable_pallet_report.xml',
        'reports/pediluvios_report.xml',
        'reports/pest_control_report.xml',
        'reports/pest_control_detail_report.xml',
        'reports/quality_control_template.xml',
        'reports/vegetable_pallet_template.xml',
        'reports/pediluvios_template.xml',
        'reports/pest_control_template.xml',
        'reports/pest_control_detail_template.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'kani_factory_quality_control/static/src/css/signature_styles.css',
            'kani_factory_quality_control/static/src/css/activity_icons.css',
            'kani_factory_quality_control/static/src/js/systray_notifications.js',
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}