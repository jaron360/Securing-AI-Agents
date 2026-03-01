"""
Lambda function to run the security agent on a schedule
Deploy this with EventBridge to run daily
"""
import json
import boto3
from datetime import datetime
from agent import run_security_check

sns_client = boto3.client('sns')
SNS_TOPIC_ARN = 'arn:aws:sns:us-west-2:ACCOUNT_ID:security-incidents'

def lambda_handler(event, context):
    """
    Lambda handler for scheduled security checks
    """
    try:
        print(f"Starting security check at {datetime.now()}")
        
        # Run the security agent
        report = run_security_check()
        
        # Send report via SNS
        sns_client.publish(
            TopicArn=SNS_TOPIC_ARN,
            Subject=f'Daily Security Incident Report - {datetime.now().strftime("%Y-%m-%d")}',
            Message=report
        )
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Security check completed successfully',
                'timestamp': datetime.now().isoformat(),
                'report_sent': True
            })
        }
    
    except Exception as e:
        print(f"Error running security check: {str(e)}")
        
        # Send error notification
        sns_client.publish(
            TopicArn=SNS_TOPIC_ARN,
            Subject='ERROR: Security Agent Failed',
            Message=f'Security agent encountered an error: {str(e)}'
        )
        
        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': 'Security check failed',
                'error': str(e)
            })
        }
