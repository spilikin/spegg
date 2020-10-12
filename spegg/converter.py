import xml.etree.ElementTree as ET
import requests
from glob import glob
import logging
from openpyxl import load_workbook
from typing import List

from .db import db
from . import dbmodel

BASE_URL="https://fachportal.gematik.de/fachportal-import/files/"

FORMAT = '[convert] %(levelname)s: %(message)s'
logging.basicConfig(format=FORMAT, level=logging.WARNING)


def convert_data():
    index_validity = ET.parse("./raw-data/metadaten-xml/index-validity-status-from-excel-file.xml")

    for index in glob("./raw-data/metadaten-xml/index-characteristics-*.xml"):
        xml = ET.parse(index)
        index = index.rsplit('/', 1)[-1]

        for file_el in xml.getroot().iter('file'):
            id = file_el.find('id').text

            if id.startswith('gemProdT_Kon_PTV'):
                id = 'gemProdT_Kon'

            version = file_el.find('typeVersion').text
            descver = file_el.find('docVersion').text

            filenames = file_el.find('fileNames').findall('fileName')

            url = requests.compat.urljoin(BASE_URL, f"../steckbriefe/{filenames[0].text}")
            r = requests.head(url)
            if r.status_code != 200:
                error = f"URL not found {url}, referenced in {id}, v{version}, {index}"
                logging.error (error)

            validity_el = index_validity.findall(f".//file[id='{id}']")


            if len(validity_el) == 0:
                logging.warning(f"Unknown entity {id}, v{version} from {index}")
            else:
                pass

            xlsx_filename = filenames[1].text

            xlx_files = glob(f"./raw-data/**/{xlsx_filename}", recursive=True)

            if len(xlx_files) == 0:
                logging.error(f"XLSX File not found for {xlsx_filename} in {index}")

            if id.startswith('gemProdT'):
                type = dbmodel.SubjectType.Product
            elif id.startswith('gemAnbT'):
                type = dbmodel.SubjectType.Provider
            elif id.startswith('gemAnw'):
                type = dbmodel.SubjectType.ThirdParty
            elif id.startswith('gemVZ'):
                type = dbmodel.SubjectType.Requirements
            else:
                logging.error(f"Unknown type: {id}")
                continue

            subj_vers = dbmodel.SubjectVersion(subject_id=id, type=type, version=version)
            db.SubjectVersion.update({'subject_id':subj_vers.subject_id, 'version':subj_vers.version}, subj_vers.dict(), upsert=True)

            logging.info(f"Subject {id}, v{version}")

            for doc_el in file_el.findall('docs/doc'):
                rid = doc_el.find('id').text
                rver = doc_el.find('docVersion').text

                resource = dbmodel.Resource(id=rid, description=doc_el.find('description').text)
                db.Resource.update({'id':rid}, resource.dict(), upsert=True)

                rv_dict = db.ResourceVersion.find_one({'resource_id': resource.id, 'version': rver})

                if rv_dict != None:
                    logging.debug(f"Already exists: {resource.id}, v{rver}")
                    resource_version = dbmodel.ResourceVersion(**rv_dict)
                else:
                    url = requests.compat.urljoin(BASE_URL, f"{rid}_V{rver}.pdf")
                    r = requests.head(url)
                    if r.status_code != 200:
                        error = f"URL not found for document {rid}_V{rver}.pdf, referenced in {subj_vers.subject_id}, v{subj_vers.version}, {index}"
                        logging.error (error)
                        url = error

                    resource_version = dbmodel.ResourceVersion(resource_id= resource.id, version=rver, url=url)
                    db.ResourceVersion.update({'resource_id':resource.id, 'version':rver}, resource_version.dict(), upsert=True)
                    rv_dict = db.ResourceVersion.find_one({'resource_id': resource.id, 'version': rver})
                    logging.info(f"ResourceVersion {resource_version.resource_id}, v{resource_version.version}")
              
                subj_vers.resources.append(rv_dict['_id']) 

            db.SubjectVersion.update({'subject_id':subj_vers.subject_id, 'version':subj_vers.version}, subj_vers.dict(), upsert=True)
    
        # uncomment for fast partial import
        #break
                
#pprint (load_requirements(doc_filename, 'Anforderungen'))
#pprint (load_requirements(desc_filename, 'Blattanforderungen'))
def load_requirements(filename: str, sheetname: str) -> List[Requirement]:
    result = []
    wb = load_workbook(filename)
    ws = wb[sheetname]
    for row in ws.iter_rows(min_row=2):
        print(row[0].value)
        result.append(dbmodel.Requirement(
            id=row[0].value,
            title=row[1].value,
            text=row[2].value,
            html=row[3].value,
            level=row[4].value
        ))
    return result
