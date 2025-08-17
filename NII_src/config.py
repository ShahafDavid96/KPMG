# config.py
import os
from pathlib import Path
from dotenv import load_dotenv
from pydantic import BaseModel, Field, field_validator
import re

# Load environment variables from a .env file if it exists
load_dotenv()

# --- Azure Document Intelligence ---
DOCUMENTINTELLIGENCE_ENDPOINT = os.getenv("DOCUMENTINTELLIGENCE_ENDPOINT")
DOCUMENTINTELLIGENCE_API_KEY = os.getenv("DOCUMENTINTELLIGENCE_API_KEY")

# --- Azure OpenAI ---
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
AZURE_OPENAI_API_VERSION = "2024-02-01"

# --- Prompt Configuration ---
SYSTEM_PROMPT_PATH = Path(__file__).with_name("prompt.txt")

# --- Target JSON Schemas (Pydantic for type-safety) ---

# --- English Schema ---
class DateModelEN(BaseModel):
    day: str = ""
    month: str = ""
    year: str = ""

class AddressModelEN(BaseModel):
    street: str = ""
    houseNumber: str = ""
    entrance: str = ""
    apartment: str = ""
    city: str = ""
    postalCode: str = ""
    poBox: str = ""

class MedicalInstitutionModelEN(BaseModel):
    healthFundMember: str = ""
    natureOfAccident: str = ""
    medicalDiagnoses: str = ""

class FormSchemaEN(BaseModel):
    lastName: str = ""
    firstName: str = ""
    idNumber: str = ""
    gender: str = ""
    dateOfBirth: DateModelEN = Field(default_factory=DateModelEN)
    address: AddressModelEN = Field(default_factory=AddressModelEN)
    landlinePhone: str = ""
    mobilePhone: str = ""
    jobType: str = ""
    dateOfInjury: DateModelEN = Field(default_factory=DateModelEN)
    timeOfInjury: str = ""
    accidentLocation: str = ""
    accidentAddress: str = ""
    accidentDescription: str = ""
    injuredBodyPart: str = ""
    signature: str = ""
    formFillingDate: DateModelEN = Field(default_factory=DateModelEN)
    formReceiptDateAtClinic: DateModelEN = Field(default_factory=DateModelEN)
    medicalInstitutionFields: MedicalInstitutionModelEN = Field(default_factory=MedicalInstitutionModelEN)

    @field_validator('idNumber')
    @classmethod
    def validate_id_number(cls, v: str) -> str:
        if v and not re.fullmatch(r'\d{9}', v):
            # We can raise a ValueError, but for this app, we'll just note it.
            # For strict validation, you would raise ValueError("Invalid Israeli ID number")
            print(f"Validation Warning: ID '{v}' is not 9 digits.")
        return v

# --- Hebrew Schema (uses aliases to map to the same English field names) ---
class DateModelHE(DateModelEN):
    day: str = Field("", alias="יום")
    month: str = Field("", alias="חודש")
    year: str = Field("", alias="שנה")

class AddressModelHE(AddressModelEN):
    street: str = Field("", alias="רחוב")
    houseNumber: str = Field("", alias="מספר בית")
    entrance: str = Field("", alias="כניסה")
    apartment: str = Field("", alias="דירה")
    city: str = Field("", alias="ישוב")
    postalCode: str = Field("", alias="מיקוד")
    poBox: str = Field("", alias="תא דואר")

class MedicalInstitutionModelHE(MedicalInstitutionModelEN):
    healthFundMember: str = Field("", alias="חבר בקופת חולים")
    natureOfAccident: str = Field("", alias="מהות התאונה")
    medicalDiagnoses: str = Field("", alias="אבחנות רפואיות")

class FormSchemaHE(FormSchemaEN):
    lastName: str = Field("", alias="שם משפחה")
    firstName: str = Field("", alias="שם פרטי")
    idNumber: str = Field("", alias="מספר זהות")
    gender: str = Field("", alias="מין")
    dateOfBirth: DateModelHE = Field(default_factory=DateModelHE, alias="תאריך לידה")
    address: AddressModelHE = Field(default_factory=AddressModelHE, alias="כתובת")
    landlinePhone: str = Field("", alias="טלפון קווי")
    mobilePhone: str = Field("", alias="טלפון נייד")
    jobType: str = Field("", alias="סוג העבודה")
    dateOfInjury: DateModelHE = Field(default_factory=DateModelHE, alias="תאריך הפגיעה")
    timeOfInjury: str = Field("", alias="שעת הפגיעה")
    accidentLocation: str = Field("", alias="מקום התאונה")
    accidentAddress: str = Field("", alias="כתובת מקום התאונה")
    accidentDescription: str = Field("", alias="תיאור התאונה")
    injuredBodyPart: str = Field("", alias="האיבר שנפגע")
    signature: str = Field("", alias="חתימה")
    formFillingDate: DateModelHE = Field(default_factory=DateModelHE, alias="תאריך מילוי הטופס")
    formReceiptDateAtClinic: DateModelHE = Field(default_factory=DateModelHE, alias="תאריך קבלת הטופס בקופה")
    medicalInstitutionFields: MedicalInstitutionModelHE = Field(default_factory=MedicalInstitutionModelHE, alias='למילוי ע"י המוסד הרפואי')