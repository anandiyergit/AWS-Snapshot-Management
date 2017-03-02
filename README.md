# AWS-Snapshot-Management
AWS Snapshot is one of the most heavily used for critical operations but the process is very cumbersome and can introduce issues when attaching/detaching volumes

Pre-requisites

Python Installation:-
#1. Install python 2.7.12 from https://www.python.org/downloads/release/python-2712/
#2. Run the installer.
#3. Set Path.
#4. On command prompt follow the steps:-
    python --version


Boto installation
reference:- http://boto3.readthedocs.io/en/latest/guide/quickstart.html
            Open command prompt:-
            pip install boto3

AWS
#1. Download AWS CLI installer for specific to OS.
    http://docs.aws.amazon.com/cli/latest/userguide/installing.html#install-msi-on-windows
#2. Run the installer.
#3. Create access key if secret key is not known.
#4. On command prompt follow the steps:-
    aws --version
    aws configure
    Use access key and secret key
    region 
    rest are default
Reference:-http://docs.aws.amazon.com/cli/latest/userguide/cli-chap-getting-started.html
Verify by running some command to make sure credentials are working

MAIN PROGRAM
For the Snapshot program please follow the below steps:-
#1. All-Instances.txt and snapshots.txt are the inputs for the program.
#2. All the instance Ids will be put into All-Instances.txt. The format should be such that every line should contain only single InstanceID.
#3. All the snapshot Ids will be put into snapshots.txt. The format should be such that every line should contain only single snapshotID.
#4. Also make sure to keep the order cardinality maintained i.e. instanceID[0]=snapshotID[0]. 
