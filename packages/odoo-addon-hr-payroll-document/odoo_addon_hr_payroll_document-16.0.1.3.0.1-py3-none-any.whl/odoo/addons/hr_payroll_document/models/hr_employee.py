from odoo import _, fields, models
from odoo.exceptions import ValidationError


class Employee(models.Model):
    _inherit = "hr.employee"

    no_payroll_encryption = fields.Boolean(
        string="Disable payrolls encryption",
        help="If this is disabled (default), "
        "the PDF payrolls are encrypted using the Identification No.\n"
        "Only future payrolls are affected by this change, "
        "existing payrolls will not change their encryption status.",
    )

    def write(self, vals):
        res = super().write(vals)
        if "identification_id" in vals and not self.env["res.partner"].simple_vat_check(
            self.env.company.country_id.code, vals["identification_id"]
        ):
            raise ValidationError(_("The field identification ID is not valid"))
        return res
