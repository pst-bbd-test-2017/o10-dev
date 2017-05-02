# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class CommitAddTimesheetWizard(models.TransientModel):
    _name = "commit.add.timesheet.wizard"
    _description = "Wizard to add commit to timesheet lines."

    time_spent = fields.Float("Time Spent")

    @api.multi
    def create_timesheet_line(self):
        ctx = self._context or {}
        task_id = ctx.get('task_id')
        project_id = self.env['project.task'].browse(task_id).project_id.id
        commit_msg = ctx.get('commit_msg')
        self.env['account.analytic.line'].create({
            'task_id': task_id,
            'project_id': project_id,
            'name': commit_msg,
            'unit_amount': self.time_spent,
        })
        self.env['vcs.commit'].browse(
            ctx.get('active_id')).in_timesheets = True
        # TODO: it's quicker to enter commits into timesheets without the
        # constant reloading, but timesheets are not updated otherwise.
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }
