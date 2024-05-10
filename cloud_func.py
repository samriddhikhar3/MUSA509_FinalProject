import functions_framework
import base64
import json
from google.cloud import bigquery
from datetime import datetime
from geopy.distance import geodesic
from google.cloud import storage

def find_matching_pairs(data):
    matching_pairs = []

    for i, user1 in enumerate(data):
        for user2 in data[i+1:]:
            # Convert timestamps to datetime objects  
            if isinstance(user1['Timestamp'], str):
                timestamp1 = datetime.strptime(user1['Timestamp'], '%Y-%m-%d %H:%M:%S')
                timestamp2 = datetime.strptime(user2['Timestamp'], '%Y-%m-%d %H:%M:%S')
            else:
                timestamp1 = user1['Timestamp']
                timestamp2 = user2['Timestamp']

            # Calculate time difference in minutes
            time_diff = abs((timestamp2 - timestamp1).total_seconds() / 60)
            
            # Calculate distance between users' locations
            user1_location = (user1['Latitude'], user1['Longitude'])
            user2_location = (user2['Latitude'], user2['Longitude'])
            distance = geodesic(user1_location, user2_location).miles
            
            # Check if users are within 30 minutes, 0.5 miles, and have at least one matching interest
            if time_diff <= 60 and distance <= 1 and any(interest in user1.values() for interest in user2.values()):
                matching_pairs.append({'user1_id': user1['UserID'], 'user2_id': user2['UserID']})

    return matching_pairs

@functions_framework.http
def process_data(request):
    # Initializing BigQuery client
    project_id= 'musa509-final-project-sk-mh'
    client = bigquery.Client(project=project_id)

    # Fetching data from BigQuery
    query = """
    SELECT UserID, Latitude, Longitude, Timestamp, Interest1, Interest2, Interest3
    FROM `musa509-final-project-sk-mh.user_data.user_data_table`
    """
    query_job = client.query(query)
    rows = query_job.result()

    # Processing data and finding matching user pairs
    data_from_bigquery = []
    for row in rows:
        data_from_bigquery.append(dict(row))

    matching_pairs = find_matching_pairs(data_from_bigquery)

    # Saving output JSON to Cloud Storage
    # Specify your Cloud Storage bucket and object name
    bucket_name = "musa509-final-project-sk-mh"
    object_name = "matching_pairs.json"
    
    # Initialize a Cloud Storage client
    storage_client = storage.Client()
    
    # Get the bucket
    bucket = storage_client.bucket(bucket_name)
    
    # Create a blob (file) in the bucket
    blob = bucket.blob(object_name)
    
    # Upload the JSON data to the blob
    blob.upload_from_string(json.dumps(matching_pairs))
    
    # Return a response if needed
    return "Output JSON saved to Cloud Storage."

     # Write matching pairs to a CSV file
    csv_data = [
        ["UserID_1", "UserID_2", "Latitude_1", "Longitude_1", "Latitude_2", "Longitude_2"]
    ]
    for pair in matching_pairs:
        csv_data.append([
            pair["UserID_1"],
            pair["UserID_2"],
            pair["Latitude_1"],
            pair["Longitude_1"],
            pair["Latitude_2"],
            pair["Longitude_2"]
        ])

    csv_string = '\n'.join([','.join(row) for row in csv_data])
    csv_blob = bucket.blob(csv_object_name)
    csv_blob.upload_from_string(csv_string)

    # Return a response if needed
    return "Output JSON and CSV saved to Cloud Storage."
