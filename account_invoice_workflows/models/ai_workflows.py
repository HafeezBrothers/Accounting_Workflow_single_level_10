from odoo import api, fields, models,_
from odoo.exceptions import UserError

_STATES = [
    ('draft', 'Draft'),
    ('to_approve', 'To Approve'),
    ('approved', 'Approved'),
    ('rejected', 'Rejected'),
  
    ('done', 'Done')
]


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    state = fields.Selection([
            ('draft','Draft'),
            ('appr', 'Approved'),
            ('pend', 'pending'),
            ('open', 'Open'),
            ('paid', 'Paid'),
            
            ('cancel', 'Cancelled'),
        ], string='Status', index=True, readonly=True, default='draft',
        track_visibility='onchange', copy=False)

    @api.multi
    def button_appro(self):
        self.action_invoice_open()
    
    @api.multi
    def action_invoice_open(self):
        # lots of duplicate calls to action_invoice_open, so we remove those already open
        view_id = self.env.ref('account.view_account_payment_invoice_form').id
        context = dict(self.env.context or {})
        
        to_open_invoices = self.filtered(lambda inv: inv.state != 'open')
        if to_open_invoices.filtered(lambda inv: inv.state not in ['draft']):
            raise UserError(_("Invoice must be in draft or Pro-forma state in order to validate it."))
        to_open_invoices.action_date_assign()
        to_open_invoices.action_move_create()
         
         
         
        return to_open_invoices.invoice_validate()  
    
    @api.multi
    def action_invoice_paid2(self,s):
        # lots of duplicate calls to action_invoice_paid, so we remove those already paid
        to_pay_invoices = s.filtered(lambda inv: inv.state != 'pending')
#         if to_pay_invoices.filtered(lambda inv: inv.state != 'open'):
#             raise UserError(_('Invoice must be validated in order to set it to register payment.'))
#         if to_pay_invoices.filtered(lambda inv: not inv.reconciled):
#             raise UserError(_('You cannot pay an invoice which is partially paid. You need to reconcile payment entries first.'))
        return to_pay_invoices.write({'state': 'pend'})
    
    
    @api.multi
    def action_invoice_paid1(self,s):
        # lots of duplicate calls to action_invoice_paid, so we remove those already paid
        to_pay_invoices = s.filtered(lambda inv: inv.state != 'paid')
#         if to_pay_invoices.filtered(lambda inv: inv.state != 'pend'):
#             raise UserError(_('Invoice must be validated in order to set it to register payment.'))
#         if to_pay_invoices.filtered(lambda inv: not inv.reconciled):
#             raise UserError(_('You cannot pay an invoice which is partially paid. You need to reconcile payment entries first.'))
        return to_pay_invoices.write({'state': 'paid'})

    @api.multi
    def action_invoice_draft(self):
        if self.filtered(lambda inv: inv.state != 'cancel'):
            raise UserError(_("Invoice must be cancelled in order to reset it to draft."))
        # go from canceled state to draft state
        self.write({'state': 'draft', 'date': False})

