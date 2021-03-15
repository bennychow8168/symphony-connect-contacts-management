import csv, sys, traceback
from modules.connectApiClient import ConnectApiClient
from modules.connectConfigure import ConnectConfig

# Input/Output File Names
INPUT_FILE = 'contact_mgmt_input.csv'
OUTPUT_FILE = 'contact_mgmt_output.csv'


def main():
    print('Start Processing...')

    # Init Connect API Client
    connect_config = ConnectConfig('./resources/connect_config.json')
    connect_config.load_config()
    connect_client = ConnectApiClient(connect_config)

    # Now process CSV file
    # CSV file will have 8 columns - ExternalNetwork,ContactAction,ContactFirstName,ContactLastName,ContactCompany,ContactEmail,ContactPhone,AdvisorEmailList
    process_result = []
    with open(INPUT_FILE, newline='') as csvfile:
        csv_list = csv.reader(csvfile, delimiter=',')
        for row in csv_list:
            # Ignore blank rows
            if len(row) == 0:
                continue

            # Ensure CSV has 8 columns
            if len(row) !=8 :
                raise Exception(
                    'Invalid CSV File Format - Expect 8 columns - ExternalNetwork, ContactAction, ContactFirstName, ContactLastName, ContactCompany, ContactEmail, ContactPhone, AdvisorEmailList')

            # Skip header row
            if row[0] == "ExternalNetwork":
                continue

            result_record = dict()
            # Get row values
            result_record['result'] = ''
            result_record['external_network'] = row[0].upper()
            result_record['action'] = row[1].upper()
            result_record['first_name'] = row[2].lstrip().rstrip()
            result_record['last_name'] = row[3].lstrip().rstrip()
            result_record['company'] = row[4].lstrip().rstrip()
            result_record['contact_email'] = row[5].lower()
            result_record['phone'] = row[6]
            result_record['advisorEmailList'] = row[7].lower()

            # Check if valid External Network
            if result_record['external_network'] not in ("WECHAT", "WHATSAPP"):
                result_record['result'] = 'ERROR - Invalid External Network - SKIPPED'
                process_result.append(result_record)
                continue

            # Check if valid Action
            if result_record['action'] not in ("ADD", "UPDATE", "DELETE"):
                result_record['result'] = 'ERROR - Invalid Contact Action - SKIPPED'
                process_result.append(result_record)
                continue

            # If Email is blank, then SKIP
            if result_record['contact_email'] is None or result_record['contact_email'] == '':
                result_record['result'] = f'ERROR - Contact Email field is not populated - SKIPPED'
                process_result.append(result_record)
                continue

            # Check and split advisor email list
            advisor_email_list = []
            if result_record['advisorEmailList'] is None or result_record['advisorEmailList'] == '':
                result_record['result'] = f'ERROR - Advisor Email List field is not populated - SKIPPED'
                process_result.append(result_record)
                continue
            else:
                advisor_email_list = result_record['advisorEmailList'].split("~")


            # Add Contact
            if result_record['action'] == "ADD":
                print(f"Add Contact {result_record['contact_email']} for {advisor_email_list}")
                try:
                    status, result = connect_client.add_contact(result_record['external_network'], result_record['first_name'], result_record['last_name'], result_record['contact_email'], result_record['phone'], result_record['company'], advisor_email_list)
                    result_record['result'] = f'{status} - {result} '

                except Exception as ex:
                    exInfo = sys.exc_info()
                    print(f" ##### ERROR WHILE ADDING CONTACT {result_record['contact_email']} #####")
                    print('Stack Trace: ' + ''.join(traceback.format_exception(exInfo[0], exInfo[1], exInfo[2])))
                    result_record['result'] = 'ERROR ADDING CONTACT - Check logs for details'

            # Update Contact
            if result_record['action'] == "UPDATE":
                for adv_email in advisor_email_list:
                    print(f"Update Contact {result_record['contact_email']} for {adv_email}")
                    try:
                        status, result = connect_client.update_contact(result_record['external_network'], result_record['contact_email'], result_record['first_name'], result_record['last_name'], result_record['company'], result_record['phone'], adv_email)
                        result_record['result'] += f'{adv_email} - {status} - {result} '

                    except Exception as ex:
                        exInfo = sys.exc_info()
                        print(f" ##### ERROR WHILE UPDATING CONTACT {result_record['contact_email']} #####")
                        print('Stack Trace: ' + ''.join(traceback.format_exception(exInfo[0], exInfo[1], exInfo[2])))
                        result_record['result'] = 'ERROR UPDATING CONTACT - Check logs for details'

            # Delete Contact
            if result_record['action'] == "DELETE":
                for adv_email in advisor_email_list:
                    print(f"Delete Contact {result_record['contact_email']} for {adv_email}")
                    try:
                        status, result = connect_client.delete_contact(result_record['external_network'], result_record['contact_email'], adv_email)
                        result_record['result'] += f'{adv_email} - {status} - {result} '

                    except Exception as ex:
                        exInfo = sys.exc_info()
                        print(f" ##### ERROR WHILE DELETING CONTACT {result_record['contact_email']} #####")
                        print('Stack Trace: ' + ''.join(traceback.format_exception(exInfo[0], exInfo[1], exInfo[2])))
                        result_record['result'] = 'ERROR DELETING CONTACT - Check logs for details'

            # Append Result
            process_result.append(result_record)

    # Print final result
    print(f'Generating Result Files...')
    print_result(process_result)


def print_result(process_result):
    with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8-sig') as csvfile:
        fieldnames = ['ExternalNetwork',
                      'ContactAction',
                      'ContactFirstName',
                      'ContactLastName',
                      'ContactCompany',
                      'ContactEmail',
                      'ContactPhone',
                      'AdvisorEmailList',
                      'Status']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for row in process_result:
            writer.writerow(
                {'ExternalNetwork': row['external_network'],
                 'ContactAction': row['action'],
                 'ContactFirstName': row['first_name'],
                 'ContactLastName': row['last_name'],
                 'ContactCompany': row['company'],
                 'ContactEmail': row['contact_email'],
                 'ContactPhone': row['phone'],
                 'AdvisorEmailList': row['advisorEmailList'],
                 'Status': row['result']})

    return

if __name__ == "__main__":
    main()
