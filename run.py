from jinja2 import Template
import os
import requests


D4H_API_KEY = os.environ.get('D4H_API_KEY', '')


def get_d4h_headers():
    """
    Build the header dictionary for the requests library (simply includes the
    D4H API key).
    """
    headers = {
        'Authorization': 'Bearer {D4H_API_KEY}'.format(D4H_API_KEY=D4H_API_KEY)
    }
    return headers


def get_member_list():
    """
    Query the D4H API and build a list of member objects that we can use.
    """
    def _convert_status(status):
        """
        Helper method that turns D4H's shitty status object into a combination of
        whether or not the member is operational (True/False), and an optional class (e.g. Resource Member, MIT, etc.)
        """
        if status['type'].lower() == 'operational':
            operational = True
        elif status['type'].lower() == 'non-operational':
            operational = False

        label = status['label']['value'] if status['label'] is not None else None

        return (operational, label)

    response = requests.get('https://api.ca.d4h.org/v2/team/members', headers=get_d4h_headers())

    members_raw = response.json()['data']

    # Clean that shit up
    members = list()
    for member in members_raw:
        name = member.get('name').replace('\t', ' ').strip()
        try:
            first_name, last_name = name.split(' ', maxsplit=1)
        except ValueError:
            first_name = name
            last_name = ''

        operational, member_class = _convert_status(member.get('status'))

        members.append({
            'id': member.get('id'),
            'first_name': first_name,
            'last_name': last_name,
            'phone': member.get('mobilephone'),
            'callsign': member.get('ref'),
            'operational': operational,
            'member_class': member_class
        })

    return members


def render_member_list(members):
    """
    Render an HTML file with our member data.
    """
    def filter_active_members(member):
        return member['operational'] is True and member['member_class'] != 'Resource Member'

    active_members = sorted(filter(filter_active_members, members), key=lambda x: x['last_name'])
    resource_members = sorted(filter(lambda x: x['member_class'] == 'Resource Member', members), key=lambda x: x['last_name'])

    with open('member_list.html') as f:
        template = Template(f.read())
        return template.render(
            active_members=active_members,
            resource_members=resource_members
        )


def save_html_file(html):
    """
    Save the file.
    """
    with open('rendered_member_list.html', 'w+') as f:
        f.write(html)


def main():
    """
    Main function that gets run when you run `python run.py`
    """
    if not D4H_API_KEY:
        raise Exception('bad u')

    # Get raw list of users from D4H
    members = get_member_list()

    # Render and save the HTML
    html = render_member_list(members)
    save_html_file(html)

    # Open the file in Firefox, cause I'm lazy
    os.system('firefox rendered_member_list.html')


if __name__ == '__main__':
    main()
