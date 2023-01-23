#!/usr/bin/python3

import copy
import os
import sys

import editor

from jira import JIRA

from trolly.args import ComplicatedArgs
from trolly.jboard import JiraProject
from trolly.decor import md_print, pretty_date, color_string, hbar_under, nym
from trolly.config import get_config


def move(args):
    if args.project.move(args.src, args.target):
        print('Moved', args.src, 'to', args.target)
        return (0, False)
    return (1, False)


def close_issues(args):
    ret = 0
    for issue in args.target:
        if not args.project.close(issue):
            ret = 1
    return (ret, False)


def print_issues_simple(issues, args=None):
    states = {}
    for issue in issues:
        cstatus = issues[issue]['fields']['status']['name']
        if cstatus not in states:
            states[cstatus] = []
        states[cstatus].append(issue)

    for key in states:
        if args and args.status and nym(key) != nym(args.status):
            continue
        print(key)
        for issue in states[key]:
            print('  ', issue, end=' ')
            if args and args.labels:
                print_labels(issues[issue], prefix='')
            print(issues[issue]['fields']['summary'])


def search_issues(args):
    named = args.named_search
    if not args.text and not named:
        named = 'default'
    if named:
        searches = args.project.get_user_data('searches')
        if named not in searches:
            print(f'No search configured: {named}')
            return (1, False)
        search_query = searches[named]
        ret = args.project.search_issues(search_query)
    else:
        search_query = ' '.join(args.text)
        if args.raw:
            ret = args.project.search_issues(search_query)
        else:
            ret = args.project.search(search_query)

    if not ret:
        return (127, False)
    print_issues_simple(ret)
    return (0, False)


def list_issues(args):
    # check for verbose
    if args.mine:
        userid = 'me'
    elif args.unassigned:
        userid = 'none'
    elif args.user:
        userid = args.user
    else:
        userid = None

    issues = args.project.list(userid=userid)
    print_issues_simple(issues, args)
    return (0, True)


def list_link_types(args):
    ltypes = args.project.link_types()
    for lt in ltypes:
        print(lt.inward)
        print(lt.outward)
    return (0, True)


def list_states(args):
    states = args.project.states()
    for name in states:
        print('  ', name, states[name]['name'])
    return (0, False)


def list_issue_types(args):
    issue_types = args.project.issue_types()
    for itype in issue_types:
        print('  ', itype.name)
    return (0, False)


def split_issue_text(text):
    lines = text.split('\n')
    name = lines[0]
    desc = ''
    if not len(name):
        return (None, None)
    lines.pop(0)
    while len(lines) and lines[0] == '':
        lines.pop(0)
    if len(lines):
        desc = '\n'.join(lines)
    return (name, desc)


def new_issue(args):
    desc = None

    if args.text:
        name = ' '.join(args.text)
    else:
        text = editor()
        name, desc = split_issue_text(text)
        if name is None:
            print('Canceled')
            return (1, False)

    issue = args.project.new(name, desc, issue_type=args.type)
    if args.quiet:
        print(issue.raw['key'])
    else:
        print_issue(args.project, issue, False)
    return (0, True)


def new_subtask(args):
    desc = None
    parent_issue = args.project.issue(args.issue_id)

    if args.text:
        name = ' '.join(args.text)
    else:
        text = editor()
        name, desc = split_issue_text(text)
        if name is None:
            print('Canceled')
            return (1, False)

    issue = args.project.subtask(parent_issue.raw['key'], name, desc)
    if args.quiet:
        print(issue.raw['key'])
    else:
        print_issue(args.project, issue, False)
    return (0, True)


def link_issues(args):
    left_issue = args.issue_left
    right_issue = args.issue_right
    link_name = ' '.join(args.text)

    args.project.link(left_issue, right_issue, link_name)
    return (0, True)


def unlink_issues(args):
    args.project.unlink(args.issue_left, args.issue_right)
    return (0, True)


def comment(args):
    issue_id = args.issue

    if args.remove:
        comment_id = args.remove
        comment = args.project.get_comment(issue_id, comment_id)
        comment.delete()
        return (0, False)

    if args.edit:
        comment_id = args.edit
        comment = args.project.get_comment(issue_id, comment_id)
        if args.text:
            new_text = ' '.join(args.text)
        else:
            new_text = editor(comment.body)
            if not new_text:
                print('Canceled')
                return (0, False)
        if comment.body != new_text:
            comment.update(body=new_text)
        else:
            print('No changes')
        return (0, False)

    if args.text:
        text = ' '.join(args.text)
    else:
        text = editor()

    if not len(text):
        print('Canceled')
        return (0, False)

    args.project.comment(issue_id, text)
    return (0, False)


def refresh(args):
    args.project.refresh()
    args.project.index_issues()
    return (0, True)


def display_comment(action, verbose):
    print(pretty_date(action['updated']), '•', action['updateAuthor']['emailAddress'], '-', action['updateAuthor']['displayName'], '• ID:', action['id'])
    md_print(action['body'])
    print()


def display_attachment(attachment, verbose):
    print('  ' + attachment['name'])
    if verbose:
        print('    ID:', attachment['id'])
    if attachment['isUpload']:
        if attachment['filename'] != attachment['name']:
            print('    Filename:', attachment['filename'])
    else:
        if attachment['url'] != attachment['name']:
            print('    URL:', attachment['url'])


def print_labels(issue, prefix='Labels: '):
    if 'labels' in issue and len(issue['labels']):
        print(prefix, end='')
        for label in issue['labels']:
            print(label, end=' ')
        print()


def print_issue_links(issue, sep):
    hbar_under('Issue Links')
    # pass 1: Get the lengths so we can draw separators
    lsize = 0
    rsize = 0
    for link in issue['issuelinks']:
        if 'outwardIssue' in link:
            text = link['type']['outward'] + ' ' + link['outwardIssue']['key']
            status = link['outwardIssue']['fields']['status']['name']
        elif 'inwardIssue' in link:
            text = link['type']['inward'] + ' ' + link['inwardIssue']['key']
            status = link['inwardIssue']['fields']['status']['name']

        if len(text) > lsize:
            lsize = len(text)
        if len(status) > rsize:
            rsize = len(status)
    # pass 2: print the stuff
    for link in issue['issuelinks']:
        if 'outwardIssue' in link:
            text = link['type']['outward'] + ' ' + link['outwardIssue']['key']
            status = link['outwardIssue']['fields']['status']
            desc = link['outwardIssue']['fields']['summary']
        elif 'inwardIssue' in link:
            text = link['type']['inward'] + ' ' + link['inwardIssue']['key']
            status = link['inwardIssue']['fields']['status']
            desc = link['inwardIssue']['fields']['summary']
        print(text.ljust(lsize), sep, color_string(status['name'].ljust(rsize), status['statusCategory']['colorName']), sep, desc)
    print()


def print_subtasks(issue, sep):
    hbar_under('Sub-tasks')
    # pass 1: Get the lengths so we can draw separators
    lsize = 0
    rsize = 0
    for task in issue['subtasks']:
        task_key = task['key']
        status = task['fields']['status']['name']
        if len(task_key) > lsize:
            lsize = len(task_key)
        if len(status) > rsize:
            rsize = len(status)
    # pass 2: print the stuff
    for task in issue['subtasks']:
        task_key = task['key']
        status = task['fields']['status']
        print(task_key.ljust(lsize), sep, color_string(status['name'].ljust(rsize), status['statusCategory']['colorName']), sep, task['fields']['summary'])
    print()


def eval_custom_field(__code__, field):
    # Proof of concept.
    #
    # Only used if 'here_there_be_dragons' is set to true.  Represents
    # an obvious security issue if you are not in control of your
    # trolly configuration file:
    #     code: "system('rm -rf ~/*')"
    #

    # field:    is your variable name for your dict
    # __code__: is inline in your config and can reference field
    if '__code__' in __code__:
        raise ValueError('Reserved keyword in code snippet')
    try:
        return eval(str(__code__))
    except Exception as e:
        return str(e)


def print_issue(project, issue_obj, verbose):
    issue = issue_obj.raw['fields']

    lsize = len('Next States')
    if project.custom_fields:
        for field in project.custom_fields:
            if 'display' not in field or field['display'] is True:
                lsize = max(lsize, len(field['name']))

    lsize = max(len(issue_obj.raw['key']), lsize)
    sep = '┃'

    print(issue_obj.raw['key'].ljust(lsize), sep, issue['summary'])
    print('Type'.ljust(lsize), sep, issue['issuetype']['name'])
    print('Created'.ljust(lsize), sep, pretty_date(issue['created']), end=' ')
    if issue['created'] != issue['updated']:
        dstr = pretty_date(issue['updated'])
        print(f'(Updated {dstr})')
    else:
        print()

    if 'parent' in issue and issue['parent']:
        print('Parent'.ljust(lsize), sep, issue['parent']['key'])
    print('Status'.ljust(lsize), sep, color_string(issue['status']['name'], 'white', issue['status']['statusCategory']['colorName']))

    if verbose:
        print('Creator'.ljust(lsize), sep, issue['creator']['emailAddress'], '-', issue['creator']['displayName'])
        if issue['reporter'] is not None and issue['reporter']['emailAddress'] != issue['creator']['emailAddress']:
            print('Reporter'.ljust(lsize), sep, issue['reporter']['emailAddress'], '-', issue['creator']['displayName'])
        print('ID'.ljust(lsize), sep, issue_obj.raw['id'])
        print('URL'.ljust(lsize), sep, issue_obj.permalink())

    if 'assignee' in issue and issue['assignee'] and 'name' in issue['assignee']:
        print('Assignee'.ljust(lsize), sep, end=' ')
        print(issue['assignee']['emailAddress'], '-', issue['assignee']['displayName'])
        # todo: add watchers (verbose)

    print_labels(issue, prefix='Labels'.ljust(lsize) + f' {sep} ')

    if verbose:
        trans = project.transitions(issue_obj.raw['key'])
        print('Next States'.ljust(lsize), sep, end=' ')
        if trans:
            print([tr['name'] for tr in trans.values()])
        else:
            print('No valid transitions; cannot alter status')

    if project.custom_fields:
        for field in project.custom_fields:
            if 'display' in field and field['display'] is not True:
                continue
            if field['id'] not in issue:
                continue
            if 'code' in field and project.allow_code:
                value = eval_custom_field(field['code'], issue[field['id']])
            else:
                value = issue[field['id']]
            if value is not None:
                print(field['name'].ljust(lsize), sep, str(value))

    print()
    if issue['description']:
        md_print(issue['description'])
        print()

    if 'issuelinks' in issue and len(issue['issuelinks']):
        print_issue_links(issue, sep)

    if 'subtasks' in issue and len(issue['subtasks']):
        print_subtasks(issue, sep)

    if issue['comment']['comments']:
        hbar_under('Comments')

        for cmt in issue['comment']['comments']:
            display_comment(cmt, verbose)


def cat(args):
    issues = []
    for issue_idx in args.issue_id:
        issue = args.project.issue(issue_idx, True)
        if not issue:
            print('No such issue:', issue_idx)
            return (127, False)
        issues.append(issue)

    for issue in issues:
        print_issue(args.project, issue, args.verbose)
    return (0, False)


def join_issue_text(name, desc):
    if desc:
        return name + '\n\n' + desc
    return name + '\n\n'


def edit_issue(args):
    issue_idx = args.issue

    issue_obj = args.project.issue(issue_idx)
    issue = issue_obj.raw['fields']
    issue_text = join_issue_text(issue['summary'], issue['description'])
    if args.text:
        new_text = ' '.join(args.text)
    else:
        new_text = editor(issue_text)
    if not new_text:
        print('Canceled')
        return (0, False)
    name, desc = split_issue_text(new_text)
    update_args = {}
    if issue['summary'] != name and issue['summary']:
        update_args['summary'] = name
    if issue['description'] != desc:
        update_args['description'] = desc
    if update_args != {}:
        args.project.update_issue(issue_idx, **update_args)
    else:
        print('No changes')
    return (0, False)


def view_issue(args):
    issue_id = args.issue_id
    issue = args.project.issue(issue_id)
    if not issue:
        return (127, False)
    os.system('xdg-open ' + issue.permalink())
    return (0, False)


def assign_issue(args):
    args.project.assign(args.issue_id, args.user)
    return (0, False)


def unassign_issue(args):
    args.project.assign(args.issue_id, 'none')
    return (0, False)


def get_project(project=None):
    config = get_config()
    allow_code = False

    if 'jira' not in config:
        print('No JIRA configuration available')
        return None
    if 'url' not in config['jira']:
        print('No JIRA URL specified')
        return None
    if 'token' not in config['jira']:
        print('No JIRA token specified')
        return None
    if 'default_project' not in config['jira']:
        print('No default JIRA project specified')
        return None

    # Allows users to represent custom fields in output.
    # Not recommended to enable.
    if 'here_there_be_dragons' in config['jira']:
        if config['jira']['here_there_be_dragons'] is True:
            allow_code = True

    jconfig = config['jira']
    if not project:
        # Not sure why I used an array here
        project = jconfig['default_project']

    jira = JIRA(jconfig['url'], token_auth=jconfig['token'])
    proj = JiraProject(jira, project, readonly=False, allow_code=allow_code)
    if 'searches' in jconfig:
        proj.set_user_data('searches', jconfig['searches'])
    if 'custom_fields' in jconfig:
        proj.custom_fields = copy.deepcopy(jconfig['custom_fields'])
    return proj


def create_parser():
    parser = ComplicatedArgs()

    parser.add_argument('-p', '--project', help='Use this JIRA project instead of default', default=None, type=str.upper)

    cmd = parser.command('ls', help='List issue(s)', handler=list_issues)
    cmd.add_argument('-m', '--mine', action='store_true', help='Display only issues assigned to me.')
    cmd.add_argument('-U', '--unassigned', action='store_true', help='Display only issues with no assignee.')
    cmd.add_argument('-u', '--user', help='Display only issues assigned to the specific user.')
    cmd.add_argument('-l', '--labels', action='store_true', help='Display issue labels.')
    cmd.add_argument('status', nargs='?', default=None, help='Restrict to issues in this state')

    cmd = parser.command('search', help='Search issue(s) with matching text', handler=search_issues)
    cmd.add_argument('-n', '--named-search', help='Perform preconfigured named search')
    cmd.add_argument('-r', '--raw', action='store_true', help='Perform raw JQL query')
    cmd.add_argument('text', nargs='*', help='Search text')

    cmd = parser.command('cat', help='Print issue(s)', handler=cat)
    cmd.add_argument('-v', '--verbose', action='store_true', help='Verbose output')
    cmd.add_argument('issue_id', nargs='+', help='Target issue(s)', type=str.upper)

    cmd = parser.command('view', help='Display issue in browser', handler=view_issue)
    cmd.add_argument('issue_id', help='Target issue', type=str.upper)

    parser.command('ll', help='List states available to project', handler=list_states)
    parser.command('lt', help='List issue types available to project', handler=list_issue_types)
    parser.command('link-types', help='Display link types', handler=list_link_types)

    cmd = parser.command('assign', help='Assign issue', handler=assign_issue)
    cmd.add_argument('issue_id', help='Target issue', type=str.upper)
    cmd.add_argument('user', help='Target assignee')
    # cmd.add_argument('users', help='First is assignee; rest are watchers (if none, assign to self)', nargs='*')

    cmd = parser.command('unassign', help='Remove assignee from issue', handler=unassign_issue)
    cmd.add_argument('issue_id', help='Target issue', type=str.upper)

    cmd = parser.command('mv', help='Move issue(s) to new state', handler=move)
    cmd.add_argument('src', metavar='issue', nargs='+', help='Issue key(s)')
    cmd.add_argument('target', help='Target state')

    cmd = parser.command('new', help='Create a new issue', handler=new_issue)
    cmd.add_argument('-t', '--type', default='task', help='Issue type (project-dependent)')
    cmd.add_argument('-q', '--quiet', default=False, help='Only print new issue ID after creation (for scripting)', action='store_true')
    cmd.add_argument('text', nargs='*', help='Issue summary')

    cmd = parser.command('subtask', help='Create a new subtask', handler=new_subtask)
    cmd.add_argument('-q', '--quiet', default=False, help='Only print subtask ID after creation (for scripting)', action='store_true')
    cmd.add_argument('issue_id', help='Parent issue', type=str.upper)
    cmd.add_argument('text', nargs='*', help='Subtask summary')

    cmd = parser.command('link', help='Create link between two issues', handler=link_issues)
    cmd.add_argument('issue_left', help='First issue', type=str.upper)
    cmd.add_argument('text', nargs='+', help='Link text')
    cmd.add_argument('issue_right', help='Second issue', type=str.upper)

    cmd = parser.command('unlink', help='Remove link(s) between two issues', handler=unlink_issues)
    cmd.add_argument('issue_left', help='First issue', type=str.upper)
    cmd.add_argument('issue_right', help='Second issue', type=str.upper)

    cmd = parser.command('comment', help='Comment (or remove) on an issue', handler=comment)
    cmd.add_argument('-e', '--edit', help='Comment ID to edit')
    cmd.add_argument('-r', '--remove', help='Comment ID to remove')
    cmd.add_argument('issue', help='Issue to operate on')
    cmd.add_argument('text', nargs='*', help='Comment text')

    cmd = parser.command('edit', help='Edit comment text', handler=edit_issue)
    cmd.add_argument('issue', help='Issue')
    cmd.add_argument('text', nargs='*', help='New text')

    cmd = parser.command('close', help='Move issue(s) to closed/done/resolved', handler=close_issues)
    cmd.add_argument('target', nargs='+', help='Target issue(s)')

    return parser


def main():
    parser = create_parser()
    ns = parser.parse_args()

    try:
        project = get_project(ns.project)
    except KeyError:
        sys.exit(1)

    # Pass this down in namespace to callbacks
    parser.add_arg('project', project)
    rc = parser.finalize(ns)
    if rc:
        ret = rc[0]
        save = rc[1]  # NOQA
    else:
        print('No command specified')
        ret = 0
        save = False  # NOQA
    sys.exit(ret)


if __name__ == '__main__':
    main()
