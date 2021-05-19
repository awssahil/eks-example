import json
import boto3
import logging
import datetime
import time

ssm = boto3.client('ssm')
sns = boto3.client('sns')

LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)



def lambda_handler(event, context):

    print ("############### LAMBDA fautomation-log-consolidation STARTED ###########")
    #step one
    #get execution id from event parameter
    aggregatemessage = ""
    executionId = event['executionId']
    topicARN = event['topicARN'] 

    #step2
    #replace AutomationExecutionId with parameter 
    response = ssm.describe_automation_step_executions(AutomationExecutionId=executionId)
    time.sleep(2)
    status = ssm.get_automation_execution(AutomationExecutionId=executionId)
    #step3
    #send response varible to sns
    message = response['StepExecutions']
    overallstatus = status['AutomationExecution']
    aggregatemessage = "%sAutomationExecutionId: %s \n" % (aggregatemessage, str(overallstatus['AutomationExecutionId']))
    aggregatemessage = "%sOverall Execution Status: %s \n" % (aggregatemessage, str(overallstatus['AutomationExecutionStatus']))
    print(aggregatemessage)
    aggregatemessage = "%s########################################################\n" % (aggregatemessage)
    for step in message:
        if step['StepStatus'] == 'Success' or step['StepStatus'] == 'Pending':
            aggregatemessage = "%sStepName: %s\n" % (aggregatemessage, step['StepName'])
            aggregatemessage = "%sStepStatus: %s\n" % (aggregatemessage, step['StepStatus'])
        else:
            for item in step:
                aggregatemessage = "%s%s: %s\n" % (aggregatemessage, item, step.get(item))
        aggregatemessage = "%s#########################################################\n" % (aggregatemessage)
    print(aggregatemessage)    
        
    sns.publish(
        TopicArn=topicARN,
        Message=aggregatemessage,
        Subject='Automation Log Consolidation'
    )
    
    return {
        'statusCode': 200,
        'body': json.dumps(aggregatemessage)
    }
