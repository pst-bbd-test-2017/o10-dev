# -*- coding: utf-8 -*-
import github
from pybitbucket import bitbucket, auth as bb_auth
from pybitbucket.repository import Repository as bb_repo
from pybitbucket.commit import Commit as bb_commit
from pybitbucket.ref import Branch as bb_branch
from pybitbucket.pullrequest import PullRequest as bb_pr
from pybitbucket.bitbucket import HTTPError as bb_http_err
from github import GithubException

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

VCS_TYPE_SELECTION = [
    ('github', 'GitHub'),
    ('bitbucket', 'Bitbucket'),
]


class VCSUser(models.Model):
    """VCS user model."""
    _name = 'vcs.user'

    name = fields.Char(string="Name")
    username = fields.Char(string="Username", required=True)
    password = fields.Char(string="Password", copy=False)
    type = fields.Selection(
        string="Type",
        selection=VCS_TYPE_SELECTION,
        required=True,
    )

    def _get_user(self):
        """Return user/client object from API."""
        if self.type == 'github':
            if not self.password:
                client = github.Github(
                    login_or_token=self.username)
            else:
                client = github.Github(
                    login_or_token=self.username, password=self.password)
            return client.get_user()
        elif self.type == 'bitbucket':
            return bitbucket.Client(
                bb_auth.BasicAuthenticator(
                    username=self.username,
                    password=self.password,
                    client_email='pybitbucket@mailinator.com',
                ))


class VCSRepository(models.Model):
    """VCS repository model."""
    _name = 'vcs.repository'

    user_id = fields.Many2one('vcs.user', string="VCS User", required=True)
    name = fields.Char(string="Name", required=True)
    related_type = fields.Selection(
        string="Type",
        selection=VCS_TYPE_SELECTION,
        related='user_id.type',
        readonly=True,
        store=True
    )
    branch_ids = fields.One2many(
        'vcs.branch',
        'repository_id',
        readonly=True,
    )
    owner = fields.Char(string="Owner")

    @api.onchange('user_id')
    def _onchange_user_id(self):
        """Set repository owner to username."""
        if self.user_id:
            self.owner = self.user_id.username

    @api.one
    @api.constrains('name', 'user_id', 'related_type', 'owner')
    def _check_repo(self):
        """Check if the repository exists on the hosting site."""
        if self.related_type == 'github':
            try:
                self.user_id._get_user().get_repo(self.name)
            except GithubException as ge:
                raise ValidationError(ge.data['message'])
        elif self.related_type == 'bitbucket':
            try:
                return bb_repo.find_repository_by_name_and_owner(
                    self.name.lower(),
                    owner=self.owner,
                    client=self.user_id._get_user()
                )
            except bb_http_err as http_err:
                raise ValidationError(http_err.message)

    @api.one
    def _get_repo(self):
        """Get repository object from API."""
        if self.related_type == 'github':
            try:
                # Returns as a list with 1 element
                return self.user_id._get_user().get_repo(self.name)
            except GithubException as ge:
                raise ValidationError(ge.data['message'])
        elif self.related_type == 'bitbucket':
            return bb_repo.find_repository_by_name_and_owner(
                self.name,
                owner=self.owner,
                client=self.user_id._get_user()
            )
        else:
            raise NotImplementedError

    @api.one
    def action_update(self):
        """Update repository data (branches)."""
        if self.related_type == 'github':
            local_branches = [br.name for br in self.branch_ids]
            remote_branches = []
            for b in self._get_repo()[0].get_branches():
                remote_branches.append(b.name)
                if b.name not in local_branches:
                    print b.name
                    br_res = self.env['vcs.branch'].create({
                        'name': b.name,
                        'repository_id': self.id
                    })
                    self.branch_ids = [(4, br_res.id)]
            for br in self.branch_ids:
                if br.name not in remote_branches:
                    br.unlink()
                else:
                    br.action_update()
        elif self.related_type == 'bitbucket':
            local_branches = [br.name for br in self.branch_ids]
            remote_branches = []
            for b in bb_branch.find_branches_in_repository(
                    self.name.lower(),
                    owner=self.owner,
                    client=self.user_id._get_user()
            ):
                remote_branches.append(b.name)
                if b.name not in local_branches:
                    br_res = self.env['vcs.branch'].create({
                        'name': b.name,
                        'repository_id': self.id
                    })
                    self.branch_ids = [(4, br_res.id)]
            for br in self.branch_ids:
                if br.name not in remote_branches:
                    br.unlink()
                else:
                    br.action_update()

    @api.model
    def create(self, vals):
        """Extend to create related branches."""
        res = super(VCSRepository, self).create(vals)
        if res.related_type == 'github':
            for br in res.user_id._get_user().get_repo(vals['name']).get_branches():
                br_res = self.env['vcs.branch'].create({
                    'name': br.name,
                    'repository_id': res.id,
                })
                res.branch_ids = [(4, br_res.id)]
        elif res.related_type == 'bitbucket':
            for b in bb_branch.find_branches_in_repository(
                    res.name.lower(),
                    owner=res.owner,
                    client=res.user_id._get_user()
            ):
                br_res = self.env['vcs.branch'].create({
                    'name': b.name,
                    'repository_id': res.id
                })
                res.branch_ids = [(4, br_res.id)]
        res.action_update()
        return res


class VCSBranch(models.Model):
    """Branch model."""
    _name = 'vcs.branch'

    name = fields.Char()
    repository_id = fields.Many2one(
        'vcs.repository',
        required=True,
        ondelete='cascade',
    )
    related_type = fields.Selection(
        string="Type",
        selection=VCS_TYPE_SELECTION,
        related='repository_id.related_type',
        readonly=True,
        store=True
    )
    commit_id = fields.Many2one(
        'vcs.commit',
        string="Latest Commit",
        readonly=True,
    )
    related_commit_author = fields.Char(
        related='commit_id.author',
        readonly=True
    )
    related_commit_sha_string = fields.Char(
        related='commit_id.sha_string',
        readonly=True
    )
    commit_ids = fields.Many2many('vcs.commit', 'branch_ids', readonly=True)
    pull_request = fields.Char(string="Pull Request", readonly=True)
    pull_request_link = fields.Char(
        string="Link to Pull Request", readonly=True)

    # TODO: branches in bitbucket are Ref (base type for tag and branch)
    @api.one
    def _get_branch(self):
        if self.related_type == 'github':
            try:
                # TODO: figure out why get_repo returns a list
                return self.repository_id._get_repo()[0].get_branch(self.name)
            except GithubException as ge:
                raise ValidationError(ge.data['message'])
        elif self.related_type == 'bitbucket':
            try:
                return bb_branch.find_branch_by_ref_name_in_repository(
                    self.name,
                    self.repository_id.name.lower(),
                    owner=self.repository_id.owner,
                    client=self.repository_id.user_id._get_user(),
                )
            except Exception as e:
                raise ValidationError(e)
        raise NotImplementedError

    @api.one
    def _get_commits(self, count=5):
        """Get latest commits on branch."""
        if self.related_type == 'github':
            try:
                commit_list = []
                # TODO: get_branch returns a list, why?
                for i, commit in enumerate(self._get_branch()[0].get_commits()):
                    if i > count:
                        break
                    commit_list.append(commit)
                    return commit_list
            except GithubException as ge:
                raise ValidationError(ge.data['message'])
        elif self.related_type == 'bitbucket':
            # TODO: this is a generator object of ALL commits on that branch
            commit_list = []
            for i, commit in enumerate(self._get_branch()[0].commits()):
                if i > count:
                    break
                commit_list.append(commit)
            return commit_list
        raise NotImplementedError

    @api.one
    def _get_pr(self):
        """Return Pull Request if it exists, False otherwise."""
        if self.related_type == 'github':
            try:
                for pr in self.repository_id._get_repo()[0].get_pulls():
                    # TODO: returning in for loop causes the pr to be wrapped
                    # in a list
                    if pr.head.ref == self.name:
                        return pr
                return False
            except GithubException as ge:
                raise ValidationError(ge.data['message'])
        elif self.related_type == 'bitbucket':
            prs = bb_pr.find_pullrequests_for_repository_by_state(
                self.repository_id.name.lower(),
                owner=self.repository_id.owner,
                client=self.repository_id.user_id._get_user(),
                state='OPEN'
            )
            for pr in prs:
                if hasattr(pr, 'source') and pr.source['branch']['name'] == self.name:
                    return pr
            return False
        raise NotImplementedError

    @api.one
    def action_update(self):
        """Update with pull request data."""
        pr = self._get_pr()
        if self.related_type == 'github':
            if pr[0]:
                self.pull_request = pr[0].title
                self.pull_request_link = pr[0]._rawData['_links']['html']['href']
                commits = pr[0].get_commits()
                for commit in commits:
                    commit_list = self.env['vcs.commit'].search([
                        ('sha_string', '=', commit.sha),
                        ('type', '=', 'github')
                    ])
                    if not commit_list:
                        vcs_commit = self.env['vcs.commit'].create({
                            'sha_string': commit.sha,
                            'type': 'github',
                            'branch_ids': [(4, self.id)],
                            'author': commit.raw_data['commit']['author']['name'],
                            'name': commit.raw_data['commit']['message'],
                            'date': fields.Date.from_string(
                                commit.raw_data['commit']['author']['date']),
                            'url': commit._html_url.value,
                        })
                        self.commit_ids = [(4, vcs_commit.id)]
                    else:
                        self.commit_ids = [(4, commit_list[0].id)]
            else:
                self.pull_request = "No pull requests"
            commit = self._get_branch()[0].commit
            commits = self.env['vcs.commit'].search([
                ('sha_string', '=', commit.sha),
                ('type', '=', 'github'),
            ])
            if commits and self.id not in commits[0].branch_ids.ids:
                commits[0].branch_ids = [(4, self.id)]
            if not commits:
                vcs_commit = self.env['vcs.commit'].create({
                    'sha_string': commit.sha,
                    'type': 'github',
                    'branch_ids': [(4, self.id)],
                    'author': commit.raw_data['commit']['author']['name'],
                    'name': commit.raw_data['commit']['message'],
                    'date': fields.Date.from_string(
                        commit.raw_data['commit']['author']['date']),
                    'url': commit._html_url.value,
                })
                self.commit_id = vcs_commit.id
            else:
                self.commit_id = commits[0].id
        elif self.related_type == 'bitbucket':
            # TODO: implement for bitbucket
            if pr[0]:
                self.pull_request = pr[0].title
                self.pull_request_link = pr[0].links['html']['href']
            else:
                self.pull_request = "No pull requests"
            # Bitbucket does not require a PR to get branch commits
            # TODO: The list of commits is wrapped inside another list
            commits = self._get_commits()[0]
            for commit in commits:
                commit_list = self.env['vcs.commit'].search([
                    ('sha_string', '=', commit.hash),
                    ('type', '=', 'bitbucket')
                ])
                if not commit_list:
                    vcs_commit = self.env['vcs.commit'].create({
                        'sha_string': commit.hash,
                        'branch_ids': [(4, self.id)],
                        'type': 'bitbucket',
                        'author': commit.author.display_name,
                        'name': commit.message,
                        'date': fields.Date.from_string(commit.date),
                        'url': commit.links['html']['href'],
                    })
                    self.commit_ids = [(4, vcs_commit.id)]
                else:
                    self.commit_ids = [(4, commit_list[0].id)]
            self.commit_id = sorted(
                self.commit_ids, key=lambda x: x.date, reverse=True)[0]


class VCSCommit(models.Model):
    """Commit model."""
    _name = 'vcs.commit'

    _order = 'date desc'

    name = fields.Text()
    sha_string = fields.Char(string="SHA")
    type = fields.Selection(selection=VCS_TYPE_SELECTION)
    branch_ids = fields.Many2many('vcs.branch', ondelete='cascade')
    author = fields.Char(string="Author")
    date = fields.Date(string="Commit Date")
    url = fields.Char(string="URL")
    in_timesheets = fields.Boolean()

    @api.multi
    def to_timesheet(self):
        task_id = self._context.get('task_id')
        return {
            'name': _('Add to TS'),
            'type': 'ir.actions.act_window',
            'res_model': 'commit.add.timesheet.wizard',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'commit_id': self.id,
                'commit_msg': self.name.split('\n')[0],
                'task_id': task_id,
            }
        }