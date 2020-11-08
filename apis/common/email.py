import boto3


def SendEmail(to, subject, message=None, html_body=None, bcc_address=[]):
    from_email = "no.reply@uiflo.com"

    ses_client = boto3.client(
        'ses',
        aws_access_key_id="AKIAR4KAVVLXAXFOT4VC",
        aws_secret_access_key="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",
        region_name="ap-south-1"
    )
    CHARSET = "UTF-8"
    Message = {
        'Body': {},
        'Subject': {
            'Charset': CHARSET,
            'Data': subject,
        },
    }
    if html_body:
        Message['Body']['Html'] = {'Charset': CHARSET, 'Data': html_body}
    if message:
        Message['Body']['Text'] = {'Charset': CHARSET, 'Data': message}

    Destination = {
        'ToAddresses': to,
        'BccAddresses': bcc_address
    }
    ses_client.send_email(Source=from_email, Message=Message, Destination=Destination)

    return {"success": 1}