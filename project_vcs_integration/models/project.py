# -*- coding: utf-8 -*-

from odoo import fields, models, api


class Project(models.Model):
    """Extend with VCS integration."""
    _inherit = 'project.project'

    repository_id = fields.Many2one(
        'vcs.repository', string="Repository")


class ProjectTask(models.Model):
    _inherit = 'project.task'

    related_repository_id = fields.Many2one(
        'vcs.repository', related='project_id.repository_id'
    )
    # TODO: continue, make branch field with domain of project repo
    branch_id = fields.Many2one(
        'vcs.branch',
        string='Branch',
        # domain=[('repository_id.id', '=', 'related_repository_id.id')]
    )
    related_pull_request = fields.Char(related='branch_id.pull_request')
    related_pull_request_url = fields.Char(
        string="Pull Request URL",
        related='branch_id.pull_request_link'
    )


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    commit_sha = fields.Char()

    @api.onchange('project_id')
    def onchange_project_id(self):
        """Override to allow setting task_id from context."""
        if self.task_id:
            if self.task_id.project_id != self.project_id:
                self.task_id = False

    @api.onchange('task_id')
    def onchange_task_id(self):
        if self.task_id.branch_id.commit_id:
            self.name = self.task_id.branch_id.commit_id.name.split('\n')[0]