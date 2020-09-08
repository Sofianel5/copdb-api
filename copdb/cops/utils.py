import pandas
import json
from datetime import datetime
from .models import *
from django.conf import settings
import gender_guesser.detector as gender
import requests
from django.db.utils import IntegrityError

def import_ccrb_csv():
    data = pandas.read_csv("cops/data/CCRB_database_raw.csv").transpose()
    data = data.where(pandas.notnull(data), None)
    command_options = json.load(open("cops/data/command_options_nypd.json"))
    rank_options = json.load(open("cops/data/rank_options_nypd.json"))
    d = gender.Detector(case_sensitive=False)
    for obj in data:
        obj = data[obj]
        if obj["ShieldNo"] == 0:
            obj["ShieldNo"] = None
        if obj["First Name"] is None or obj["Last Name"] is None:
            continue
        if Cop.objects.filter(first_name=obj["First Name"], last_name=obj["Last Name"], badge_number=obj["ShieldNo"]).exists():
            cop = Cop.objects.get(
                first_name=obj["First Name"], 
                last_name=obj["Last Name"], 
                badge_number=obj["ShieldNo"]
            )
        else:
            if obj["Command"] in command_options:
                command = command_options[obj["Command"]]
            else:
                command = obj["Command"]
            if obj["Rank"] in rank_options:
                rank = rank_options[obj["Rank"]]
            else:
                rank = obj["Rank"]
            sex = d.get_gender(obj["First Name"])
            if "female" in sex:
                ans_sex = "F"
            elif "male" in sex:
                ans_sex = "M"
            else:
                ans_sex = "U"
            cop = Cop.objects.create(
                first_name=obj["First Name"], 
                last_name=obj["Last Name"], 
                rank=rank,
                badge_number=obj["ShieldNo"],
                precinct=Precinct.objects.filter(name=command).first(),
                police_department=PoliceDepartment.objects.get(),
                sex=ans_sex
            )
        if obj["Incident Date"] is not None and obj["FADO Type"] is not None and obj["Allegation"] is not None:
            date = datetime.strptime(obj["Incident Date"], "%m/%d/%Y")
            if not Complaint.objects.filter(
                cop=cop,
                abuse_type=obj["FADO Type"],
                allegation=obj["Allegation"],
                date_recieved__month=date.month, 
                date_recieved__year=date.year).exists():
                Complaint.objects.create(
                    abuse_type=obj["FADO Type"],
                    allegation=obj["Allegation"],
                    cop=cop,
                    date_recieved=date,
                    outcome=obj["PenaltyDesc"],
                    finding=obj["Board Disposition"],
                )
            else:
                continue

def make_ccrb_human_readable():
    with open("cops/data/command_options_nypd.json") as json_file:
        data = json.load(json_file)
        for cop in Cop.objects.all():
            try:
                cop.precinct = data[cop.precinct]
                cop.save()
            except KeyError:
                continue
    with open("cops/data/rank_options_nypd.json") as json_file:
        data = json.load(json_file)
        for cop in Cop.objects.all():
            try:
                cop.rank = data[cop.rank]
                cop.save()
            except KeyError:
                continue

def generate_precincts():   
    df = pandas.read_excel("cops/data/parsed_precints.xlsx")
    df = df.transpose()
    df = df.where(pandas.notnull(df), None)
    GOOGLE_KEY = settings.GOOGLE_KEY
    for i in df:
        data = df[i]
        if data["address"] is None:
            print(f"Empty: {data['Command Name']}")
        if Precinct.objects.filter(name=data["Command Name"]).count() == 0:
            try: 
                if data["lat"] == 0 or data["lng"] == 0:
                    request = requests.get(f"https://maps.googleapis.com/maps/api/geocode/json?address={data['address']}&key={GOOGLE_KEY}")
                    response = dict(request.json())
                    coordinates = response['results'][0]['geometry']['location']
                    obj, _ = Coordinates.objects.get_or_create(lat=coordinates['lat'], lng=coordinates['lng'])
                    obj.save()
                else:
                    obj, _ = Coordinates.objects.get_or_create(lat=data['lat'], lng=data['lng'])
                    obj.save()
                res = Precinct.objects.create(
                    name=data["Command Name"],
                    police_department=PoliceDepartment.objects.get(),
                    coordinates=obj,
                    address=obj.to_address()
                )
            except Exception as e:
                print(f"Failed: {data['Command Name']}")
                print(e)

def attach_precincts():
    for cop in Cop.objects.all():
        try:
            cop.p = Precinct.objects.get(name=cop.precinct)
            cop.save()
        except Precinct.DoesNotExist:
            cop.description = f"Works in {cop.precinct}."
            cop.save()

def save_police():
    data = pandas.read_csv("cops/data/police_officer.csv").transpose()
    for i in data:
        try:
            obj = data[i]
            obj["First Name"] = obj["First Name"].lower().capitalize()
            obj["Last Name"] = obj["Last Name"].lower().capitalize()
            if not Cop.objects.filter(first_name=obj["First Name"], last_name=obj["Last Name"]).exists():
                Cop.objects.create(first_name=obj["First Name"], last_name=obj["Last Name"], police_department=PoliceDepartment.objects.get())
        except AttributeError:
            print(obj["First Name"], obj["Last Name"])