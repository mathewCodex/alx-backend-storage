#!/usr/bin/env python3
'''Task 8 mod
'''


def list_all(mongo_collection):
    '''List all docs in a collection
    '''
    return [doc for doc in mongo_collection.find()]
