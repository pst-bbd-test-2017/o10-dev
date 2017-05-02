# -*- coding: utf-8 -*-

from odoo import fields, models


class HrTimesheetConfiguration(models.TransientModel):
    _inherit = 'project.config.settings'

    reload_after_commit = fields.Boolean(
        "Reload view after Commit entry to Timesheets")
