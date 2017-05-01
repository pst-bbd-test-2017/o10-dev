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
