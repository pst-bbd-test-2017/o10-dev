# -*- coding: utf-8 -*-
import pybitbucket

from odoo import models, fields, api


class RepositoryBitbucket(models.Model):
    _name = 'repository.bitbucket'

    username = fields.Char(string='Username')
    password = fields.Char(string='Password')


    def _get_branches(self):
        pass