
import boto3
import StringIO
import zipfile
import mimetypes

def lambda_handler(event, context):
    s3 = boto3.resource('s3')
    sns = boto3.resource('sns')
    topic = sns.Topic('arn:aws:sns:eu-west-2:268054990449:Deploy-RG-Portfolio')

    try:
        portfolio_bucket = s3.Bucket('portfolio.rgregson.info')
        build_bucket = s3.Bucket('portfoliobuild.rgregson.info')

        portfolio_zip = StringIO.StringIO()
        build_bucket.download_fileobj('rgportfoliobuild.zip', portfolio_zip)

        with zipfile.ZipFile(portfolio_zip) as myzip:
            for nm in myzip.namelist():
                obj = myzip.open(nm)
                portfolio_bucket.upload_fileobj(obj, nm,
                    ExtraArgs={'ContentType': mimetypes.guess_type(nm)[0]})
                portfolio_bucket.Object(nm).Acl().put(ACL='public-read')

        print "Job Done!"
        topic.publish(Subject='RG Portfolio', Message='Portfolio deployed succesfully')
    except:
        topic.publish(Subject='RG Portfolio Deployment Failure', Message='Portfolio NOT deployed succesfully')
        raise


    return 'Hello from Lambda'
