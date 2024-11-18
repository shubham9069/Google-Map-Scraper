import csv
import requests
import json

def convert_json_to_csv(data, filepath):
    with open(filepath, 'a', newline='') as data_file:
        csv_writer = csv.writer(data_file)
        for obj in data:
            csv_writer.writerow(obj.values())
    print("Data successfully save in excel")
    pass


def read_csv(filepath):
    with open(filepath, 'r') as file:
        reader = csv.reader(file)
        data = list(reader)
    return data

def create_csv_file(data, filepath):
    with open(filepath, 'w', newline='') as data_file:
        pass



    
    
