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
        * Digital forms with signatures
        * PDF report generation
        * Audit trail and compliance tracking
        * Recurring task configuration and automation
        * Automatic task generation for quality controls
        * Dashboard for monitoring recurring tasks
        * Personal task management interface
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
        'data/cron_data.xml',
        'views/quality_control_views.xml',
        'views/vegetable_pallet_views.xml',
        'views/pediluvios_views.xml',
        'views/recurring_task_views.xml',
        'views/dashboard_views.xml',
        'views/quality_control_menu.xml',
        'reports/quality_control_report.xml',
        'reports/vegetable_pallet_report.xml',
        'reports/pediluvios_report.xml',
        'reports/quality_control_template.xml',
        'reports/vegetable_pallet_template.xml',
        'reports/pediluvios_template.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}