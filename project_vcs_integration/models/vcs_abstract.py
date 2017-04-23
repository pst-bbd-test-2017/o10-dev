# -*- coding: utf-8 -*-

from odoo import fields, models, api

# Ideas for abstraction, no included in __init__
class VCSIntegrationAbstract(models.AbstractModel):
    """Abstract model for VCS integration."""

    _name = 'vcs.integration.abstract'

    username = fields.Char()
    password = fields.Char()


class VCSUser(models.Model):
    _name = 'vcs.user'