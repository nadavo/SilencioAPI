from __future__ import print_function
import httplib2
import os
from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
import learn
from calendar import day_abbr
from datetime import datetime
import parsedatetime

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/gmail-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/gmail.readonly'
CLIENT_SECRET_FILE = '../client_secret.json'
APPLICATION_NAME = 'Gmail API Python Quickstart'


def get_credentials():
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'gmail-python-quickstart.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

def calculatePriority(stats,entry):
    emailFrom = entry['from']
    emailSpam = entry['spam']
    num_msg=stats['num_messages']
    if emailSpam == -1:
        return 2
    elif emailSpam < 0.1:
        return 1
    elif stats['from'][emailFrom] >= num_msg*0.1 or emailSpam >= 0.1:
        return 3
    else:
        return 2


def countFrequency(dict, key, value):
    if dict[key].get(value, False) is False:
        dict[key][value] = 1
    else:
        count = dict[key][value] + 1
        dict[key][value] = count


def top_entries(dict, num):
    return sorted(dict, key=dict.get, reverse=True)[:num]


def main():
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('gmail', 'v1', http=http)

    # two_weeks_ago = datetime.utcnow() - timedelta(days=14)
    # two_weeks_ago = (two_weeks_ago - datetime.utcfromtimestamp(0)).total_seconds()*1000
    # print (two_weeks_ago)

    results = service.users().messages().list(userId='me', maxResults=1000, q="newer_than:30d").execute()
    messages = results.get('messages', [])
    NUM_MESSAGES = len(messages)
    print(NUM_MESSAGES)

    dataset = {}
    stats = {'num_messages': NUM_MESSAGES, 'from': {}, 'spam': {}, 'priority': {}}
    from_encode = {}
    from_id = 1
    for message in messages:
        message_req = service.users().messages().get(userId='me', id=message['id']).execute()
        m_id = message_req['id']
        spamProb = -1.0
        for item in message_req['payload']['headers']:
            if item['name'] == 'From':
                emailFrom = item.get('value')
            elif item['name'] == 'Date':
                emailDate = str(item.get('value')) #Fri, 28 Apr 2017 00:01:56 +0000
                cal = parsedatetime.Calendar()
                # result = cal.parse(emailDate)[0][:10]
                # print(result)
                helper = emailDate.split(' ')
                helper.pop()
                while ':' not in helper[-1]:
                    helper.pop()
                helper = ' '.join(helper)
                if ',' in helper:
                    date = datetime.strptime(helper, '%a, %d %b %Y %H:%M:%S')
                elif helper[0] not in list(day_abbr):
                    date = datetime.strptime(helper, '%d %b %Y %H:%M:%S')
                else:
                    date = datetime.strptime(helper, '%a %d %b %Y %H:%M:%S')
                emailHour = date.hour
                emailDay = date.weekday
                # print(emailDate)
                # print(emailDay)
                # print(emailHour)


            elif item['name'] == 'Subject':
                emailSubject = item.get('value')
            elif item['name'] == 'SpamDiagnosticOutput':
                emailSpamDiagnosticOutput = item.get('value').split(':')
                spamProb = float(emailSpamDiagnosticOutput[0])/float(emailSpamDiagnosticOutput[1])

        dataset[m_id] = {'labelIDs': len(message_req['labelIds']),
                         'day': emailDay,
                         'hour': emailHour,
                         'from': emailFrom,
                         'subject': len(emailSubject),
                         'spam': spamProb
                         }

        countFrequency(stats, 'from', emailFrom)
        countFrequency(stats, 'spam', spamProb)

        for item in stats['from']:
            from_encode[item] = from_id
            from_id += 1


    for message in messages:
        message_req = service.users().messages().get(userId='me', id=message['id']).execute()
        m_id = message_req['id']
        dataset[m_id]['notification_priority'] = calculatePriority(stats, dataset[m_id])
        countFrequency(stats, 'priority', dataset[m_id]['notification_priority'])

    print(stats)
    print(dataset)


    model = learn.createModel(dataset, from_encode)



if __name__ == '__main__':
    main()