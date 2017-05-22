# -*- coding: utf-8 -*-
# Author: Paulius Stundžia. Copyright: JSC Boolit.
# See LICENSE file for full copyright and licensing details.

{
    'name': 'Project Management Integration with VCS',
    'version': '0.10.0',
    'category': 'Project',
    'summary': 'project, vcs, git, integration',
    'description': """
	Integration of projects, tasks and timesheets with git repositories.
	""",
    'author': 'Paulius Stundžia',
    'website': '',
    'external_dependencies': {
        'python': ['github', 'pybitbucket']},
    'depends': [     
        'project',
        'hr_timesheet'
    ],
    'data': [
        'security/vcs_integration_security.xml',
        'security/ir.model.access.csv',
        'views/repository_views.xml',
        'views/project_views.xml',
        'views/project_vcs_config_settings_views.xml',
        'wizards/add_commit_to_timesheet_wizard_views.xml',
    ],
}
