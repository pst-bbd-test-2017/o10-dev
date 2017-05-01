# -*- coding: utf-8 -*-
# Author: Paulius Stundžia. Copyright: JSC Boolit.
# See LICENSE file for full copyright and licensing details.

{
    'name': 'Project Management Integration with CVS',
    'version': '0.6.0',
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
        'views/repository_views.xml',
        'views/project_views.xml',
    ],
}
