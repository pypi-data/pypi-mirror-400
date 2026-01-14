import logging
from odoo import models, fields, api
from odoo.tools.translate import _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)

class NegativeDDAAOrderWizard(models.TransientModel):
    _name = "editorial.negative.ddaa.order.wizard"
    _description = "Wizard for managing negative DDAA orders."

    ddaa_order = fields.Many2one(
        comodel_name='purchase.order',
        string='DDAA Order')

    company_id = fields.Many2one('res.company', store=True, copy=False,
                                 string="Company",
                                 default=lambda self: self.env.user.company_id.id)
    currency_id = fields.Many2one('res.currency', string="Currency",
                                  related='company_id.currency_id',
                                  default=lambda self: self.env.user.company_id.currency_id.id)

    # Total amount of the ddaa_order
    amount_total = fields.Monetary(string='Importe total', store=True)

    ddaa_order_lines = fields.Many2many(
        comodel_name='purchase.order.line',
        string='DDAA Order Lines'
    )

    # sum of the distributed quantities between the order_lines
    calculated_total = fields.Monetary(string='Total calculado', compute='_compute_calculated_total', store=True)

    selection = fields.Selection(
        string='Selection',
        selection=[
            ('close_anyway', 'Cerrar el albarán de autoría liquidando el importe negativo.'),
            ('distribute_amounts', 'Distribuir el importe total y abrir un nuevo albarán de autoría.')
        ]
    )

    @api.onchange('ddaa_order')
    def _get_ddaa_order_lines(self):
        _logger.debug(f"Getting wizard ddaa order lines for DDAA Order [{self.ddaa_order.id}]")

        order_lines = self.ddaa_order.order_line
        wizard_order_lines = []
        for line in order_lines:
            if line.product_id.categ_id.id != self.env.company.product_category_ddaa_id.id:
                line_data = line.copy_data()[0]
                line_data["product_qty"] = 0
                line_data["price_unit"] = 0
                _logger.debug(f"Line data:\n{line_data}")
                wizard_order_lines.append(self.env['purchase.order.line'].new(line_data))

        self.ddaa_order_lines = [line.id for line in wizard_order_lines]

    @api.depends('ddaa_order_lines')
    def _compute_calculated_total(self):
        total = sum(line.price_total for line in self.ddaa_order_lines)
        _logger.debug(f"calculated_total={total}")
        self.calculated_total = total

    def create(self, values):
        # ToDo - Ideally this code block will be inside the function 'open_new_ddaa_order' but odoo calls the create function
        #        before the button action as part of the model auto-save functionality when the wizard is closed.
        #        As we don't want to save the order_lines, it was not possible to then access the values in the button action function.
        ddaa_order = self.env['purchase.order'].browse(values.get("ddaa_order"))

        selection = values.get("selection", None)
        _logger.debug(f"Selection: {selection}")

        if not selection:
            raise ValidationError(_("Selecciona una opción antes de confirmar."))

        if selection != "close_anyway":
            if not self.validate(values):
                _logger.debug("Validation failed")
                raise ValidationError(_("Los importes no coinciden."))

            self.close_current_ddaa_order(ddaa_order)

            order_lines = values.get("ddaa_order_lines")

            royalties_advance_id = self.env.ref("gestion_editorial.product_royalties_advance").id
            courtesy_id = self.env.ref("gestion_editorial.product_books_delivered_to_authorship").id

            for authorship in ddaa_order.partner_id.authorship_ids:
                product = authorship.product_id
                product_id = product.id

                royalties_advance_qty = 0
                royalties_advance_amount = 0
                courtesy_qty = 0
                courtesy_amount = 0
                for line in order_lines:
                    line_data = line[2]
                    if line_data.get("section_id") == product_id:
                        if line_data.get("product_id") == royalties_advance_id:
                            royalties_advance_qty = line_data.get("product_qty")
                            royalties_advance_amount = line_data.get("price_unit")
                        if line_data.get("product_id") == courtesy_id:
                            courtesy_qty = line_data.get("product_qty")
                            courtesy_amount = line_data.get("price_unit")

                _logger.debug(f"Royalties advance quantity: {royalties_advance_qty}")
                _logger.debug(f"Royalties advance amount: {royalties_advance_amount}")
                _logger.debug(f"Courtesy quantity: {courtesy_qty}")
                _logger.debug(f"Courtesy amount: {courtesy_amount}")
                new_ddaa_order = product.update_or_create_ddaa_purchase_orders(courtesy_qty=courtesy_qty, courtesy_amount=courtesy_amount, royalties_advance_qty=royalties_advance_qty, royalties_advance_amount=royalties_advance_amount)
                self.post_notes(ddaa_order, new_ddaa_order)
        else:
            self.close_current_ddaa_order(ddaa_order)

        values.pop('ddaa_order', None)
        values.pop('ddaa_order_lines', None)

        return super(NegativeDDAAOrderWizard, self).create(values)


    def validate(self, values):
        _logger.debug(f"values: {values}")
        amount_total = values.get("amount_total", None)
        calculated_total = values.get("calculated_total", None)
        _logger.debug(f"Amount total: {amount_total}")
        _logger.debug(f"Calculated total: {calculated_total}")
        return amount_total and calculated_total and amount_total == calculated_total

    def close_current_ddaa_order(self, ddaa_order):
        ddaa_order.button_confirm(validate_negative_order=False)

    def post_notes(self, previous_ddaa_order, new_ddaa_order):
        previous_ddaa_order.message_post_with_source(
            "gestion_editorial.new_ddaa_order_created",
            subtype_xmlid="mail.mt_note",
            render_values={"new_ddaa_order": new_ddaa_order},
        )

        new_ddaa_order.message_post_with_source(
            "gestion_editorial.ddaa_order_created_as_continuation_of",
            subtype_xmlid="mail.mt_note",
            render_values={"previous_ddaa_order": previous_ddaa_order},
        )

    def open_new_ddaa_order(self):
        pass