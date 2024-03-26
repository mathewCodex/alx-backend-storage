#!/usr/bin/env python3
'''Task 9 mod '''


def insert_school(mongo_collection, **kwargs):
    '''Insert a new docs in a coll
    '''
    res = mongo_collection.insert_one(kwargs)
    return res.inserted_id
