from fastapi import FastAPI,Path,HTTPException,Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel,Field,computed_field
from typing import Literal,Optional
from typing_extensions import Annotated
import pandas as pd
import json


class patient(BaseModel):
    id:Annotated[str,Field(...,description='this is the unique id given to patient must be strig as well')]
    name:Annotated[str,Field(...,description='name of the patient must be string')]
    city: Annotated[str, Field(..., description='City where the patient is living')]
    age:Annotated[int,Field(...,gt=0,lt=100,description='age of the patient')]
    gender:Annotated[Literal['male','female','others'],Field(...,description='gender of the patients')]
    height:Annotated[float,Field(...,gt=0,description='height of the patient')]
    weight:Annotated[float,Field(...,gt=0,description='weight of the patient')]   

    # Store data that is a source of truth. Compute data that is derived from it.
    @computed_field
    @property
    def bmi(self) ->float:
        bmi=round((self.weight/self.height**2),2)
        return bmi

    @computed_field
    @property
    def verdict(self) ->str:

        if self.bmi < 18.5:
            return 'Underweight'
        elif self.bmi < 25:
            return 'Normal'
        elif self.bmi < 30:
            return 'Normal'
        else:
            return 'Obese'
    
      
def load_data():
    with open('patients.json','r') as f:
        data=json.load(f)
    return data

def save_data(data):
    with open('patients.json','w') as f:
        json.dump(data,f,indent=2)

app=FastAPI()

@app.get("/")
def hello():
    return {'message':'Patient Managment API System'}

@app.get('/about')
def about():
    return {'about':'Fully functional patients data'}


@app.get('/view')
def view():
    data=load_data()
    return pd.DataFrame(data)
    

@app.get('/patient/{patient_id}')
def view_patient(patient_id: str = Path(..., description='ID of patient in DB',example='P001')):
    data=load_data()
    if patient_id in data:
        return data[patient_id]
    raise HTTPException(status_code=404,detail="patient ID not found")


@app.get('/sort')
def sort_patient(sort_by:str = Query(...,description='sort on basis of height, name, city'),order:str=Query('asc',description='sort in ascending or descending ordeer')):
    valid_fields=['height','name','city','age']

    if sort_by not in valid_fields:
        raise HTTPException (status_code=400,detail=f'Invalid field select from {valid_fields}')
    
    if order not in ['asc','desc']:
        raise HTTPException(status_code=400,detail="Invalid order select from ['asc','desc']")
    
    data=load_data()
    sort_order=True if (order=='desc') else False
    # sorted_data=sorted(data.values(),key=lambda x:x[sort_by],reverse=sort_order)
    sorted_data=sorted(data.values(),key=lambda x:x.get(sort_by,0),reverse=sort_order)
    return sorted_data

@app.post('/create')
def create_patient(patient:patient):
    #load existing data
    data=load_data()

    #check if the patient already present in the data
    if patient.id in data:
        raise HTTPException(status_code=400,detail='patient already exist')

    #add new patient to data
    data[patient.id]=patient.model_dump(exclude=['id'])

    #save the new patient data 
    save_data(data)

    #raise json response
    return JSONResponse(status_code=201,content='patient created successfully')
