import os
from pymongo import MongoClient
from bson.objectid import ObjectId
from werkzeug.utils import secure_filename


class Applicant:

    def __init__(self, name: str,
                 birthday: str,
                 origin: str,
                 company: str,
                 email: str,
                 languages: list[str],
                 tools: list[str],
                 special_field: str,
                 cv_path: str = None,
                 img_path: str = None):
        self.name = name
        # birthday is in format: DD-MM-YYYY
        self.birthday = birthday
        self.origin = origin
        self.company = company
        self.email = email
        self.languages = languages
        self.tools = tools
        self.special_field = special_field
        self.cv_path = cv_path
        self.img_path = img_path

    @classmethod
    def from_dict(cls, d):
        return cls(**d)
    
    def to_dict(self):
        return {
            "name": self.name,
            "birthday": self.birthday,
            "origin": self.origin,
            "company": self.company,
            "email": self.email,
            "languages": self.languages,
            "tools": self.tools,
            "special_field": self.special_field,
            "cv_path": self.cv_path,
            "img_path": self.img_path
        }
    

class ApplicantDB:

    def __init__(self, uri, db_name, upload_folder="uploads"):
        self.client = MongoClient(uri)
        self.db = self.client[db_name]
        self.applicants = self.db.applicants
        self.upload_folder = upload_folder
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)

    def get_applicant_by_id(self, applicant_id):
        """ retrieve an applicant from the database.
        example:
        applicant = db.get_applicant(applicant_id)
        print(f"Retrieved Applicant: {applicant.name}, Skills: {applicant.email}")
        """
        result = self.applicants.find_one({"_id": ObjectId(applicant_id)})
        if result:
            return Applicant(**result)
        else:
            return None
        
    def get_applicant_by_name(self, name):
        # retrieve an applicant from the database
        result = self.applicants.find_one({"name": name})
        if result:
            return Applicant(**result)
        else:
            return None
        
    def search_applicants(self, query):
        """ search for applicants in the database
        example
        applicants = db.search_applicants({"company": "BMW"})
        for applicant in applicants:
            print(f"Found Applicant: {applicant.name}, Email: {applicant.email}")
        """
        results = self.applicants.find(query)
        return [Applicant(**result) for result in results]
    
    def add_applicant(self, applicant, cv_file=None, image_file=None):
        """ insert an applicant into the database, handling file uploads.
        """
        if cv_file:
            cv_filename = secure_filename(cv_file.name)
            cv_path = os.path.join(self.upload_folder, cv_filename)
            cv_file.save(cv_path)
            applicant.cv_path = cv_path

        if image_file:
            image_filename = secure_filename(image_file.name)
            image_path = os.path.join(self.upload_folder, image_filename)
            image_file.save(image_path)
            applicant.image_path = image_path

        applicant_dict = applicant.to_dict()
        result = self.applicants.insert_one(applicant_dict)
        return str(result.inserted_id)

    

if __name__ == "__main__":
    john = {
        "name": "John Doe",
        "birthday": "12-08-2000",
        "origin": "Pakistan",
        "company": "BMW",
        "email": "john.doe@gmail.com",
        "languages": ["pakistani", "english"],
        "tools": ["GitLab", "Docker"],
        "special_field": "IT"
    }

    db = ApplicantDB(uri="mongodb+srv://admin:TTFG7zjLeAoF8g1k@cluster0.lbxzur6.mongodb.net/",
                     db_name="workway_db")
    a = Applicant.from_dict(john)
    applicant_id = db.add_applicant(a)
    print(f"Inserted Applicant with ID: {applicant_id}")

    applicant = db.get_applicant(applicant_id)
    print(f"Retrieved Applicant: {applicant.name}, Skills: {applicant.skills}")

    applicants = db.search_applicants({"company": "BMW"})
    for applicant in applicants:
        print(f"Found Applicant: {applicant.name}, Email: {applicant.email}")
