from odoo import models, fields, api, _ # type: ignore
from odoo.exceptions import ValidationError
from datetime import datetime


class QualityControlCleaningRoom(models.Model):
    _name = 'quality.control.cleaning.room'
    _description = 'Control de Limpieza de Cuarto Refrigerado y Pallets'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'control_date desc'

    name = fields.Char(
        string='Control Number',
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: self.env['ir.sequence'].next_by_code('quality.control.cleaning.room')
    )
    
    # Single date field - control and cleaning happen same day
    control_date = fields.Date(
        string='Fecha de Control/Limpieza',
        default=fields.Date.context_today,
        required=True,
        tracking=True
    )
    
    responsible_id = fields.Many2one(
        'res.users',
        string='Responsable - Asistente de Cocina',
        required=True,
        default=lambda self: self.env.user,
        tracking=True
    )
    
    supervisor_id = fields.Many2one(
        'res.users',
        string='Supervisión - Supervisor de Cocina y Deshidratados',
        required=True,
        tracking=True
    )
    
    # Unified compliance field - True = Compliant, False = Non-compliant
    is_compliant = fields.Boolean(
        string='Control Cumple',
        default=True,
        tracking=True,
        help="Activado = Sí Cumple, Desactivado = No Cumple"
    )
    
    attention_required = fields.Boolean(
        string='Llamada de Atención',
        tracking=True
    )
    
    # Signatures (using Binary field with image widget)
    responsible_signature = fields.Binary(
        string='Firma del Responsable',
        attachment=True
    )
    
    supervisor_signature = fields.Binary(
        string='Firma del Supervisor',
        attachment=True
    )
    
    # Status
    state = fields.Selection([
        ('draft', 'Borrador'),
        ('in_progress', 'En Progreso'),
        ('completed', 'Completado'),
        ('validated', 'Validado')
    ], string='Estado', default='draft', tracking=True)
    
    notes = fields.Text(string='Observaciones Generales')
    
    def action_start_control(self):
        """Start the quality control process"""
        self.state = 'in_progress'
        return True
    
    def action_complete_control(self):
        """Mark control as completed"""
        if not self.responsible_signature:
            raise ValidationError(_("Se requiere la firma del responsable para completar el control"))
        self.state = 'completed'
        return True
    
    def action_validate_control(self):
        """Validate the control (supervisor action)"""
        if not self.supervisor_signature:
            raise ValidationError(_("Se requiere la firma del supervisor para validar"))
        self.state = 'validated'
        return True
    
    def action_reset_to_draft(self):
        """Reset to draft state"""
        self.state = 'draft'
        return True

# Add this to models/quality_control.py at the end
class QualityControlVegetablePalletCleaning(models.Model):
    _name = 'quality.control.vegetable.pallet.cleaning'
    _description = 'Control de Limpieza de Palets de Verdura'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'control_date desc'

    name = fields.Char(
        string='Control Number',
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: self.env['ir.sequence'].next_by_code('quality.control.vegetable.pallet.cleaning')
    )
    
    # Single date field - control and cleaning happen same day
    control_date = fields.Date(
        string='Fecha de Control/Limpieza',
        default=fields.Date.context_today,
        required=True,
        tracking=True
    )
    
    responsible_id = fields.Many2one(
        'res.users',
        string='Responsable - Asistente de Cocina',
        required=True,
        default=lambda self: self.env.user,
        tracking=True
    )
    
    supervisor_id = fields.Many2one(
        'res.users',
        string='Supervisión - Supervisor de Cocina y Deshidratados',
        required=True,
        tracking=True
    )
    
    # Unified compliance field - True = Compliant, False = Non-compliant
    is_compliant = fields.Boolean(
        string='Control Cumple',
        default=True,
        tracking=True,
        help="Activado = Sí Cumple, Desactivado = No Cumple"
    )
    
    attention_required = fields.Boolean(
        string='Llamada de Atención',
        tracking=True
    )
    
    # Signatures (using Binary field with image widget)
    responsible_signature = fields.Binary(
        string='Firma del Responsable',
        attachment=True
    )
    
    supervisor_signature = fields.Binary(
        string='Firma del Supervisor',
        attachment=True
    )
    
    # Status
    state = fields.Selection([
        ('draft', 'Borrador'),
        ('in_progress', 'En Progreso'),
        ('completed', 'Completado'),
        ('validated', 'Validado')
    ], string='Estado', default='draft', tracking=True)
    
    notes = fields.Text(string='Observaciones Generales')
    
    def action_start_control(self):
        """Start the quality control process"""
        self.state = 'in_progress'
        return True
    
    def action_complete_control(self):
        """Mark control as completed"""
        if not self.responsible_signature:
            raise ValidationError(_("Se requiere la firma del responsable para completar el control"))
        self.state = 'completed'
        return True
    
    def action_validate_control(self):
        """Validate the control (supervisor action)"""
        if not self.supervisor_signature:
            raise ValidationError(_("Se requiere la firma del supervisor para validar"))
        self.state = 'validated'
        return True
    
    def action_reset_to_draft(self):
        """Reset to draft state"""
        self.state = 'draft'
        return True