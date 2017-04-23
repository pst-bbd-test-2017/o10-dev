# -*- coding: utf-8 -*-
import github
from github import GithubException

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class GitHubUser(models.Model):
    """GitHub user model."""
    _name = 'github.user'

    username = fields.Char(string='Username')
    password = fields.Char(string='Password')

    def _get_user(self):
        client = github.Github(login_or_token=self.username, password=self.password)
        return client.get_user()


class RepositoryGitHub(models.Model):
    """GitHub repository model."""
    _name = 'repository.github'

    user_id = fields.Many2one('github.user', required=True)
    name = fields.Char(string="Name", required=True)
    main_branch = fields.Selection(selection=lambda s: s._get_branch_selection())
    branch_ids = fields.One2many('branch.github')

    @api.depends('user_id')
    def _get_branch_selection(self):
        # TODO: doesn't work
        print "get branch called"
        if self.user_id:
            branch_selection = []
            for b in self.user_id._get_user().get_repos()[0].get_branches():
                branch_selection.append(b.name, b.name)
            print branch_selection
            return branch_selection
        return [('none', 'None')]


    @api.constrains('name', 'user_id')
    def _check_repo(self):
        try:
            self.user_id._get_user().get_repo(self.name)
        except GithubException as ge:
            raise ValidationError(ge.data['message'])

    @api.model
    def create(self, vals):
        res = super(RepositoryGitHub, self).create(vals)
        print "create calledd"
        for br in self.env['github.user'].browse(vals['user_id'])[0]._get_user().get_repo(vals['name']).get_branches():
            self.env['branch.github'].create({
                'name': br.name,
                'repository_id': res.id
            })
            print "created branch"
        return res

class BranchGitHub(models.Model):
    _name = 'branch.github'

    name = fields.Char()
    repository_id = fields.Many2one('repository.github')
