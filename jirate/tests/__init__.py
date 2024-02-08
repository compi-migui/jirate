#!/usr/bin/env python

import jira.utils
# Hack to paste input to output
jira.utils.json_loads = lambda val: val

from jira.client import JIRA
from jira.resources import Issue, dict2resource, Project
from jirate.args import GenericArgs
from jirate.decor import pretty_print

testx = 1

fake_user = {'self': 'https://domain.com/rest/api/2/user?username=porkchop', 'key': 'porkchop', 'name': 'porkchop', 'emailAddress': 'porkchop@domain.com', 'avatarUrls': {'48x48': 'https://domain.com/secure/useravatar?avatarId=1', '24x24': 'https://domain.com/secure/useravatar?size=small&avatarId=1', '16x16': 'https://domain.com/secure/useravatar?size=xsmall&avatarId=1',
                                                                                                                                                                          '32x32': 'https://domain.com/secure/useravatar?size=medium&avatarId=1'}, 'displayName': 'Chop Pork', 'active': True, 'deleted': False, 'timeZone': 'America/New_York', 'locale': 'en_US', 'groups': {'size': 9, 'items': []}, 'applicationRoles': {'size': 1, 'items': []}, 'expand': 'groups,applicationRoles'}


fake_fields = [
    {'clauseNames': ['parent', 'Parent'],
        'custom': False,
        'id': 'parent',
        'name': 'Parent',
        'schema': {'system': 'parent', 'type': 'issuelink'}
     },
    {'clauseNames': ['priority', 'Priority'],
        'custom': False,
        'id': 'priority',
        'name': 'Priority',
        'schema': {'system': 'priority', 'type': 'priority'},
        'allowedValues': [
            {'id': 101,
             'name': 'Blocker'},
            {'id': 102,
             'name': 'Critical'},
            {'id': 103,
             'name': 'Major'},
            {'id': 104,
             'name': 'Normal'},
            {'id': 105,
             'name': 'Minor'},
            {'id': 106,
             'name': 'Undefined'}],
        'defaultValue': {'id': 104, 'name': 'Normal'},
        'hasDefaultValue': True,
        'operations': ['set']
     },
    {'clauseNames': ['description', 'Description'],
        'custom': False,
        'name': 'Description',
        'id': 'description',
        'required': True,
        'operations': ['set'],
        'schema': {'type': 'string'},
     },
    {'clauseNames': ['components', 'Component/s'],
        'custom': False,
        'id': 'components',
        'name': 'Component/s',
        'schema': {'system': 'items', 'type': 'array', 'items': 'component'},
        'allowedValues': [
            {'id': 1001,
             'name': 'python'},
            {'id': 1002,
             'name': 'kernel'},
            {'id': 1003,
             'name': 'glibc'},
            {'id': 1004,
             'name': 'porkchop'}],
        'operations': ['add', 'set', 'remove'],
        'required': True
     },
    {'clauseNames': ['cf[1234567]', 'Fixed in Build'],
        'custom': True,
        'id': 'customfield_1234567',
        'name': 'Fixed in Build',
        'navigable': True,
        'orderable': True,
        'schema': {'custom': 'com.atlassian.jira.plugin.system.customfieldtypes:textfield',
                   'customId': 1234567,
                   'type': 'string'},
        'operations': ['set'],
        'searchable': True},
    {'clauseNames': ['cf[1234568]', 'Score'],
        'custom': True,
        'id': 'customfield_1234568',
        'name': 'Score',
        'navigable': True,
        'orderable': True,
        'schema': {'custom': 'org.jboss.labs.jira.plugin.jboss-custom-field-types-plugin:jbonlynumber',
                   'customId': 1234568,
                   'type': 'number'},
        'operations': ['set'],
        'searchable': True},
    {'clauseNames': ['cf[1234569]', 'Array of Options'],
        'custom': True,
        'id': 'customfield_1234569',
        'name': 'Array of Options',
        'navigable': True,
        'orderable': True,
        'schema': {'custom': 'com.atlassian.jira.plugin.system.customfieldtypes:multiselect',
                   'customId': 1234569,
                   'items': 'option',
                   'type': 'array'},
        'allowedValues': [
            {'value': 'One',
             'id': '1'},
            {'value': 'Two',
             'id': '2'},
            {'value': 'Three',
             'id': '3'}
    ],
        'operations': ['add', 'set', 'remove'],
        'searchable': True},
    {'clauseNames': ['cf[1234570]', 'Array of Versions'],
        'custom': True,
        'id': 'customfield_1234570',
        'name': 'Array of Versions',
        'navigable': True,
        'orderable': True,
        'schema': {'custom': 'com.atlassian.jira.plugin.system.customfieldtypes:multiselect',
                   'customId': 1234570,
                   'items': 'version',
                   'type': 'array'},
        'allowedValues': [
            {'name': '1.0.1',
             'id': '11'},
            {'name': '1.0.2',
             'id': '12'}
    ],
        'operations': ['add', 'set', 'remove'],
        'searchable': True},
    {'clauseNames': ['cf[1234571]', 'Array of Users'],
        'custom': True,
        'id': 'customfield_1234571',
        'name': 'Array of Users',
        'navigable': True,
        'orderable': True,
        'schema': {'custom': 'com.atlassian.jira.plugin.system.customfieldtypes:multiselect',
                   'customId': 1234571,
                   'items': 'user',
                   'type': 'array'},
        'operations': ['add', 'set', 'remove'],
        'searchable': True},
    {'clauseNames': ['cf[1234572]', 'Array of Strings'],
        'custom': True,
        'id': 'customfield_1234572',
        'name': 'Array of Strings',
        'navigable': True,
        'orderable': True,
        'schema': {'custom': 'com.atlassian.jira.plugin.system.customfieldtypes:multiselect',
                   'customId': 1234572,
                   'items': 'string',
                   'type': 'array'},
        'operations': ['add', 'set', 'remove'],
        'searchable': True},
    {'clauseNames': ['cf[1234573]', 'Array of Groups'],
        'custom': True,
        'id': 'customfield_1234573',
        'name': 'Array of Groups',
        'navigable': True,
        'orderable': True,
        'schema': {'custom': 'com.atlassian.jira.plugin.system.customfieldtypes:multiselect',
                   'customId': 1234573,
                   'items': 'group',
                   'type': 'array'},
        'searchable': True},
    {'clauseNames': ['cf[1234574]', 'Any Value'],
        'custom': True,
        'id': 'customfield_1234574',
        'name': 'Any Value',
        'navigable': True,
        'orderable': True,
        'schema': {'custom': 'com.atlassian.jira.plugin.system.customfieldtypes:multiselect',
                   'customId': 1234574,
                   'type': 'any'},
        'operations': ['add', 'set', 'remove'],
        'searchable': True},
    {'clauseNames': ['cf[1234575]', 'Date Value'],
        'custom': True,
        'id': 'customfield_1234575',
        'name': 'Date Value',
        'navigable': True,
        'orderable': True,
        'schema': {'custom': 'com.atlassian.jira.plugin.system.customfieldtypes:multiselect',
                   'customId': 1234575,
                   'type': 'date'},
        'operations': ['set'],
        'searchable': True},
    {'clauseNames': ['cf[1234576]', 'Datetime Value'],
        'custom': True,
        'id': 'customfield_1234576',
        'name': 'Datetime Value',
        'navigable': True,
        'orderable': True,
        'schema': {'custom': 'com.atlassian.jira.plugin.system.customfieldtypes:multiselect',
                   'customId': 1234576,
                   'type': 'datetime'},
        'operations': ['set'],
        'searchable': True},
    {'clauseNames': ['cf[1234577]', 'Related Issue'],
        'custom': True,
        'id': 'customfield_1234577',
        'name': 'Related Issue',
        'navigable': True,
        'orderable': True,
        'schema': {'custom': 'com.atlassian.jira.plugin.system.customfieldtypes:multiselect',
                   'customId': 1234577,
                   'type': 'issuelinks'},
        'operations': ['set'],
        'searchable': True},
    {'clauseNames': ['cf[1234578]', 'Option Value'],
        'custom': True,
        'id': 'customfield_1234578',
        'name': 'Option Value',
        'navigable': True,
        'orderable': True,
        'operations': ['set'],
        'allowedValues': [
            {'value': 'One',
             'id': '1'},
            {'value': 'Two',
             'id': '2'},
            {'value': 'Three',
             'id': '3'}
    ],
        'schema': {'custom': 'com.atlassian.jira.plugin.system.customfieldtypes:multiselect',
                   'customId': 1234578,
                   'type': 'option'},
        'searchable': True},
    {'clauseNames': ['cf[1234579]', 'Option and Child'],
        'custom': True,
        'id': 'customfield_1234579',
        'name': 'Option and Child',
        'navigable': True,
        'orderable': True,
        'schema': {'custom': 'com.atlassian.jira.plugin.system.customfieldtypes:multiselect',
                   'customId': 1234579,
                   'type': 'option-with-child'},
        'allowedValues': [
            {'value': 'One',
             'id': '1'},
            {'value': 'Two',
             'id': '2'},
            {'value': 'Three',
             'id': '3'}
    ],
        'searchable': True},
    {'clauseNames': ['cf[1234580]', 'User Value'],
        'custom': True,
        'id': 'customfield_1234580',
        'name': 'User Value',
        'navigable': True,
        'orderable': True,
        'schema': {'custom': 'com.atlassian.jira.plugin.system.customfieldtypes:multiselect',
                   'customId': 1234580,
                   'type': 'user'},
        'searchable': True},
    {'clauseNames': ['cf[1234581]', 'Version Value'],
        'custom': True,
        'id': 'customfield_1234581',
        'name': 'Version Value',
        'navigable': True,
        'orderable': True,
        'schema': {'custom': 'com.atlassian.jira.plugin.system.customfieldtypes:multiselect',
                   'customId': 1234581,
                   'type': 'version'},
        'allowedValues': [
            {'name': '1.0.1',
             'id': '11'},
            {'name': '1.0.2',
             'id': '12'}
    ],
        'searchable': True}

]


fake_metadata = {val['id']: val for val in fake_fields}


fake_transitions = {'expand': 'transitions',
                    'transitions': [{'id': '11', 'name': 'New', 'to': {'name': 'New', 'id': '10000'}},
                                    {'id': '12', 'name': 'In Progress', 'to': {'name': 'In Progres', 'id': '10001'}},
                                    {'id': '13', 'name': 'Done', 'to': {'name': 'Done', 'id': '10002'},
                                     'fields':
                                         {'resolution': {
                                             'name': 'Resolution',
                                             'fieldId': 'resolution',
                                             'schema': {
                                                 'type': 'resolution',
                                                 'system': 'resolution'},
                                             'operations': ['set'],
                                             'allowedValues': [{'name': 'Done'}, {'name': 'Won\'t Do'}, {'name': 'Duplicate'}]}}},
                                    {'id': '14', 'name': 'New', 'to': {'name': 'New', 'id': '10003'}}]
                    }


fake_issues = {
    'TEST-1': {'expand': 'renderedFields,names,schema,operations,editmeta,changelog,versionedRepresentations',
               'fields': {'aggregateprogress': {'progress': 0, 'total': 0},
                          'aggregatetimeestimate': None,
                          'aggregatetimeoriginalestimate': None,
                          'aggregatetimespent': None,
                          'archivedby': None,
                          'archiveddate': None,
                          'assignee': {'active': True,
                                       'displayName': 'Rory Obert',
                                       'emailAddress': 'robert@pie.com',
                                       'key': 'rory',
                                       'name': 'rory',
                                       'self': 'https://domain.com/rest/api/2/user?username=rory',
                                       'timeZone': 'America/New_York'},
                          'attachment': [],
                          'comment': {'comments': []},
                          'components': [{'name': 'food, pork'}, {'name': 'food, carrot'}],
                          'created': '2023-08-03T10:28:48.366+0000',
                          'description': 'Test Description 1',
                          'duedate': '2024-01-30',
                          'environment': None,
                          'fixVersions': [],
                          'issuelinks': [],
                          'issuetype': {'avatarId': 13263,
                                        'description': 'A bug',
                                        'id': '1',
                                        'name': 'Bug',
                                        'self': 'https://domain.com/rest/api/2/issuetype/1',
                                        'subtask': False},
                          'labels': ['label1', 'label2'],
                          'lastViewed': '2023-11-22T15:51:50.281+0000',
                          'priority': {'id': '104', 'name': 'Normal'},
                          'progress': {'progress': 0, 'total': 0},
                          'project': {'id': '1234',
                                      'key': 'TEST',
                                      'name': 'Test Project',
                                      'projectCategory': {'description': 'Test Projects',
                                                          'id': '1073',
                                                          'name': 'Projecto',
                                                          'self': 'https://domain.com/rest/api/2/projectCategory/1073'},
                                      'projectTypeKey': 'software',
                                      'self': 'https://domain.com/rest/api/2/project/1234'},
                          'reporter': {'active': True,
                                       'displayName': 'Pork Chop',
                                       'emailAddress': 'pchop@domai.com',
                                       'key': 'JIRAUSER1',
                                       'name': 'pchop@domain.com',
                                       'self': 'https://domain.com/rest/api/2/user?username=pchop%40domain.com',
                                       'timeZone': 'Asia/Kolkata'},
                          'resolution': None,
                          'resolutiondate': None,
                          'security': None,
                          'status': {'description': 'Initial creation status. ',
                                     'id': '10',
                                     'name': 'New',
                                     'self': 'https://domain.com/rest/api/2/status/10016',
                                     'statusCategory': {'colorName': 'default',
                                                        'id': 2,
                                                        'key': 'new',
                                                        'name': 'To Do',
                                                        'self': 'https://domain.com/rest/api/2/statuscategory/2'}},
                          'subtasks': [],
                          'summary': 'Test 1',
                          'timeestimate': None,
                          'timeoriginalestimate': None,
                          'timespent': None,
                          'timetracking': {},
                          'updated': '2023-11-30T15:06:39.875+0000',
                          'versions': [{'archived': False,
                                        'description': '',
                                        'id': '6',
                                        'name': 'version-6',
                                        'released': False,
                                        'self': 'https://domain.com/rest/api/2/version/6'}],
                          'votes': {'hasVoted': False,
                                    'self': 'https://domain.com/rest/api/2/issue/TEST-1/votes',
                                    'votes': 0},
                          'watches': {'isWatching': False,
                                      'self': 'https://domain.com/rest/api/2/issue/TEST-1/watchers',
                                      'watchCount': 2},
                          'worklog': {'maxResults': 20,
                                      'startAt': 0,
                                      'total': 0,
                                      'worklogs': []},
                          'workratio': -1,
                          'customfield_1234567': 'test-build-1',
                          'customfield_1234568': 22.0,
                          'customfield_1234569': [{'name': 'Option1', 'value': 'option_one'},
                                                  {'name': 'Option2', 'value': 'option_two'}],
                          'customfield_1234570': [{'name': 'Version1', 'value': 'version_one'},
                                                  {'name': 'Version2', 'value': 'version_two'}],
                          'customfield_1234571': [{'key': 'user1', 'name': 'user-one', 'displayName': 'One', 'emailAddress': 'one@two.com'},
                                                  {'key': 'user2', 'name': 'two@other.eml', 'displayName': 'Two', 'emailAddress': 'two@two.com'}],
                          'customfield_1234572': ['one', 'two', 'three, and four'],
                          'customfield_1234573': [{'name': 'group1'}, {'name': 'group2'}],
                          'customfield_1234574': ['one', 2.0],
                          'customfield_1234575': '2022-08-01',
                          'customfield_1234576': '2019-12-25T02:10:00.000+0000',
                          'customfield_1234577': {'key': 'TEST-2'},
                          'customfield_1234578': {'name': 'Option1', 'value': 'option_one'},
                          'customfield_1234579': {'name': 'Option1', 'value': 'option_one', 'child': {'name': 'child1', 'value': 'child_value'}},
                          'customfield_1234580': {
                   'displayName': 'Rory Obert',
                                  'emailAddress': 'robert@pie.com',
                                  'key': 'rory',
                                  'name': 'rory',
                                  'self': 'https://domain.com/rest/api/2/user?username=rory',
                                  'timeZone': 'America/New_York'},
                          'customfield_1234581': {'name': 'Version1', 'value': 'version_one'}
                          },
               'id': '1000001',
               'key': 'TEST-1',
               'self': 'https://domain.com/rest/api/2/issue/1000001'},

    'TEST-2': {'expand': 'renderedFields,names,schema,operations,editmeta,changelog,versionedRepresentations',
               'fields': {'aggregateprogress': {'progress': 0, 'total': 0},
                          'aggregatetimeestimate': None,
                          'aggregatetimeoriginalestimate': None,
                          'aggregatetimespent': None,
                          'archivedby': None,
                          'archiveddate': None,
                          'assignee': None,
                          'attachment': [],
                          'comment': {'comments': []},
                          'components': [],
                          'created': '2023-08-03T10:28:48.366+0000',
                          'customfield_1234567': None,
                          'customfield_1234568': None,
                          'customfield_1234569': None,
                          'description': 'Test Description 2',
                          'duedate': '2024-01-30',
                          'environment': None,
                          'fixVersions': [],
                          'issuelinks': [],
                          'issuetype': {'avatarId': 13263,
                                        'description': 'A bug',
                                        'id': '1',
                                        'name': 'Bug',
                                        'self': 'https://domain.com/rest/api/2/issuetype/1',
                                        'subtask': False},
                          'labels': ['label2'],
                          'lastViewed': '2023-11-22T15:51:50.281+0000',
                          'priority': {'id': 104, 'name': 'Normal'},
                          'progress': {'progress': 0, 'total': 0},
                          'project': {'id': '1234',
                                      'key': 'TEST',
                                      'name': 'Test Project',
                                      'projectCategory': {'description': 'Test Projects',
                                                          'id': '1073',
                                                          'name': 'Projecto',
                                                          'self': 'https://domain.com/rest/api/2/projectCategory/1073'},
                                      'projectTypeKey': 'software',
                                      'self': 'https://domain.com/rest/api/2/project/1234'},
                          'reporter': {'active': True,
                                       'displayName': 'Pork Chop',
                                       'emailAddress': 'pchop@domai.com',
                                       'key': 'JIRAUSER1',
                                       'name': 'pchop@domain.com',
                                       'self': 'https://domain.com/rest/api/2/user?username=pchop%40domain.com',
                                       'timeZone': 'Asia/Kolkata'},
                          'resolution': None,
                          'resolutiondate': None,
                          'security': None,
                          'status': {'description': 'Initial creation status. ',
                                     'id': '10',
                                     'name': 'New',
                                     'self': 'https://domain.com/rest/api/2/status/10016',
                                     'statusCategory': {'colorName': 'default',
                                                        'id': 2,
                                                        'key': 'new',
                                                        'name': 'To Do',
                                                        'self': 'https://domain.com/rest/api/2/statuscategory/2'}},
                          'subtasks': [],
                          'summary': 'Test 1',
                          'timeestimate': None,
                          'timeoriginalestimate': None,
                          'timespent': None,
                          'timetracking': {},
                          'updated': '2023-11-30T15:06:39.875+0000',
                          'versions': [{'archived': False,
                                        'description': '',
                                        'id': '6',
                                        'name': 'version-6',
                                        'released': False,
                                        'self': 'https://domain.com/rest/api/2/version/6'}],
                          'votes': {'hasVoted': False,
                                    'self': 'https://domain.com/rest/api/2/issue/TEST-1/votes',
                                    'votes': 0},
                          'watches': {'isWatching': False,
                                      'self': 'https://domain.com/rest/api/2/issue/TEST-1/watchers',
                                      'watchCount': 2},
                          'worklog': {'maxResults': 20,
                                      'startAt': 0,
                                      'total': 0,
                                      'worklogs': []},
                          'workratio': -1},
               'id': '1000002',
               'key': 'TEST-2',
               'self': 'https://domain.com/rest/api/2/issue/1000002'}
}


fake_statuses = [
        {'id': '12363',
         'name': 'Bug',
         'subtask': False,
         'statuses': [{'id': '10000', 'name': 'New', 'statusCategory': { 'id': 2, 'name': 'To Do'}},
                      {'id': '10001', 'name': 'In Progress', 'statusCategory': { 'id': 4, 'name': 'In Progress' }},
                      {'id': '10002', 'name': 'Done', 'statusCategory': { 'id': 6, 'name': 'Done'}}
                     ]
         }
        ]

fake_project = {   'archived': False,
    'assigneeType': 'UNASSIGNED',
    'components': [   {   'description': 'Comp1',
                          'id': '12392576',
                          'isAssigneeTypeValid': False,
                          'name': 'aardvark',
                          'self': 'https://issues.pie.com/rest/api/2/component/12392576'},
                      {   'description': 'anteater',
                          'id': '12392393',
                          'isAssigneeTypeValid': False,
                          'name': 'anteater',
                          'self': 'https://issues.pie.com/rest/api/2/component/12392393'},
                      {   'description': 'yellow belly',
                          'id': '12392577',
                          'isAssigneeTypeValid': False,
                          'name': 'marmot',
                          'self': 'https://issues.pie.com/rest/api/2/component/12392577'}],
    'description': 'The Test Project',
    'expand': 'description,lead,url,projectKeys',
    'id': '12336920',
    'issueTypes': [   {
                          'description': '',
                          'iconUrl': 'https://issues.pie.com/secure/viewavatar?size=xsmall&avatarId=13275&avatarType=issuetype',
                          'id': '20',
                          'name': 'Bug',
                          'self': 'https://issues.pie.com/rest/api/2/issuetype/20',
                          'subtask': False},
                      {   'avatarId': 13267,
                          'description': 'Created by Jira Software - do not '
                                         'edit or delete. Issue type for a big '
                                         'user story that needs to be broken '
                                         'down.',
                          'iconUrl': 'https://issues.pie.com/secure/viewavatar?size=xsmall&avatarId=13267&avatarType=issuetype',
                          'id': '16',
                          'name': 'Epic',
                          'self': 'https://issues.pie.com/rest/api/2/issuetype/16',
                          'subtask': False},
                      {   'avatarId': 13275,
                          'description': 'Created by Jira Software - do not '
                                         'edit or delete. Issue type for a '
                                         'user story.',
                          'iconUrl': 'https://issues.pie.com/secure/viewavatar?size=xsmall&avatarId=13275&avatarType=issuetype',
                          'id': '17',
                          'name': 'Story',
                          'self': 'https://issues.pie.com/rest/api/2/issuetype/17',
                          'subtask': False},
                      {   'avatarId': 13278,
                          'description': 'A task that needs to be done.',
                          'iconUrl': 'https://issues.pie.com/secure/viewavatar?size=xsmall&avatarId=13278&avatarType=issuetype',
                          'id': '3',
                          'name': 'Task',
                          'self': 'https://issues.pie.com/rest/api/2/issuetype/3',
                          'subtask': False},
                      {   'avatarId': 13276,
                          'description': 'The sub-task of the issue',
                          'iconUrl': 'https://issues.pie.com/secure/viewavatar?size=xsmall&avatarId=13276&avatarType=issuetype',
                          'id': '5',
                          'name': 'Sub-task',
                          'self': 'https://issues.pie.com/rest/api/2/issuetype/5',
                          'subtask': True}],
    'key': 'TEST',
    'lead': {   'active': True,
                'displayName': "Pork Chop",
                'key': 'pchop',
                'name': 'pchop@pie.com',
                'self': 'https://issues.pie.com/rest/api/2/user?username=pchop@pie.com'},
    'name': 'Test Project',
    'projectCategory': {   'description': 'The Project Category',
                           'id': '10730',
                           'name': 'Category',
                           'self': 'https://issues.pie.com/rest/api/2/projectCategory/10730'},
    'projectTypeKey': 'software',
    'versions': [   {   'archived': False,
                        'description': '1.0',
                        'id': '12416509',
                        'name': 'version-1.0',
                        'overdue': False,
                        'projectId': 12336920,
                        'releaseDate': '2032-01-01',
                        'released': False,
                        'self': 'https://issues.pie.com/rest/api/2/version/12416509',
                        'startDate': '2024-01-01',
                        'userReleaseDate': '2024/06/01',
                        'userStartDate': '2024/01/01'},
                    {   'archived': False,
                        'description': '2.0',
                        'id': '12416345',
                        'name': 'version-2.0',
                        'overdue': False,
                        'projectId': 12336920,
                        'releaseDate': '2024-03-05',
                        'released': False,
                        'self': 'https://issues.pie.com/rest/api/2/version/12416345',
                        'startDate': '2023-12-01',
                        'userReleaseDate': '2024/12/01',
                        'userStartDate': '2024/12/01'}]
}


class fake_jira_session():
    def __init__(self):
        self.get_urls = []
        self.post_urls = {}
        self.delete_urls = []

    def get(self, url):
        self.get_urls.append(url)
        if url.endswith('statuses'):
            return fake_statuses

    def post(self, url, data=None):
        self.post_urls[url] = data

    def delete(self, url):
        self.delete_urls.append(url)

    def close(self):
        pass

    def reset(self):
        self.__init__()


class fake_jira(JIRA):
    def __init__(self, **kwargs):
        self._fields_cache_value = {}
        self.deploymentType = 'Server'
        self._version = (9, 0, 0)
        self._options = {'async': False}

    def _get_url(self, url_fragment, **args):
        pass

    def _get_json(self, url_fragment, **args):
        pass

    def add_simple_link(self, issue, link):
        pass

    def search_users(self, username):
        pass

    def fields(self):
        return fake_fields

    def search_issues(self, seach_query, startAt=None, maxResults=None):
        pass

    def create_issue(self, **args):
        global testx

        ret = GenericArgs()
        proj = args['project']
        ret.key = f'{proj}-{testx}'
        testx = testx + 1
        ret.raw = {'fields': args}
        ret.raw['fields']['project'] = {'key': proj}
        pretty_print(ret)
        return ret

    def issue(self, issue_key):
        if issue_key.upper() not in fake_issues:
            return None
        ret = Issue(None, None)
        ret.raw = fake_issues[issue_key]
        dict2resource(fake_issues[issue_key], ret)
        return ret

    def issue_link_types(self):
        pass

    def create_issue_link(self, text, left_key, right_key):
        pass

    def remote_links(self, issue_key):
        pass

    def remote_link(self, left_key, right_key):
        pass

    def delete_issue_link(self, left_key, right_key):
        pass

    def project(self, project_key):
        ret = Project({'server': 'issues.pie.com', 'rest_path': 'rest/api/2', 'rest_api_version': 2, 'async': False}, None)
        ret.raw = fake_project
        dict2resource(fake_project, ret)
        return ret

    def myself(self):
        return fake_user

    _session = fake_jira_session()
