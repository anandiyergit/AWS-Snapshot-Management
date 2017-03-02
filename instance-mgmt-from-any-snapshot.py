import boto3
import json
import pprint

# author : aniyer

##Allows the user to go back to the older snapshots.##
##Requires snapshot-ids and instance-ids as I/P##
##Make sure the number of instance-ids and snapshoy-ids are same and in identical position##
##Just to claarify the above sentence it means snapshotID[0]==instanceID[0]##

# Define the client as ec2.
client = boto3.client('ec2')

#  Initialization
pp = pprint.PrettyPrinter(indent=4)

###########################################################################################
def createVolume(snapshotID):
    print "About to create volume with snapshotID = '%s' " %(snapshotID)
    volume = client.create_volume(
    DryRun=False,
    Size=150,
    SnapshotId=snapshotID,
    AvailabilityZone='us-west-2a',
    VolumeType='gp2',
    Encrypted=False
)
    #pp.pprint(volume)
    new_volume = volume ["VolumeId"]
    print "Created volume with VolumeID= '%s'" %new_volume
    return new_volume

###########################################################################################
def describeVolume(instanceID):
    desc_volume = client.describe_volumes(
    VolumeIds=[],
    Filters=[
        {
            'Name': 'status',
            'Values': [
                'in-use',
            ]
        },
        {
            'Name': 'attachment.instance-id',
            'Values': [
                instanceID,
            ]
        },
    ],
)
    #pp.pprint(desc_volume)
    old_volume = desc_volume["Volumes"][0]["VolumeId"]
    instance_id = desc_volume["Volumes"][0]["Attachments"][0]["InstanceId"]
    print "Volume='%s', instance_id = '%s' and State='%s'" %(old_volume , instance_id ,desc_volume ["Volumes"][0]["State"])
    return old_volume 


###########################################################################################
def fetchInstanceIDForInUseVolume(snapshotID):
    desc_volume = client.describe_volumes(
    VolumeIds=[],
    Filters=[
        {
            'Name': 'status',
            'Values': [
                'in-use',
            ]
        },
        {
            'Name': 'snapshot-id',
            'Values': [
                snapshotID,
            ]
        },
    ],
)
    #pp.pprint(desc_volume)
    instance_id = desc_volume["Volumes"][0]["Attachments"][0]["InstanceId"]
    return instance_id

###########################################################################################
def detachVolume(old_volume, snapshotID):
    print "About to detach in-use volume '%s' with snapshotID = '%s' " %(old_volume , snapshotID)
    detach_volume = client.detach_volume(
    VolumeId=old_volume,
    Force=False
)
    #pp.pprint(detach_volume)
    print "Detached volume '%s' with snapshotID = '%s' " %(old_volume , snapshotID)
    return detach_volume

###########################################################################################
def stableVolumeState(detach_volume,old_volume, new_volume):
    while (detach_volume ["State"] != "detached"):
        old_desc_volume = client.describe_volumes(
        VolumeIds=[old_volume],
        )
        new_desc_volume = client.describe_volumes(
        VolumeIds=[new_volume],
        )
        print "For Volume='%s' current State='%s'" %(old_volume , old_desc_volume ["Volumes"][0]["State"])
        print "For Volume='%s' current State='%s'" %(new_volume , new_desc_volume ["Volumes"][0]["State"])
        if ((old_desc_volume ["Volumes"][0]["State"] == 'available') and (new_desc_volume ["Volumes"][0]["State"] == 'available')):
            break
        
        print "Volume '%s' has been successfully detached with state '%s'" %(old_volume, old_desc_volume ["Volumes"][0]["State"])
        print "Volume '%s' will be attached with state '%s'" %(new_volume, new_desc_volume ["Volumes"][0]["State"])
        return True

###########################################################################################
def attachVolume(new_volume,snapshotID,instance_id):
    print "About to attach volume with snapshotID = '%s' and InstanceID= '%s'" %(snapshotID,instance_id)
    attached_volume = client.attach_volume(
    VolumeId=new_volume,
    InstanceId=instance_id ,
    Device='/dev/sda1'
)
    #pp.pprint(attached_volume)
    print "Attached volume with VolumeID = '%s', snapshotID = '%s' and InstanceID= '%s'" %(new_volume,snapshotID,instance_id)
    return True

###########################################################################################
def deleteVolume(old_volume):
    print "About to delete old volume '%s' as part of cleanup !" %(old_volume)
    del_volume = client.delete_volume(
    VolumeId=old_volume
)
    #pp.pprint(del_volume)
    print "Deleted old volume '%s'" %(old_volume)

###########################################################################################
def readFile(fileName):
    try:
        text_file = open(fileName, "r")
    
    except:
        print "File '%s' cannot be opened!" %(fileName)
        exit()
    
    instanceIDs = text_file.read().splitlines()
    print "Instances going for snapshots are: '%s'" %(instanceIDs)
    print "Total number of instances for snapshot creation are : '%s'" %(len(instanceIDs))
    text_file.close()
    return instanceIDs

###########################################################################################
def fetchVolumeID(instanceID):
    print "About to fetch the VolumeID for the instance-ID : '%s'" %(instanceID)
    instance = client.describe_instances(
    InstanceIds=[
        instanceID,
    ],
)
    #pp.pprint(instanceID)
    volume_ID = instance ["Reservations"][0]["Instances"][0]["BlockDeviceMappings"][0]["Ebs"]["VolumeId"]
    print "Volume-ID is '%s' for instance-id '%s'" %(volume_ID , instanceID )
    return volume_ID

###########################################################################################
def detachVolume(old_volume):
    print "About to detach in-use volume '%s'" %(old_volume)
    detach_volume = client.detach_volume(
    VolumeId=old_volume,
    Force=False
)
    #pp.pprint(detach_volume)
    print "Detached volume '%s'" %(old_volume)
    return detach_volume

############################################## Main Program Starts Here #############################################

## Query snapshots from a text file
snapshotFileName = "snapshots.txt"

## Query instances from a text file
instanceFileName = "All-Instances.txt"

## Return list of snapshots from the file
snaphotIDs = readFile(snapshotFileName)

## Return list of instances from the file
instanceIDs = readFile(instanceFileName)

#snaphotIDs = ['snap-6494e557']
for index in range(len(snaphotIDs)):
    snapshotID = snaphotIDs[index]
    instanceID = instanceIDs[index]
    print 'Current snapshot :', snaphotIDs[index]
    print 'Current instance :', instanceIDs[index]

    # Create Volume with the snapshot
    new_volume = createVolume(snapshotID)

    # Fetch Volume
    volumeID = fetchVolumeID(instanceID)

    # describe Volume
    old_volume = describeVolume(instanceID)
    
    # describe Volume
    #old_volume = describeVolume(snapshotID)
    #instance_id = fetchInstanceIDForInUseVolume(snapshotID)

    # Detach Old Volume
    #detach_volume = detachVolume(old_volume, snapshotID)
    detach_volume = detachVolume(volumeID)

    # Check whether the old volume is completely detached.
    while (detach_volume ["State"] != "detached"):
        old_desc_volume = client.describe_volumes(
        VolumeIds=[old_volume],
        )
        new_desc_volume = client.describe_volumes(
        VolumeIds=[new_volume],
        )
        print "For Volume='%s' current State='%s'" %(old_volume , old_desc_volume ["Volumes"][0]["State"])
        print "For Volume='%s' current State='%s'" %(new_volume , new_desc_volume ["Volumes"][0]["State"])
        if ((old_desc_volume ["Volumes"][0]["State"] == 'available') and (new_desc_volume ["Volumes"][0]["State"] == 'available')):
            break
            
    print "Volume '%s' has been successfully detached with state '%s'" %(old_volume, old_desc_volume ["Volumes"][0]["State"])
    print "Volume '%s' will be attached with state '%s'" %(new_volume, new_desc_volume ["Volumes"][0]["State"])
    #    return True
    #isVolumeStateStable = stableVolumeState(detach_volume,old_volume, new_volume)

    # Attach New Volume
    isAttached = attachVolume(new_volume,snapshotID,instanceID)

    #Delete old volume
    isDeleted = deleteVolume(old_volume)

    print "We are done with restoring the snapshot '%s'" %(snapshotID)

print "We are done with restoring for all the given snapshots!!"

############################################## Main Program Ends Here #############################################
