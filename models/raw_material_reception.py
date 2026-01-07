from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime


class QualityControlRawMaterialReception(models.Model):
    _name = 'quality.control.raw.material.reception'
    _description = 'Control de Recepción de Materia Prima'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'reception_date desc'

    name = fields.Char(
        string='Control Number',
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: self.env['ir.sequence'].next_by_code('quality.control.raw.material.reception')
    )
    
    # SECCIÓN 1: RECEPCIÓN DEL PRODUCTO
    reception_date = fields.Date(
        string='Fecha de Recepción',
        default=fields.Date.context_today,
        required=True,
        tracking=True
    )
    
    reception_time = fields.Float(
        string='Hora de Recepción',
        help='Formato 24h (ej: 8.5 = 8:30 AM)'
    )
    
    supplier_id = fields.Many2one(
        'res.partner',
        string='Proveedor',
        domain=[('supplier_rank', '>', 0)],
        required=True,
        tracking=True
    )
    
    lot_number = fields.Char(
        string='Número de Lote',
        required=True,
        tracking=True
    )
    
    harvest_date = fields.Date(
        string='Fecha de Cosecha'
    )
    
    origin = fields.Char(
        string='Procedencia',
        help='Lugar de origen del producto'
    )
    
    invoice_reference = fields.Char(
        string='Referencia de Factura'
    )
    
    # Verificación de transporte
    transport_clean = fields.Boolean(
        string='Transporte Limpio',
        default=True
    )
    
    transport_no_odors = fields.Boolean(
        string='Sin Olores',
        default=True
    )
    
    transport_integrity = fields.Boolean(
        string='Integridad',
        default=True
    )
    
    transport_temperature = fields.Float(
        string='Temperatura del Transporte (°C)',
        help='Si aplica'
    )
    
    # SECCIÓN 2: CONTROL DE CALIDAD
    product_type = fields.Selection([
        ('tubérculos', 'Tubérculos (papa, camote, yuca, zanahoria, remolacha)'),
        ('hoja', 'Vegetales de Hoja (acelga, espinaca, lechuga, apio)'),
        ('crucíferas', 'Crucíferas (brócoli, coliflor, repollo)'),
        ('granos', 'Granos y Cereales (maíz, avena, arroz, frijol)'),
        ('legumbres', 'Legumbres Frescas (ejote, arveja, habas)'),
        ('frutas', 'Frutas'),
    ], string='Tipo de Producto', required=True)
    
    color_adequate = fields.Boolean(
        string='Color Adecuado',
        default=True,
        help='Verde intenso en vegetales, piel firme en tubérculos'
    )
    
    fresh_odor = fields.Boolean(
        string='Olor Fresco',
        default=True,
        help='NO fermentado'
    )
    
    firm_texture = fields.Boolean(
        string='Textura Firme',
        default=True
    )
    
    no_yellow_leaves = fields.Boolean(
        string='Sin Hojas Amarillas',
        default=True
    )
    
    no_black_spots = fields.Boolean(
        string='Sin Manchas Negras',
        default=True
    )
    
    no_soft_parts = fields.Boolean(
        string='Sin Partes Blandas',
        default=True
    )
    
    no_visible_fungi = fields.Boolean(
        string='Sin Hongos Visibles',
        default=True
    )
    
    no_pests = fields.Boolean(
        string='Sin Presencia de Plagas',
        default=True
    )
    
    packaging_state_ok = fields.Boolean(
        string='Estado del Empaque OK',
        default=True
    )
    
    dirt_level_acceptable = fields.Boolean(
        string='Nivel de Suciedad Aceptable',
        default=True
    )
    
    no_excess_humidity = fields.Boolean(
        string='Sin Exceso de Humedad',
        default=True
    )
    
    quality_decision = fields.Selection([
        ('approved', 'Apto'),
        ('approved_observations', 'Apto con Observaciones'),
        ('rejected', 'Rechazado')
    ], string='Decisión de Calidad', default='approved', tracking=True)
    
    quality_observations = fields.Text(
        string='Observaciones de Calidad'
    )
    
    # SECCIÓN 3: PESAJE INICIAL
    gross_weight = fields.Float(
        string='Peso Bruto (libras)',
        digits=(10, 2)
    )
    
    packaging_weight = fields.Float(
        string='Peso de Empaque/Sacos (libras)',
        digits=(10, 2)
    )
    
    net_weight = fields.Float(
        string='Peso Neto (libras)',
        compute='_compute_net_weight',
        store=True,
        digits=(10, 2)
    )
    
    @api.depends('gross_weight', 'packaging_weight')
    def _compute_net_weight(self):
        for record in self:
            record.net_weight = record.gross_weight - record.packaging_weight
    
    # SECCIÓN 4: LIMPIEZA PREVIA
    pre_cleaning_done = fields.Boolean(
        string='Limpieza Previa Realizada',
        default=False
    )
    
    damaged_leaves_removed = fields.Boolean(
        string='Hojas Dañadas Removidas',
        default=False
    )
    
    damaged_stems_removed = fields.Boolean(
        string='Tallos Dañados Removidos',
        default=False
    )
    
    dirt_removed = fields.Boolean(
        string='Tierra Gruesa Removida',
        default=False
    )
    
    decomposed_units_removed = fields.Boolean(
        string='Unidades en Descomposición Removidas',
        default=False
    )
    
    # SECCIÓN 5: LAVADO DEL PRODUCTO
    washing_required = fields.Boolean(
        string='Requiere Lavado',
        default=True
    )
    
    washing_start_time = fields.Float(
        string='Hora Inicio Lavado',
        help='Formato 24h'
    )
    
    pre_wash_weight = fields.Float(
        string='Peso Pre-Lavado (libras)',
        digits=(10, 2)
    )
    
    sanitizer_used = fields.Char(
        string='Sanitizante/Desinfectante Usado',
        help='Grado alimenticio'
    )
    
    washing_end_time = fields.Float(
        string='Hora Fin Lavado',
        help='Formato 24h'
    )
    
    post_wash_weight = fields.Float(
        string='Peso Post-Lavado (libras)',
        digits=(10, 2)
    )
    
    # SECCIÓN 6: MÉTRICAS DE CALIDAD
    waste_percentage = fields.Float(
        string='% Merma',
        compute='_compute_metrics',
        store=True,
        digits=(5, 2),
        readonly=True,
        help="Porcentaje de pérdida durante el proceso de limpieza"
    )
    
    yield_percentage = fields.Float(
        string='% Rendimiento Final',
        compute='_compute_metrics',
        store=True,
        digits=(5, 2),
        readonly=True,
        help="Porcentaje de producto utilizable después del proceso"
    )
    
    @api.depends('pre_wash_weight', 'post_wash_weight', 'net_weight')
    def _compute_metrics(self):
        for record in self:
            if record.pre_wash_weight and record.post_wash_weight:
                waste = record.pre_wash_weight - record.post_wash_weight
                record.waste_percentage = (waste / record.pre_wash_weight) if record.pre_wash_weight else 0
                record.yield_percentage = (record.post_wash_weight / record.pre_wash_weight) if record.pre_wash_weight else 0
            else:
                record.waste_percentage = 0
                record.yield_percentage = 0
    
    # SECCIÓN 7: ALMACENAMIENTO REFRIGERADO
    storage_temperature = fields.Float(
        string='Temperatura de Almacenamiento (°C)',
        help='Recomendado: 4-6°C'
    )
    
    storage_location = fields.Char(
        string='Ubicación de Almacenamiento'
    )
    
    fifo_applied = fields.Boolean(
        string='FIFO Aplicado',
        default=True,
        help='First In, First Out'
    )
    
    # SECCIÓN 8: VIDA ÚTIL
    shelf_life_days = fields.Integer(
        string='Vida Útil (días)',
        compute='_compute_shelf_life',
        store=True,
        help='Calculado según tipo de producto y si fue lavado'
    )
    
    expiry_date = fields.Date(
        string='Fecha de Vencimiento',
        compute='_compute_expiry_date',
        store=True
    )
    
    @api.depends('product_type', 'washing_required', 'reception_date')
    def _compute_shelf_life(self):
        shelf_life_map = {
            'tubérculos': {'washed': 15, 'unwashed': 37},  # Promedio 10-20 lavados, 30-45 sin lavar
            'hoja': {'washed': 6, 'unwashed': 6},  # 5-7 días
            'crucíferas': {'washed': 10, 'unwashed': 10},  # 8-12 días
            'granos': {'washed': 0, 'unwashed': 270},  # 6-12 meses (no lavar)
            'legumbres': {'washed': 7, 'unwashed': 7},  # 5-10 días
            'frutas': {'washed': 30, 'unwashed': 30},  # Variable según fruta
        }
        
        for record in self:
            if record.product_type:
                wash_status = 'washed' if record.washing_required else 'unwashed'
                record.shelf_life_days = shelf_life_map.get(record.product_type, {}).get(wash_status, 0)
            else:
                record.shelf_life_days = 0
    
    @api.depends('reception_date', 'shelf_life_days')
    def _compute_expiry_date(self):
        from datetime import timedelta
        for record in self:
            if record.reception_date and record.shelf_life_days:
                record.expiry_date = record.reception_date + timedelta(days=record.shelf_life_days)
            else:
                record.expiry_date = False
    
    # Personal
    reception_responsible_id = fields.Many2one(
        'res.users',
        string='Encargado de Recepción',
        required=True,
        default=lambda self: self.env.user,
        tracking=True
    )
    
    quality_responsible_id = fields.Many2one(
        'res.users',
        string='Responsable de Control de Calidad',
        tracking=True
    )
    
    supervisor_id = fields.Many2one(
        'res.users',
        string='Supervisor de Planta',
        required=True,
        tracking=True
    )
    
    # Firmas
    reception_signature = fields.Binary(
        string='Firma Encargado de Recepción',
        attachment=True
    )
    
    quality_signature = fields.Binary(
        string='Firma Control de Calidad',
        attachment=True
    )
    
    supervisor_signature = fields.Binary(
        string='Firma Supervisor',
        attachment=True
    )
    
    # Estado
    state = fields.Selection([
        ('draft', 'Borrador'),
        ('reception', 'En Recepción'),
        ('quality_check', 'Control de Calidad'),
        ('processing', 'En Procesamiento'),
        ('storage', 'Almacenado'),
        ('completed', 'Completado'),
        ('rejected', 'Rechazado')
    ], string='Estado', default='draft', tracking=True)
    
    notes = fields.Text(string='Observaciones Generales')
    
    # Métodos de workflow
    def action_start_reception(self):
        """Iniciar proceso de recepción"""
        self.state = 'reception'
        return True
    
    def action_quality_check(self):
        """Pasar a control de calidad"""
        if not self.reception_signature:
            raise ValidationError(_("Se requiere la firma del encargado de recepción"))
        self.state = 'quality_check'
        return True
    
    def action_start_processing(self):
        """Iniciar procesamiento (limpieza/lavado)"""
        if not self.quality_signature:
            raise ValidationError(_("Se requiere la firma del control de calidad"))
        if self.quality_decision == 'rejected':
            raise ValidationError(_("No se puede procesar un producto rechazado"))
        self.state = 'processing'
        return True
    
    def action_move_to_storage(self):
        """Mover a almacenamiento"""
        self.state = 'storage'
        return True
    
    def action_complete(self):
        """Completar el control"""
        if not self.supervisor_signature:
            raise ValidationError(_("Se requiere la firma del supervisor para completar"))
        self.state = 'completed'
        return True
    
    def action_reject(self):
        """Rechazar el producto"""
        self.state = 'rejected'
        self.quality_decision = 'rejected'
        return True
    
    def action_reset_to_draft(self):
        """Resetear a borrador"""
        self.state = 'draft'
        return True