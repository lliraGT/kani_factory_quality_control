# models/recurring_task.py
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta


class QualityControlRecurringTask(models.Model):
    _name = 'quality.control.recurring.task'
    _description = 'Configuración de Tareas Recurrentes para Control de Calidad'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'

    name = fields.Char(
        string='Nombre de Configuración',
        required=True,
        tracking=True
    )
    
    description = fields.Text(
        string='Descripción',
        help='Descripción de la tarea recurrente'
    )
    
    # Task configuration
    task_type = fields.Selection([
        ('cleaning_control', 'Control de Limpieza de Cuarto Refrigerado'),
        ('vegetable_pallet_cleaning', 'Control de Limpieza de Palets de Verdura'),
        ('pediluvios_control', 'Control y Aplicación de Sterbac para Pediluvios'),
        ('pest_control', 'Control de Plagas Planta KANI'),
        ('pest_control_detail', 'Detalle de Control de Plagas Planta KANI')
    ], string='Tipo de Control', required=True, default='cleaning_control')
    
    # Recurrence configuration
    recurrence_type = fields.Selection([
        ('daily', 'Diario'),
        ('weekly', 'Semanal'),
        ('monthly', 'Mensual')
    ], string='Frecuencia', required=True, tracking=True)
    
    # For weekly recurrence
    weekday = fields.Selection([
        ('0', 'Lunes'),
        ('1', 'Martes'),
        ('2', 'Miércoles'),
        ('3', 'Jueves'),
        ('4', 'Viernes'),
        ('5', 'Sábado'),
        ('6', 'Domingo')
    ], string='Día de la Semana', 
    help='Solo aplica para frecuencia semanal')
    
    # For monthly recurrence
    day_of_month = fields.Integer(
        string='Día del Mes', 
        help='Solo aplica para frecuencia mensual (1-31)',
        default=1
    )
    
    # Time configuration
    reminder_time = fields.Float(
        string='Hora de Recordatorio',
        default=8.0,
        help='Hora del día para crear el recordatorio (formato 24h, ej: 8.5 = 8:30 AM)'
    )
    
    # User assignments
    assigned_user_ids = fields.Many2many(
        'res.users',
        'quality_recurring_task_user_rel',
        'task_id', 'user_id',
        string='Usuarios Asignados',
        required=True,
        help='Usuarios que recibirán las tareas automáticamente'
    )
    
    # Status and dates
    active = fields.Boolean(
        string='Activo',
        default=True,
        tracking=True
    )
    
    start_date = fields.Date(
        string='Fecha de Inicio',
        default=fields.Date.context_today,
        required=True,
        tracking=True
    )
    
    end_date = fields.Date(
        string='Fecha de Fin',
        help='Opcional: fecha hasta la cual generar tareas'
    )
    
    last_generated_date = fields.Date(
        string='Última Fecha Generada',
        readonly=True,
        help='Última fecha en que se generó una tarea'
    )
    
    # Statistics
    total_tasks_generated = fields.Integer(
        string='Total de Tareas Generadas',
        readonly=True,
        default=0
    )
    
    # Configuration fields
    task_title_template = fields.Char(
        string='Plantilla de Título',
        default='Control de Limpieza - {date}',
        required=True,
        help='Plantilla para el título de la tarea. Use {date} para incluir la fecha'
    )
    
    task_description_template = fields.Text(
        string='Plantilla de Descripción',
        default='Recordatorio: Completar el control de limpieza del cuarto refrigerado y pallets para el día {date}.',
        help='Plantilla para la descripción de la tarea. Use {date} para incluir la fecha'
    )
    
    days_before_due = fields.Integer(
        string='Días de Anticipación',
        default=0,
        help='Días antes de la fecha objetivo para crear la tarea'
    )
    
    days_to_generate_ahead = fields.Integer(
        string='Días a Generar por Adelantado',
        default=7,
        help='Cuando se generen tareas manualmente, cuántos días hacia el futuro generar'
    )

    @api.constrains('weekday', 'recurrence_type')
    def _check_weekday_for_weekly(self):
        for record in self:
            if record.recurrence_type == 'weekly' and not record.weekday:
                raise ValidationError(_('Debe seleccionar un día de la semana para frecuencia semanal'))

    @api.constrains('day_of_month', 'recurrence_type')
    def _check_day_of_month(self):
        for record in self:
            if record.recurrence_type == 'monthly':
                if not record.day_of_month or record.day_of_month < 1 or record.day_of_month > 31:
                    raise ValidationError(_('El día del mes debe estar entre 1 y 31'))

    @api.constrains('start_date', 'end_date')
    def _check_dates(self):
        for record in self:
            if record.end_date and record.start_date > record.end_date:
                raise ValidationError(_('La fecha de fin debe ser posterior a la fecha de inicio'))

    @api.constrains('reminder_time')
    def _check_reminder_time(self):
        for record in self:
            if record.reminder_time < 0 or record.reminder_time >= 24:
                raise ValidationError(_('La hora debe estar entre 0.0 y 23.59'))

    def _get_custom_activity_type(self):
        """Get or create a custom activity type with KANI icon"""
        activity_type = self.env['mail.activity.type'].search([
            ('name', '=', 'KANI Control de Calidad')
        ], limit=1)
        
        if not activity_type:
            # Fallback to creating if not found in data file
            activity_type = self.env['mail.activity.type'].create({
                'name': 'KANI Control de Calidad',
                'summary': 'Control de Calidad KANI',
                'icon': 'fa-industry',  # Use industry icon which we'll override with CSS
                'category': 'default',
                'delay_count': 0,
                'delay_unit': 'days',
                'delay_from': 'current_date',
            })
        
        return activity_type

    def _calculate_next_date(self, from_date):
        """Calculate the next date based on recurrence configuration"""
        if self.recurrence_type == 'daily':
            return from_date + timedelta(days=1)
        
        elif self.recurrence_type == 'weekly':
            # Find next occurrence of the specified weekday
            days_ahead = int(self.weekday) - from_date.weekday()
            if days_ahead <= 0:  # Target day already happened this week
                days_ahead += 7
            return from_date + timedelta(days=days_ahead)
        
        elif self.recurrence_type == 'monthly':
            # Next month, same day
            try:
                next_month = from_date + relativedelta(months=1)
                return next_month.replace(day=self.day_of_month)
            except ValueError:
                # Handle cases like day 31 in February
                next_month = from_date + relativedelta(months=1)
                # Use the last day of the month if the specified day doesn't exist
                next_month_last_day = (next_month + relativedelta(months=1) - timedelta(days=1)).day
                day_to_use = min(self.day_of_month, next_month_last_day)
                return next_month.replace(day=day_to_use)

    def _create_task_for_user(self, user, target_date):
        """Create a task/activity for a specific user and date"""
        task_title = self.task_title_template.format(
            date=target_date.strftime('%d/%m/%Y')
        )
        task_description = self.task_description_template.format(
            date=target_date.strftime('%d/%m/%Y')
        )
        
        # Get custom activity type with KANI branding
        custom_activity_type = self._get_custom_activity_type()
        
        # Create activity (task) for the user
        activity_vals = {
            'activity_type_id': custom_activity_type.id,  # Use custom activity type instead of default
            'summary': task_title,
            'note': task_description,
            'date_deadline': target_date,
            'user_id': user.id,
            'res_model_id': self.env['ir.model']._get('quality.control.recurring.task').id,
            'res_id': self.id,
        }
        
        activity = self.env['mail.activity'].create(activity_vals)
        
        # Log the creation
        self.message_post(
            body=_('Tarea creada para %s: %s (fecha límite: %s)') % (
                user.name, task_title, target_date.strftime('%d/%m/%Y')
            ),
            message_type='notification'
        )
        
        return activity

    def generate_pending_tasks(self):
        """Generate all pending tasks up to today"""
        today = fields.Date.context_today(self)
        
        for record in self.filtered('active'):
            if record.end_date and today > record.end_date:
                continue  # Skip expired configurations
            
            # Determine the starting date for generation
            if record.last_generated_date:
                # Start from the next date after the last generated
                start_from = record._calculate_next_date(record.last_generated_date)
            else:
                # First time generation - start from start_date
                start_from = record.start_date
            
            current_date = start_from
            generated_count = 0
            
            # Generate tasks up to a reasonable future limit
            generation_limit = today + timedelta(days=max(record.days_before_due, 7))
            
            while current_date <= generation_limit:
                # Check if we should stop due to end_date
                if record.end_date and current_date > record.end_date:
                    break
                
                # Calculate when to create the task (considering anticipation)
                task_creation_date = current_date - timedelta(days=record.days_before_due)
                
                # Only create if the creation date is today or in the past
                if task_creation_date <= today:
                    # Check if tasks already exist for this date to avoid duplicates
                    existing_activities = self.env['mail.activity'].search([
                        ('res_model', '=', record._name),
                        ('res_id', '=', record.id),
                        ('date_deadline', '=', current_date),
                        ('user_id', 'in', record.assigned_user_ids.ids)
                    ])
                    
                    if not existing_activities:
                        # Create tasks for all assigned users
                        for user in record.assigned_user_ids:
                            record._create_task_for_user(user, current_date)
                        
                        generated_count += 1
                        record.last_generated_date = current_date
                        
                        # Log generation with more detail
                        record.message_post(
                            body=_('Se generaron %d tareas para la fecha %s') % (
                                len(record.assigned_user_ids), 
                                current_date.strftime('%d/%m/%Y')
                            ),
                            message_type='notification'
                        )
                    else:
                        # Tasks already exist, just update the last generated date
                        record.last_generated_date = current_date
                
                # Calculate next date
                current_date = record._calculate_next_date(current_date)
                
                # Safety break to avoid infinite loops
                if generated_count > 50:
                    break
            
            # Update statistics
            if generated_count > 0:
                record.total_tasks_generated += generated_count

    @api.model
    def _cron_generate_tasks(self):
        """Cron job to automatically generate pending tasks"""
        active_configs = self.search([('active', '=', True)])
        active_configs.generate_pending_tasks()

    def action_generate_tasks_now(self):
        """Manual action to generate tasks immediately with detailed feedback"""
        today = fields.Date.context_today(self)
        
        # Debug information
        debug_info = []
        tasks_created = 0
        
        for record in self.filtered('active'):
            debug_info.append(f"Procesando configuración: {record.name}")
            debug_info.append(f"Última fecha generada: {record.last_generated_date}")
            debug_info.append(f"Fecha de inicio: {record.start_date}")
            debug_info.append(f"Frecuencia: {record.recurrence_type}")
            debug_info.append(f"Días a generar por adelantado: {record.days_to_generate_ahead}")
            
            # Determine starting point
            if record.last_generated_date:
                current_date = record._calculate_next_date(record.last_generated_date)
                debug_info.append(f"Próxima fecha calculada: {current_date}")
            else:
                current_date = record.start_date
                debug_info.append(f"Primera generación desde: {current_date}")
            
            # Generate multiple tasks ahead
            generation_limit = today + timedelta(days=record.days_to_generate_ahead)
            debug_info.append(f"Generando hasta: {generation_limit}")
            
            generated_this_run = 0
            while current_date <= generation_limit and generated_this_run < 10:  # Safety limit
                # Check if we should stop due to end_date
                if record.end_date and current_date > record.end_date:
                    debug_info.append(f"Detenido por fecha de fin: {record.end_date}")
                    break
                
                # Check for existing activities for this date
                existing_activities = self.env['mail.activity'].search([
                    ('res_model', '=', record._name),
                    ('res_id', '=', record.id),
                    ('date_deadline', '=', current_date),
                    ('user_id', 'in', record.assigned_user_ids.ids)
                ])
                
                if not existing_activities:
                    # Create tasks for all assigned users
                    for user in record.assigned_user_ids:
                        activity = record._create_task_for_user(user, current_date)
                        if activity:
                            tasks_created += 1
                    
                    generated_this_run += 1
                    record.last_generated_date = current_date
                    debug_info.append(f"✓ Creadas {len(record.assigned_user_ids)} tareas para {current_date}")
                else:
                    debug_info.append(f"⚠ Ya existen {len(existing_activities)} tareas para {current_date}")
                
                # Calculate next date
                current_date = record._calculate_next_date(current_date)
            
            # Update statistics
            if generated_this_run > 0:
                record.total_tasks_generated += generated_this_run * len(record.assigned_user_ids)
                debug_info.append(f"Total generado en esta ejecución: {generated_this_run * len(record.assigned_user_ids)} tareas")
        
        # Show detailed message
        if tasks_created > 0:
            message = f"✓ Se crearon {tasks_created} tareas correctamente."
        else:
            message = "⚠ No se crearon nuevas tareas. Revisa la configuración o verifica si ya existen tareas para las próximas fechas."
        
        # Add debug info for administrators
        if self.env.user.has_group('base.group_system'):
            message += f"\n\nInformación de depuración:\n" + "\n".join(debug_info)
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Generación de Tareas'),
                'message': message,
                'type': 'success' if tasks_created > 0 else 'warning',
                'sticky': True,
            }
        }

    def action_reset_generation_status(self):
        """Reset the last generated date to allow manual re-generation"""
        self.last_generated_date = False
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Estado Reiniciado'),
                'message': _('El estado de generación ha sido reiniciado. Ahora puedes generar tareas desde la fecha de inicio.'),
                'type': 'success',
            }
        }

    def action_view_generated_activities(self):
        """View all activities generated by this configuration"""
        return {
            'name': _('Tareas Generadas'),
            'type': 'ir.actions.act_window',
            'res_model': 'mail.activity',
            'view_mode': 'tree,form',
            'domain': [
                ('res_model', '=', self._name),
                ('res_id', '=', self.id)
            ],
            'context': {'default_res_model': self._name, 'default_res_id': self.id}
        }