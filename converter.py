from spegg import model
import xml.etree.ElementTree as ET
import requests
import yaml
from glob import glob
import logging

BASE_URL="https://fachportal.gematik.de/fachportal-import/files/"

documents = yaml.safe_load(open('data/documents.yaml'))
if documents == None:
    documents = []
documents = {  doc['id'] : model.Document(**doc) for doc in documents }

document_versions = []

for index in glob("./raw-data/metadaten-xml/index-characteristics-*.xml"):
    xml = ET.parse(index)

    for file in xml.getroot().iter('file'):
        c13s_id = file.find('id').text
        c13s_version = file.find('typeVersion').text
        if c13s_version == "Keine Angabe":
            c13s_version = None
        c13s_doc_version = file.find('docVersion').text
        if c13s_doc_version == "Keine Angabe":
            c13s_version = None

        if c13s_version == None and c13s_doc_version != None:
            c13s_version = c13s_doc_version
            c13s_doc_version = None

        for doc in file.findall('docs/doc'):
            doc_id = doc.find('id').text
            doc_version = doc.find('docVersion').text
            doc = model.Resource(id=doc_id, description=doc.find('description').text)
            if doc.id in documents and documents[doc.id].description != doc.description:
                logging.warning (documents[doc.id].description + " != "+doc.description)
            documents[doc.id] = doc

            url = requests.compat.urljoin(BASE_URL, f"{doc_id}_V{doc_version}.pdf")
            r = requests.head(url)
            if r.status_code != 200:
                logging.error (f"File not found: {doc_id}_V{doc_version}.pdf, referenced in {c13s_id}#{c13s_version}")
                url = "not_found"

            doc_version = model.ResourceVersion(documentId=doc_id, version=doc_version, url=url)
            document_versions.append(doc_version)

documents = sorted(documents.values(), key=lambda doc: doc.id.lower())
documents = [ d.dict() for d in documents ]

document_versions = sorted(document_versions, key=lambda doc_version: doc_version.docId)
document_versions = [ d.dict() for d in document_versions ]

yaml.dump(documents, open('./data/documents.yaml', 'w'), allow_unicode=True, sort_keys=False, width=256)
yaml.dump(document_versions, open('./data/document_versions.yaml', 'w'), allow_unicode=True, sort_keys=False, width=256)