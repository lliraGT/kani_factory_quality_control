from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime


class QualityControlPestControlDetail(models.Model):
    _name = 'quality.control.pest.control.detail'
    _description = 'Detalle de Control de Plagas Planta KANI'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'control_date desc'

    name = fields.Char(
        string='Control Number',
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: self.env['ir.sequence'].next_by_code('quality.control.pest.control.detail')
    )
    
    control_date = fields.Date(
        string='Fecha de Control',
        default=fields.Date.context_today,
        required=True,
        tracking=True
    )
    
    responsible_id = fields.Many2one(
        'res.users',
        string='Responsable',
        required=True,
        default=lambda self: self.env.user,
        tracking=True
    )
    
    supervisor_id = fields.Many2one(
        'res.users',
        string='Supervisión',
        required=True,
        tracking=True
    )
    
    # Individual fields for ONE control entry (like your cleaning modules)
    pest_type = fields.Selection([
        ('roedor', 'Roedor'),
        ('insecto', 'Insecto'),
        ('aracnido', 'Arácnido'),
        ('otro', 'Otro'),
    ], string='Tipo de Plaga', tracking=True)
    
    location = fields.Char(
        string='Ubicación',
        help="Ubicación específica donde se encontró",
        tracking=True
    )
    
    finding_type = fields.Selection([
        ('vivo', 'Encontrado Vivo'),
        ('muerto', 'Encontrado Muerto'),
        ('rastro', 'Rastro/Evidencia'),
        ('trampa', 'En Trampa'),
    ], string='Tipo de Encontrado', tracking=True)
    
    # Additional tracking fields
    action_taken = fields.Text(
        string='Acción Tomada',
        help="Descripción de las acciones correctivas tomadas"
    )
    
    follow_up_required = fields.Boolean(
        string='Requiere Seguimiento',
        default=False,
        tracking=True
    )
    
    follow_up_date = fields.Date(
        string='Fecha de Seguimiento',
        help="Fecha programada para verificar la efectividad de las acciones"
    )
    
    # Signatures
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