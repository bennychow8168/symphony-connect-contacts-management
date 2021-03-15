# Symphony Connect Contacts Management

## Overview
This Python script allows you to add / update / remove contacts to the Symphony WeChat & WhatsApp Connect.
Contacts who are added to the WeChat & WhatsApp Connect will be able to connect and communicate with Symphony users via the selected network (e.g WeChat / WhatsApp).

The script will be able to perform the following:
- Add contacts to a single / multiple advisors on Symphony
- Update contacts from a single / multiple advisors
- Remove contacts from a single / multiple advisors

The script expects a CSV file as input.
Upon completion, the script will produce an CSV file as output containing the results.

The input and output file names can be adjusted at the top of the script. 

    # Input/Output File Names
    INPUT_FILE = 'contact_mgmt_input.csv'
    OUTPUT_FILE = 'contact_mgmt_output.csv'

## Input CSV Columns
The script expects an input CSV file at the top directory where the script runs with filename - ``contact_mgmt_input.csv``

The CSV file will contain following columns:
- ExternalNetwork (``WECHAT`` / ``WHATSAPP``)
- ContactAction (``ADD`` / ``UPDATE`` / ``DELETE``)
- ContactFirstName
- ContactLastName
- ContactCompany
- ContactEmail
- ContactPhone
- AdvisorEmailList (List of Symphony Users / advisors who will connect with this contact - multiple emails possible - separated by ``~``)

Example input CSV file

    ExternalNetwork,ContactAction,ContactFirstName,ContactLastName,ContactCompany,ContactEmail,ContactPhone,AdvisorEmailList
    WHATSAPP,ADD,John,Doe,Acme Pte Ltd,john.doe@gmail.com,+6598984545,john.smith@symphony.com~mike.smith@symphony.com
    WHATSAPP,UPDATE,John,Doe,Acme Pte Ltd,john.doe@gmail.com,+6598984545,john.smith@symphony.com~mike.smith@symphony.com
    WHATSAPP,DELETE,John,Doe,Acme Pte Ltd,john.doe@gmail.com,+6598984545,john.smith@symphony.com~mike.smith@symphony.com
    WECHAT,ADD,John,Doe,Acme Pte Ltd,john.doe@gmail.com,+6598984545,john.smith@symphony.com~mike.smith@symphony.com


## Output CSV Columns
The output file will be saved in the same directory as the input file with filename - ``contact_mgmt_output.csv``

Columns will be same as Input CSV above, with additional of **Status** column.

Successful entries will be marked with status = OK. Otherwise, error / more info will be displayed


## Environment Setup
This client is compatible with **Python 3.6 or above**

Create a virtual environment by executing the following command **(optional)**:
``python3 -m venv ./venv``

Activate the virtual environment **(optional)**:
``source ./venv/bin/activate``

Install dependencies required for this client by executing the command below.
``pip install -r requirements.txt``


## Getting Started
### 1 - Prepare RSA Key pair
You will first need to generate a **RSA Public/Private Key Pair**.
- Send the **Public** key to Symphony Support Team in order to set up 
- Private Key will be required in steps below
- In return, Symphony team will provide a publicKeyID which you will need to populate in the config.json file below


### 2 - Upload Service Account Private Key
Please copy the private key file (*.pem) to the **rsa** folder. You will need to configure this in the next step.


### 3 - Update resources/connect_config.json

To run the script, you will need to configure **connect_config.json** provided in the **resources** directory. 

**Notes:**

You also need to update based on the service account created above:
- wechat_apiURL / whatsapp_apiURL (please confirm this with Symphony team)
- privateKeyPath (ends with a trailing "/"))
- privateKeyName
- wechat_publicKeyId /  whatsapp_publicKeyId (please confirm this with Symphony team)
- podId (please confirm this with Symphony team)


Sample:

    {
      "wechat_apiURL": "wcgw-uat.symphony.com/wechatgateway",
      "whatsapp_apiURL": "connect.uat.symphony.com/admin",
      "privateKeyPath":"./rsa/",
      "privateKeyName": "connect-privateKey.pem",
      "wechat_publicKeyId": "develop2-uat",
      "whatsapp_publicKeyId": "develop2-uat",
      "podId": "5119",
      "proxyURL": "",
      "proxyUsername": "",
      "proxyPassword": "",
      "truststorePath": ""
    }



### 5 - Run script
The script can be executed by running
``python3 main.py`` 



# Release Notes

## 0.1
- Initial Release

