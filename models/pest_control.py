from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime


class QualityControlPestControl(models.Model):
    _name = 'quality.control.pest.control'
    _description = 'Control de Plagas Planta KANI'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'control_date desc'

    name = fields.Char(
        string='Control Number',
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: self.env['ir.sequence'].next_by_code('quality.control.pest.control')
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
    
    # Pest Control Lines (for each location)
    pest_control_line_ids = fields.One2many(
        'quality.control.pest.control.line',
        'pest_control_id',
        string='Líneas de Control'
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
    
    @api.model
    def create(self, vals):
        """Create default location lines when creating a new control"""
        record = super().create(vals)
        # Only create default lines if no lines were provided
        if not record.pest_control_line_ids:
            record._create_default_lines()
        return record
    
    def _create_default_lines(self):
        """Create default lines for all standard locations"""
        default_locations = [
            ('Comedor', 'A-01'),
            ('Comedor', 'A-02'),
            ('Pila', 'B-01'),
            ('Cocina', 'B-02'),
            ('Ingreso IG', 'B-03'),
            ('Galvano IG', 'B-04'),
            ('Pulido IG', 'B-05'),
            ('Centro IG', 'B-06'),
            ('Moldes IG', 'B-07'),
            ('Pasillo Desh', 'C-01'),
            ('Desh', 'C-02'),
            ('Taller', 'C-03'),
            ('Bodega Granos', 'L-01'),
        ]
        
        line_vals = []
        for location, code in default_locations:
            line_vals.append({
                'pest_control_id': self.id,
                'location': location,
                'code': code,
                'cleanliness_ok': True,  # Default to clean
                'trap_consumption': 'sc',  # Default to no consumption
            })
        
        # Create all lines in batch for better performance
        if line_vals:
            self.env['quality.control.pest.control.line'].create(line_vals)
    
    def action_create_default_lines(self):
        """Manual action to create default lines if they don't exist"""
        if not self.pest_control_line_ids:
            self._create_default_lines()
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Líneas Creadas'),
                'message': _('Se han creado las líneas de control por defecto para todas las ubicaciones.'),
                'type': 'success',
            }
        }
    
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


class QualityControlPestControlLine(models.Model):
    _name = 'quality.control.pest.control.line'
    _description = 'Línea de Control de Plagas'
    _order = 'sequence, code'

    pest_control_id = fields.Many2one(
        'quality.control.pest.control',
        string='Control de Plagas',
        required=True,
        ondelete='cascade'
    )
    
    sequence = fields.Integer(
        string='Secuencia',
        default=10,
        help="Usado para ordenar las líneas"
    )
    
    location = fields.Selection([
        ('Comedor', 'Comedor'),
        ('Pila', 'Pila'),
        ('Cocina', 'Cocina'),
        ('Ingreso IG', 'Ingreso IG'),
        ('Galvano IG', 'Galvano IG'),
        ('Pulido IG', 'Pulido IG'),
        ('Centro IG', 'Centro IG'),
        ('Moldes IG', 'Moldes IG'),
        ('Pasillo Desh', 'Pasillo Desh'),
        ('Desh', 'Desh'),
        ('Taller', 'Taller'),
        ('Bodega Granos', 'Bodega Granos'),
    ], string='Ubicación', required=True)
    
    code = fields.Selection([
        ('A-01', 'A-01'),
        ('A-02', 'A-02'),
        ('B-01', 'B-01'),
        ('B-02', 'B-02'),
        ('B-03', 'B-03'),
        ('B-04', 'B-04'),
        ('B-05', 'B-05'),
        ('B-06', 'B-06'),
        ('B-07', 'B-07'),
        ('C-01', 'C-01'),
        ('C-02', 'C-02'),
        ('C-03', 'C-03'),
        ('L-01', 'L-01'),
    ], string='Código', required=True)
    
    cleanliness_ok = fields.Boolean(
        string='Limpieza OK',
        default=True,
        help="Indica si la limpieza en esta ubicación está correcta"
    )
    
    trap_consumption = fields.Selection([
        ('sc', 'SC - Sin Consumo'),
        ('cc', 'CC - Consumo Completo'),
        ('cc_plus', 'CC+ - Consumo superior al 30%')
    ], string='Consumo de Trampa', default='sc', required=True)
    
    observations = fields.Text(string='Observaciones')
    
    @api.onchange('location')
    def _onchange_location(self):
        """Auto-fill code based on location selection"""
        location_code_map = {
            'Comedor': ['A-01', 'A-02'],
            'Pila': ['B-01'],
            'Cocina': ['B-02'],
            'Ingreso IG': ['B-03'],
            'Galvano IG': ['B-04'],
            'Pulido IG': ['B-05'],
            'Centro IG': ['B-06'],
            'Moldes IG': ['B-07'],
            'Pasillo Desh': ['C-01'],
            'Desh': ['C-02'],
            'Taller': ['C-03'],
            'Bodega Granos': ['L-01'],
        }
        
        if self.location and self.location in location_code_map:
            available_codes = location_code_map[self.location]
            if len(available_codes) == 1:
                # If only one code available, set it automatically
                self.code = available_codes[0]
            else:
                # If multiple codes (like Comedor), clear the code to let user choose
                self.code = False
    
    @api.constrains('location', 'code')
    def _check_location_code_combination(self):
        """Validate that the location and code combination is correct"""
        valid_combinations = {
            'Comedor': ['A-01', 'A-02'],
            'Pila': ['B-01'],
            'Cocina': ['B-02'],
            'Ingreso IG': ['B-03'],
            'Galvano IG': ['B-04'],
            'Pulido IG': ['B-05'],
            'Centro IG': ['B-06'],
            'Moldes IG': ['B-07'],
            'Pasillo Desh': ['C-01'],
            'Desh': ['C-02'],
            'Taller': ['C-03'],
            'Bodega Granos': ['L-01'],
        }
        
        for record in self:
            if record.location and record.code:
                if record.code not in valid_combinations.get(record.location, []):
                    raise ValidationError(
                        _('El código %s no es válido para la ubicación %s') % 
                        (record.code, record.location)
                    )
    
    _sql_constraints = [
        ('unique_code_per_control', 'unique(pest_control_id, code)', 
         'El código debe ser único por control!')
    ]