# -*- coding: utf-8 -*-

from odoo import fields, models, api


class Project(models.Model):
    """Extend with VCS integration."""
    _inherit = 'project.project'

    repository_id = fields.Reference(
        string='Repository',
        selection=[('repository.github', 'GitHub')]
    )


class ProjectTask(models.Model):
    _inherit = 'project.task'

    # repository_id = fields.Many2one(
    #     'repository.github', related='project_id.repository_id')
    # TODO: continue, make branch field with domain of project repo
    branch_id = fields.Reference(
        string='Branch',
        selection=[('branch.github', 'GitHub')]
    )
