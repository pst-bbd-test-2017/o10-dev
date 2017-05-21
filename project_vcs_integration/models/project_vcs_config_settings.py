# -*- coding: utf-8 -*-

from odoo import fields, models


class HrTimesheetConfiguration(models.TransientModel):
    _inherit = 'project.config.settings'

    related_reload_after_commit = fields.Boolean(
        related='company_id.reload_after_commit',
        string="Reload view after Commit entry to Timesheets")

class ResCompany(models.Model):
    _inherit = 'res.company'

    reload_after_commit = fields.Boolean(
        "Reload view after Commit entry to Timesheets")
