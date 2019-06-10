# This script imports content extracted from ratsinfo documents
# into an Elasticsearch database.

from datetime import datetime
import os
import subprocess

from dateutil.parser import parse
from elasticsearch import Elasticsearch

es_index_name = 'ratsinfo'

es_host = 'localhost'
es_port = '9200'

documents_path = 'documents/{document_id}/{filename}'
ocred_documents_path = 'documents/{document_id}/ocr/{filename}'
source_path = 'fulltext'

pdfinfo_path = '/usr/local/bin/pdfinfo'

def get_metadata(document_id, filename):
    """
    Returns a dict with document details like
    title, subject, creation date, last modification date, author, num_pages, size, 
    """
    path = documents_path.format(document_id=document_id, filename=filename)
    cmd =  "{binary} -enc UTF-8 '{path}'".format(binary=pdfinfo_path, path=path)
    output = subprocess.check_output(cmd, encoding='UTF-8', shell=True)

    out_dict = {}
    for line in output.splitlines():
        if ":" in line:
            label, value = line.strip().split(":", 1)
            label = label.lower().replace(" ", "_")

            value = value.strip()

            if label == 'file_size':
                value = int(value.split()[0])  # only take number from string "123 bytes"
            if label == 'pages':
                value = int(value)
            
            if value == 'yes':
                value = True
            elif value == 'no':
                value = False
            
            if label in ('creationdate', 'moddate'):
                value = parse(value)

            out_dict[label] = value

    return out_dict


def is_ocred(document_id, filename):
    """
    Checks whether a document has been OCRed and returns True if so.
    """
    path = ocred_documents_path.format(document_id=document_id, filename=filename)
    return os.path.exists(path)


def get_documents():
    """
    Yields info on every single document found in the repo folder
    """

    for root, _, files in os.walk(source_path, topdown=True):

        document_id = os.path.basename(root)
        try:
            int(document_id)
        except:
            continue

        for filename in files:
            textfile_path = os.path.join(root, filename)
            print(textfile_path)
            
            # remove .txt from end
            pdf_filename = filename[:-4]

            text = ""
            with open(textfile_path, encoding='utf8') as textfile:
                text = textfile.read()

            meta = get_metadata(document_id, pdf_filename)

            ret = {
                "proposal_id": document_id,
                "proposal_page_url": 'http://ratsinfo.roesrath.de/ratsinfo/roesrath/Proposal.html?select=%s' % document_id,
                "filename": pdf_filename,
                "id": "%s/%s" % (document_id, pdf_filename),
                "text": text,
                "ocr_processed": is_ocred(document_id, pdf_filename),
            }

            if 'creationdate' in meta:
                ret['created'] = meta['creationdate']
            if 'moddate' in meta:
                ret['modified'] = meta['moddate']
            if 'author' in meta:
                ret['author'] = meta['author']
            if 'creator' in meta:
                ret['pdf_creator'] = meta['creator']
            if 'producer' in meta:
                ret['pdf_producer'] = meta['producer']

            if 'file_size' in meta:
                ret['size'] = meta['file_size']
            if 'pages' in meta:
                ret['num_pages'] = meta['pages']

            if 'encrypted' in meta:
                ret['pdf_encrypted'] = meta['encrypted']
            if 'tagged' in meta:
                ret['pdf_tagged'] = meta['tagged']
            if 'optimized' in meta:
                ret['pdf_optimized'] = meta['optimized']

            if 'pdf_version' in meta:
                ret['pdf_version'] = meta['pdf_version']

            if 'title' in meta or 'subject' in meta:
                if 'title' in meta and 'subject' in meta:
                    ret['title'] = "%s (%s)" % (meta['subject'], meta['title'])
                elif 'title' in meta:
                    ret['title'] = meta['title']
                elif 'subject' in meta:
                    ret['title'] = meta['subject']

            yield ret


def main():
    print("Connecting to elasticsearch:9200...")
    es = Elasticsearch([{'host': es_host, 'port': es_port}])
    es.cluster.health(wait_for_status='yellow', request_timeout=20)

    mappings = {
        "properties": {
            "proposal_page_url": {"type": "keyword"},
            "proposal_id": {"type": "keyword"},
            "filename": {"type": "keyword"},
            "size": {"type": "long"},
            "num_pages": {"type": "long"},
            "created": {"type": "date"},
            "modified": {"type": "date"},
            "author": {"type": "text"},
            "pdf_creator": {"type": "keyword"},
            "pdf_producer": {"type": "keyword"},
            "pdf_tagged": {"type": "boolean"},
            "pdf_encrypted": {"type": "boolean"},
            "pdf_optimized": {"type": "boolean"},
            "pdf_version": {"type": "keyword"},
            "ocr_processed": {"type": "boolean"},
            "author": {"type": "text"},
            "title": {
                "type": "text",
                "analyzer": "german",
                "store": False,
            },
            "text": {
                "type": "text",
                "analyzer": "german",
                "store": False,
            },
        }
    }

    # Sometimes useful in development
    es.indices.delete(index=es_index_name)

    if not es.indices.exists(index=es_index_name):
        es.indices.create(index=es_index_name, ignore=400)
        es.indices.close(index=es_index_name)
        es.indices.put_mapping(index=es_index_name, doc_type='result', body=mappings)
        es.indices.open(index=es_index_name)

    # Index database content
    count = 0
    for doc in get_documents():
        es.index(index=es_index_name, doc_type='document', id=doc['id'], body=doc)

        count += 1

    print('Done indexing %s documents' % count)


if __name__ == "__main__":
    main()
