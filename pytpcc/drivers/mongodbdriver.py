# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------
# Copyright (C) 2011
# Andy Pavlo
# http://www.cs.brown.edu/~pavlo/
#
# Original Java Version:
# Copyright (C) 2008
# Evan Jones
# Massachusetts Institute of Technology
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT
# IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR ANY CLAIM, DAMAGES OR
# OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
# ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
# -----------------------------------------------------------------------



import sys
import json
import logging
import urllib.request, urllib.parse, urllib.error
from pprint import pformat
from time import sleep
import pymongo
from pymongo.client_session import TransactionOptions

import constants
from .abstractdriver import AbstractDriver


TABLE_COLUMNS = {
    constants.TABLENAME_ITEM: [
        ["I_ID", "int", "Cacheable", 4], # INTEGER
        ["I_IM_ID", "int", "Cacheable", 4], # INTEGER
        ["I_NAME", "string", "Cacheable", 4], # VARCHAR
        ["I_PRICE", ["double", "int"], "Cacheable", 5], # FLOAT
        ["I_DATA", "string", "Cacheable", 50], # VARCHAR
        ["I_W_ID", "int", "Cacheable", 4] # INTEGER
    ],
    constants.TABLENAME_WAREHOUSE: [
        ["W_ID", "int", "Cacheable", 4], # SMALLINT
        ["W_NAME", "string", "Cacheable", 20], # VARCHAR
        ["W_STREET_1", "string", "Cacheable", 20], # VARCHAR
        ["W_STREET_2", "string", "Cacheable", 20], # VARCHAR
        ["W_CITY", "string", "Cacheable", 20], # VARCHAR
        ["W_STATE", "string", "Cacheable", 20], # VARCHAR
        ["W_ZIP", "string", "Cacheable", 20], # VARCHAR
        ["W_TAX", ["double", "int"], "Cacheable", 8], # FLOAT
        ["W_YTD", ["double", "int"], "Cacheable", 8]# FLOAT
    ],
    constants.TABLENAME_DISTRICT: [
        ["D_ID", "int", "Cacheable", 4], # TINYINT
        ["D_W_ID", "int", "Cacheable", 4], # SMALLINT
        ["D_NAME", "string", "Cacheable", 20], # VARCHAR
        ["D_STREET_1", "string", "Cacheable", 20], # VARCHAR
        ["D_STREET_2", "string", "Cacheable", 20], # VARCHAR
        ["D_CITY", "string", "Cacheable", 20], # VARCHAR
        ["D_STATE", "string", "Cacheable", 20], # VARCHAR
        ["D_ZIP", "string", "Cacheable", 20], # VARCHAR
        ["D_TAX", ["double", "int"], "Cacheable", 8], # FLOAT
        ["D_YTD", ["double", "int"], "Cacheable", 8], # FLOAT
        ["D_NEXT_O_ID", "int", "Cacheable", 4] # INT
    ],
    constants.TABLENAME_CUSTOMER:   [
        ["C_ID", "int", "Cacheable", 4], # INTEGER
        ["C_D_ID", "int", "Cacheable", 4], # TINYINT
        ["C_W_ID", "int", "Cacheable", 4], # SMALLINT
        ["C_FIRST", "string", "Cacheable", 20], # VARCHAR
        ["C_MIDDLE", "string", "Cacheable", 20], # VARCHAR
        ["C_LAST", "string", "Cacheable", 20], # VARCHAR
        ["C_STREET_1", "string", "Cacheable", 20], # VARCHAR
        ["C_STREET_2", "string", "Cacheable", 20], # VARCHAR
        ["C_CITY", "string", "Cacheable", 20], # VARCHAR
        ["C_STATE", "string", "Cacheable", 20], # VARCHAR
        ["C_ZIP", "string", "Cacheable", 20], # VARCHAR
        ["C_PHONE", "string", "Cacheable", 20], # VARCHAR
        ["C_SINCE", "string", "Cacheable", 20], # TIMESTAMP
        ["C_CREDIT", "string", "Cacheable", 20], # VARCHAR
        ["C_CREDIT_LIM", ["double", "int"], "Cacheable", 20], # FLOAT
        ["C_DISCOUNT", ["double", "int"], "Cacheable", 8], # FLOAT
        ["C_BALANCE", ["double", "int"], "Cacheable", 20], # FLOAT
        ["C_YTD_PAYMENT", ["double", "int"], "Cacheable", 20], # FLOAT
        ["C_PAYMENT_CNT", "int", "Cacheable", 20], # INTEGER
        ["C_DELIVERY_CNT", "int", "Cacheable", 20], # INTEGER
        ["C_DATA", "string", "Cacheable", 500], # VARCHAR
    ],
    constants.TABLENAME_STOCK:      [
        ["S_I_ID", "int", "Cacheable", 4], # INTEGER
        ["S_W_ID", "int", "Cacheable", 4], # SMALLINT
        ["S_QUANTITY", "int", "Cacheable", 4], # INTEGER
        ["S_DIST_01", "string", "Cacheable", 30], # VARCHAR
        ["S_DIST_02", "string", "Cacheable", 30], # VARCHAR
        ["S_DIST_03", "string", "Cacheable", 30], # VARCHAR
        ["S_DIST_04", "string", "Cacheable", 30], # VARCHAR
        ["S_DIST_05", "string", "Cacheable", 30], # VARCHAR
        ["S_DIST_06", "string", "Cacheable", 30], # VARCHAR
        ["S_DIST_07", "string", "Cacheable", 30], # VARCHAR
        ["S_DIST_08", "string", "Cacheable", 30], # VARCHAR
        ["S_DIST_09", "string", "Cacheable", 30], # VARCHAR
        ["S_DIST_10", "string", "Cacheable", 30], # VARCHAR
        ["S_YTD", "int", "Cacheable", 4], # INTEGER
        ["S_ORDER_CNT", "int", "Cacheable", 4], # INTEGER
        ["S_REMOTE_CNT", "int", "Cacheable", 4], # INTEGER
        ["S_DATA", "string", "Cacheable", 500] # VARCHAR
    ],
    constants.TABLENAME_ORDERS:     [
        ["O_ID", "int", "Cacheable", 4], # INTEGER
        ["O_C_ID", "int", "Cacheable", 4], # INTEGER
        ["O_D_ID", "int", "Cacheable", 4], # TINYINT
        ["O_W_ID", "int", "Cacheable", 4], # SMALLINT
        ["O_ENTRY_D", ["date", "string"], "Cacheable", 20], # TIMESTAMP
        ["O_CARRIER_ID", "int", "Cacheable", 20], # INTEGER
        ["O_OL_CNT", "int", "Cacheable", 20], # INTEGER
        ["O_ALL_LOCAL", "int", "Cacheable", 20] # INTEGER
    ],
    constants.TABLENAME_NEW_ORDER:  [
        ["NO_O_ID", "int", "Cacheable", 4], # INTEGER
        ["NO_D_ID", "int", "Cacheable", 4], # TINYINT
        ["NO_W_ID", "int", "Cacheable", 4] # SMALLINT
    ],
    constants.TABLENAME_ORDER_LINE: [
        ["OL_O_ID", "int", "Cacheable", 4], # INTEGER
        ["OL_D_ID", "int", "Cacheable", 4], # TINYINT
        ["OL_W_ID", "int", "Cacheable", 4], # SMALLINT
        ["OL_NUMBER", "int", "Cacheable", 4], # INTEGER
        ["OL_I_ID", "int", "Cacheable", 4], # INTEGER
        ["OL_SUPPLY_W_ID", "int", "Cacheable", 4], # SMALLINT
        ["OL_DELIVERY_D", ["date", "string"], "Cacheable", 20], # TIMESTAMP
        ["OL_QUANTITY", "int", "Cacheable", 4], # INTEGER
        ["OL_AMOUNT", ["double", "int"], "Cacheable", 8], # FLOAT
        ["OL_DIST_INFO", "string", "Cacheable", 24] # VARCHAR
    ],
    constants.TABLENAME_HISTORY:    [
        ["H_C_ID", "int", "Cacheable", 4], # INTEGER
        ["H_C_D_ID", "int", "Cacheable", 4], # TINYINT
        ["H_C_W_ID", "int", "Cacheable", 4], # SMALLINT
        ["H_D_ID", "int", "Cacheable", 4], # TINYINT
        ["H_W_ID", "int", "Cacheable", 4], # SMALLINT
        ["H_DATE", ["timestamp", "string"], "Cacheable", 8], # TIMESTAMP
        ["H_AMOUNT", "int", "Cacheable", 4], # FLOAT
        ["H_DATA", "string", "Cacheable", 20] # VARCHAR
    ],
}

TABLE_INDEXES = {
    constants.TABLENAME_ITEM:       [
        [("I_W_ID", pymongo.ASCENDING), ("I_ID", pymongo.ASCENDING)]
    ],
    constants.TABLENAME_WAREHOUSE:  [
        [("W_ID", pymongo.ASCENDING), ("W_TAX", pymongo.ASCENDING)]
    ],
    constants.TABLENAME_DISTRICT:   [
        [("D_W_ID", pymongo.ASCENDING), ("D_ID", pymongo.ASCENDING), ("D_NEXT_O_ID", pymongo.ASCENDING), ("D_TAX", pymongo.ASCENDING)]
    ],
    constants.TABLENAME_CUSTOMER:   [
        [("C_W_ID", pymongo.ASCENDING), ("C_D_ID", pymongo.ASCENDING), ("C_ID", pymongo.ASCENDING)],
        [("C_W_ID", pymongo.ASCENDING), ("C_D_ID", pymongo.ASCENDING), ("C_LAST", pymongo.ASCENDING)]
    ],
    constants.TABLENAME_STOCK:      [
        [("S_W_ID", pymongo.ASCENDING), ("S_I_ID", pymongo.ASCENDING), ("S_QUANTITY", pymongo.ASCENDING)],
        "S_I_ID"
    ],
    constants.TABLENAME_ORDERS:     [
        [("O_W_ID", pymongo.ASCENDING), ("O_D_ID", pymongo.ASCENDING), ("O_ID", pymongo.ASCENDING), ("O_C_ID", pymongo.ASCENDING)],
        [("O_C_ID", pymongo.ASCENDING), ("O_D_ID", pymongo.ASCENDING), ("O_W_ID", pymongo.ASCENDING), ("O_ID", pymongo.DESCENDING), ("O_CARRIER_ID", pymongo.ASCENDING), ("O_ENTRY_ID", pymongo.ASCENDING)]
    ],
    constants.TABLENAME_NEW_ORDER:  [
        [("NO_W_ID", pymongo.ASCENDING), ("NO_D_ID", pymongo.ASCENDING), ("NO_O_ID", pymongo.ASCENDING)]
    ],
    constants.TABLENAME_ORDER_LINE: [
        [("OL_O_ID", pymongo.ASCENDING), ("OL_D_ID", pymongo.ASCENDING), ("OL_W_ID", pymongo.ASCENDING), ("OL_NUMBER", pymongo.ASCENDING)],
        [("OL_O_ID", pymongo.ASCENDING), ("OL_D_ID", pymongo.ASCENDING), ("OL_W_ID", pymongo.ASCENDING), ("OL_I_ID", pymongo.DESCENDING), ("OL_AMOUNT", pymongo.ASCENDING)]
    ],
}

## ==============================================
## MongodbDriver
## ==============================================
class MongodbDriver(AbstractDriver):
    DEFAULT_CONFIG = {
        "uri":              ("The mongodb connection string or URI", "mongodb://localhost:27017"),
        "name":             ("Database name", "tpcc"),
        "denormalize":      ("If true, data will be denormalized using MongoDB schema design best practices", True),
        "notransactions":   ("If true, transactions will not be used (benchmarking only)", False),
        "findandmodify":    ("If true, all things to update will be fetched via findAndModify", True),
        "secondary_reads":  ("If true, we will allow secondary reads", True),
        "retry_writes":     ("If true, we will enable retryable writes", False),
        "causal_consistency":  ("If true, we will perform causal reads ", True),
        "shards":          ("If >1 then sharded", "1")
    }
    DENORMALIZED_TABLES = [
        constants.TABLENAME_ORDERS,
        constants.TABLENAME_ORDER_LINE
    ]


    def __init__(self, ddl):
        super(MongodbDriver, self).__init__("mongodb", ddl)
        self.no_transactions = False
        self.find_and_modify = True
        self.read_preference = "primary"
        self.database = None
        self.client = None
        self.executed = False
        self.w_orders = {}
        # things that are not better can't be set in config
        self.batch_writes = True
        self.agg = False
        self.all_in_one_txn = True
        # initialize
        self.causal_consistency = False
        self.secondary_reads = False
        self.retry_writes = False
        self.read_concern = "majority"
        self.write_concern = pymongo.write_concern.WriteConcern(w=1)
        self.denormalize = False
        self.output = open('results.json','a')
        self.result_doc = {}
        self.warehouses = 0
        self.shards = 1

        ## Create member mapping to collections
        for name in constants.ALL_TABLES:
            self.__dict__[name.lower()] = None

    ## ----------------------------------------------
    ## makeDefaultConfig
    ## ----------------------------------------------
    def makeDefaultConfig(self):
        return MongodbDriver.DEFAULT_CONFIG

    ## ----------------------------------------------
    ## loadConfig
    ## ----------------------------------------------
    def loadConfig(self, config):
        default_uri = 'uri' not in config
        for key in MongodbDriver.DEFAULT_CONFIG:
            # rather than forcing every value which has a default to be specified
            # we should pluck out the keys from default that are missing in config
            # and set them there to their default values
            if not key in config:
                logging.debug("'%s' not in %s conf, set to %s",
                              key, self.name, str(MongodbDriver.DEFAULT_CONFIG[key][1]))
                config[key] = str(MongodbDriver.DEFAULT_CONFIG[key][1])

        logging.debug("Default plus our config %s", pformat(config))
        self.denormalize = config['denormalize'] == 'False'
        self.no_transactions = config['notransactions'] == 'True'
        self.shards = int(config['shards'])
        self.warehouses = config['warehouses']
        self.find_and_modify = config['findandmodify'] == 'True'
        self.causal_consistency = config['causal_consistency'] == 'True'
        self.retry_writes = config['retry_writes'] == 'True'
        self.secondary_reads = config['secondary_reads'] == 'True'
        if self.secondary_reads:
            self.read_preference = "nearest"

        if 'write_concern' in config and config['write_concern'] and config['write_concern'] != '1':
            # only expecting string 'majority' as an alternative to w:1
            self.write_concern = pymongo.write_concern.WriteConcern(w=str(config['write_concern']), wtimeout=30000)

        # handle building connection string
        userpassword = ""
        usersecret = ""
        uri = config['uri']
        # only use host/port if they didn't provide URI
        if default_uri and 'host' in config:
            host = config['host']
            if 'port' in config:
                host = host+':'+config['port']
            uri = "mongodb://" + host
        if 'user' in config:
            user = config['user']
            if not 'passwd' in config:
                logging.error("must specify password if user is specified")
                sys.exit(1)
            userpassword = urllib.parse.quote_plus(user)+':'+urllib.parse.quote_plus(config['passwd'])+"@"
            usersecret = urllib.parse.quote_plus(user)+':'+ '*'*len(config['passwd']) + "@"

        pindex = 10  # "mongodb://"
        if uri[0:14] == "mongodb+srv://":
            pindex = 14
        real_uri = uri[0:pindex]+userpassword+uri[pindex:]
        display_uri = uri[0:pindex]+usersecret+uri[pindex:]

        self.client = pymongo.MongoClient(real_uri,
                                          retryWrites=self.retry_writes,
                                          readPreference=self.read_preference,
                                          readConcernLevel=self.read_concern)

        self.result_doc['before']=self.get_server_status()

        # set default writeConcern on the database
        self.database = self.client.get_database(name=str(config['name']), write_concern=self.write_concern)
        if self.denormalize:
            logging.debug("Using denormalized data model")

        try:
            if config["reset"]:
                logging.info("Deleting database '%s'", self.database.name)
                for name in constants.ALL_TABLES:
                    self.database[name].drop()
                    logging.debug("Dropped collection %s", name)
                ## FOR
            ## IF

            ## whether should check for indexes
            load_indexes = ('execute' in config and not config['execute']) and \
                           ('load' in config and not config['load'])

            for name in constants.ALL_TABLES:
                self.createCollection(name)

                if self.denormalize and name == "ORDER_LINE":
                    continue
                self.__dict__[name.lower()] = self.database[name]
                if load_indexes and name in TABLE_INDEXES:
                    uniq = True
                    for index in TABLE_INDEXES[name]:
                        self.database[name].create_index(index, unique=uniq)
                        uniq = False
                ## IF
            ## FOR
        except pymongo.errors.OperationFailure as exc:
            logging.error("OperationFailure %d (%s) when connected to %s: ",
                          exc.code, exc.details, display_uri)
            return
        except pymongo.errors.ServerSelectionTimeoutError as exc:
            logging.error("ServerSelectionTimeoutError %d (%s) when connected to %s: ",
                          exc.code, exc.details, display_uri)
            return
        except pymongo.errors.ConnectionFailure:
            logging.error("ConnectionFailure %d (%s) when connected to %s: ",
                          exc.code, exc.details, display_uri)
            return
        except pymongo.errors.PyMongoError as err:
            logging.error("Some general error (%s) when connected to %s: ", str(err), display_uri)
            print(("Got some other error: %s" % str(err)))
            return

    def generate_json_schema(self, table_name):
        # Map your types to BSON types
        type_mapping = {
            "int": "int",
            "string": "string",
            "float": "double"  # MongoDB uses "double" for floating-point numbers
        }
        
        # Get the column definitions for the given table
        columns = TABLE_COLUMNS.get(table_name, [])
        
        # Build the JSON schema properties
        properties = {}
        for column in columns:
            maxLength = 4
            column_name, column_type, description, l = column
            # bson_type = type_mapping.get(column_type.lower(), "string")  # Default to string if unknown
            # if bson_type == "string":
            if  "string" in column_type:
                maxLength = l
            properties[column_name] = {
                "bsonType": column_type,
                "maxLength": maxLength,
                "description": description
            }
        
        # Assemble the full schema
        json_schema = {
            "$jsonSchema": {
                "bsonType": "object",
                "properties": properties
            }
        }
        
        return json_schema


    def createCollection(self, tableName):
        self.database[tableName].drop() 
        user_schema = self.generate_json_schema(tableName)
        self.database.create_collection(tableName, validator=user_schema)


    ## ----------------------------------------------
    ## loadTuples
    ## ----------------------------------------------
    def loadTuples(self, tableName, tuples):
        if not tuples:
            return

        logging.debug("Loading %d tuples for tableName %s", len(tuples), tableName)

        assert tableName in TABLE_COLUMNS, "Table %s not found in TABLE_COLUMNS" % tableName
        columns = TABLE_COLUMNS[tableName]
        num_columns = list(range(len(columns)))

        tuple_dicts = []

        ## We want to combine all of a CUSTOMER's ORDERS, and ORDER_LINE records
        ## into a single document
        if self.denormalize and tableName in MongodbDriver.DENORMALIZED_TABLES:
            ## If this is the ORDERS table, then we'll just store the record locally for now
            if tableName == constants.TABLENAME_ORDERS:
                for t in tuples:
                    key = tuple(t[:1]+t[2:4]) # O_ID, O_C_ID, O_D_ID, O_W_ID
                    # self.w_orders[key] = dict(map(lambda i: (columns[i], t[i]), num_columns))
                    self.w_orders[key] = dict([(columns[i][0], t[i]) for i in num_columns])
                ## FOR
            ## IF

            ## If this is an ORDER_LINE record, then we need to stick it inside of the
            ## right ORDERS record
            elif tableName == constants.TABLENAME_ORDER_LINE:
                try:
                    for t in tuples:
                        o_key = tuple(t[:3]) # O_ID, O_D_ID, O_W_ID
                        assert o_key in self.w_orders, "Order Key: %s\nAll Keys:\n%s" % (str(o_key), "\n".join(map(str, sorted(self.w_orders.keys()))))
                        o = self.w_orders[o_key]
                        if not tableName in o:
                            o[tableName] = []
                        o[tableName].append(dict([(columns[i][0], t[i]) for i in num_columns[4:]]))
                except Exception as e:
                    print(f"Error: {e}")
                else:
                    print("ORDER_LINE Loaded")
                ## FOR

            ## Otherwise nothing
            else: assert False, "Only Orders and order lines are denormalized! Got %s." % tableName
        ## Otherwise just shove the tuples straight to the target collection
        else:
            if tableName == constants.TABLENAME_ITEM:
                tuples3 = []
                if self.shards > 1:
                    ww = list(range(1,self.warehouses+1))
                else:
                    ww = [0]
                for t in tuples:
                    for w in ww:
                       t2 = list(t)
                       t2.append(w)
                       tuples3.append(t2)
                tuples = tuples3
            
            for t in tuples:
                if len(t) != len(columns):
                    logging.error(f"Mismatch: columns({len(columns)}): {columns}, tuple({len(t)}): {t}")
                    raise ValueError(f"Mismatch between columns and tuple data: columns({len(columns)}), tuple({len(t)})")

                tuple_dicts.append(dict([(columns[i][0], t[i]) for i in num_columns]))
            ## FOR

            self.database[tableName].insert_many(tuple_dicts)
        ## IF

        return

    def loadFinishDistrict(self, w_id, d_id):
        if self.denormalize:
            logging.debug("Pushing %d denormalized ORDERS records for WAREHOUSE %d DISTRICT %d into MongoDB", len(self.w_orders), w_id, d_id)
            self.database[constants.TABLENAME_ORDERS].insert_many(list(self.w_orders.values()))
            self.w_orders.clear()
        ## IF

    def executeStart(self):
        """Optional callback before the execution for each client starts"""
        return None

    def executeFinish(self):
        """Callback after the execution for each client finishes"""
        return None

    ## ----------------------------------------------
    ## doDelivery
    ## ----------------------------------------------
    def doDelivery(self, params):
        # two options, option one (default) is to run a db transaction for each of 10 orders

        if self.all_in_one_txn:
            (value, retries) = self.run_transaction_with_retries(self._doDelivery10Txn, "DELIVERY", params)
            return (value, retries)
        result = []
        retries = 0
        # there will be as many orders as districts per warehouse (10)
        for d_id in range(1, constants.DISTRICTS_PER_WAREHOUSE+1):
            params["d_id"] = d_id
            (r, rt) = self.run_transaction_with_retries(self._doDeliveryTxn, "DELIVERY", params)
            retries += rt
            result.append(r)
        return (result, retries)

    def _doDelivery10Txn(self, s, params):
        result = []
        # there will be as many orders as districts per warehouse (10)
        for d_id in range(1, constants.DISTRICTS_PER_WAREHOUSE+1):
            params["d_id"] = d_id
            r = self._doDeliveryTxn(s, params)
            if r:
                result.append(r)
        return result

    def _doDeliveryTxn(self, s, params):
        w_id = params["w_id"]
        o_carrier_id = params["o_carrier_id"]
        ol_delivery_d = params["ol_delivery_d"]
        d_id = params["d_id"]
        comment = "DELIVERY " + str(d_id)
        ## getNewOrder
        new_order_query = {"NO_D_ID": d_id, "NO_W_ID": w_id, "$comment": comment}
        new_order_project = {"_id":0, "NO_D_ID":1, "NO_W_ID":1, "NO_O_ID": 1}
        if self.find_and_modify:
            no = self.new_order.find_one_and_delete(new_order_query,
                                                    projection=new_order_project,
                                                    sort=[("NO_O_ID", 1)], session=s)
            if not no:
                ## No orders for this district: skip it. Note: This must be reported if > 1%
                return None
        else:
            no_cursor = self.new_order.find(new_order_query,
                                            new_order_project,
                                            session=s).sort([("NO_O_ID", 1)]).limit(1)
            no_converted_cursor = list(no_cursor)
            if not no_converted_cursor:
                ## No orders for this district: skip it. Note: This must be reported if > 1%
                return None
            ## IF
            no = no_converted_cursor[0]
        ## IF

        o_id = no["NO_O_ID"]
        assert o_id, "o_id cannot be missing for delivery"

        ## getCId
        order_query = {"O_ID": o_id, "O_D_ID": d_id, "O_W_ID": w_id, "$comment": comment}
        if self.denormalize:
            if self.find_and_modify:
                o = self.orders.find_one_and_update(order_query,
                                                    {"$set": {"O_CARRIER_ID": o_carrier_id,
                                                              "ORDER_LINE.$[].OL_DELIVERY_D": ol_delivery_d}},
                                                    session=s)
                # o = self.orders.find_one_and_update(order_query,
                #                                     {"$set": {"O_CARRIER_ID": o_carrier_id}},
                #                                     session=s)
            else:
                o = self.orders.find_one(order_query, session=s)
        else:
            o = self.orders.find_one(order_query,
                                     {"O_C_ID": 1, "O_ID": 1, "O_D_ID": 1, "O_W_ID": 1, "_id":0},
                                     session=s)
        assert o, "o cannot be none, delivery"
        c_id = o["O_C_ID"]

        if self.denormalize:
            ## sumOLAmount + updateOrderLine
            ol_total = 0
            order_lines = o["ORDER_LINE"]

            ol_total = sum([ol["OL_AMOUNT"] for ol in order_lines])

            assert ol_total > 0, "ol_total is 0"

            ## updateOrders
            if not self.find_and_modify:
                self.orders.update_one({"_id": o['_id'], "$comment": comment},
                                       {"$set": {"O_CARRIER_ID": o_carrier_id,
                                                 "ORDER_LINE.$[].OL_DELIVERY_D": ol_delivery_d}},
                                       session=s)
        else:
            ## sumOLAmount
            order_lines = self.order_line.find({"OL_O_ID": o_id,
                                                "OL_D_ID": d_id,
                                                "OL_W_ID": w_id,
                                                "$comment": comment},
                                               {"_id":0, "OL_AMOUNT": 1}, session=s)
            assert order_lines, "order_lines cannot be missing in delivery"
            ol_total = sum([ol["OL_AMOUNT"] for ol in order_lines])

            ## updateOrders
            o["$comment"] = comment
            self.orders.update_one(o, {"$set": {"O_CARRIER_ID": o_carrier_id}}, session=s)

            ## updateOrderLines
            self.order_line.update_many({"OL_O_ID": o_id, "OL_D_ID": d_id, "OL_W_ID": w_id},
                                        {"$set": {"OL_DELIVERY_D": ol_delivery_d}}, session=s)

        ## IF

        ## updateCustomer
        self.customer.update_one({"C_ID": c_id, "C_D_ID": d_id, "C_W_ID": w_id, "$comment": comment},
                                 {"$inc": {"C_BALANCE": ol_total}}, session=s)

        ## deleteNewOrder
        if not self.find_and_modify:
            self.new_order.delete_one(no, session=s)

        # These must be logged in the "result file" according to TPC-C 2.7.2.2 (page 39)
        # We remove the queued time, completed time, w_id, and o_carrier_id: the client can figure
        # them out
        # If there are no order lines, SUM returns null. There should always be order lines.
        assert ol_total, "ol_total is NULL: there are no order lines. This should not happen"
        assert ol_total > 0.0, "ol_total is 0"

        return (d_id, o_id)

    ## ----------------------------------------------
    ## doNewOrder
    ## ----------------------------------------------
    def doNewOrder(self, params):
        (value, retries) = self.run_transaction_with_retries(self._doNewOrderTxn, "NEW_ORDER", params)
        return (value, retries)

    def _doNewOrderTxn(self, s, params):
        w_id = params["w_id"]
        d_id = params["d_id"]
        c_id = params["c_id"]
        o_entry_d = params["o_entry_d"]
        i_ids = params["i_ids"]
        i_w_ids = params["i_w_ids"]
        i_qtys = params["i_qtys"]
        s_dist_col = "S_DIST_%02d" % d_id
        comment = "NEW_ORDER"

        assert i_ids, "No matching i_ids found for new order"
        assert len(i_ids) == len(i_w_ids), "different number of i_ids and i_w_ids"
        assert len(i_ids) == len(i_qtys), "different number of i_ids and i_qtys"

        ## ----------------
        ## Collect Information from WAREHOUSE, DISTRICT, and CUSTOMER
        ## ----------------

        # getDistrict
        district_project = {"_id":0, "D_ID":1, "D_W_ID":1, "D_TAX": 1, "D_NEXT_O_ID": 1}
        if self.find_and_modify:
            d = self.district.find_one_and_update(
                {"D_ID": d_id, "D_W_ID": w_id},  # Query filter
                {"$inc": {"D_NEXT_O_ID": 1}},    # Update operation
                projection=district_project,     # Fields to project
                session=s,                       # Active session
                comment=comment                  # Optional comment for the operation
            )
            if not d:
                d1 = self.district.find_one({"D_ID": d_id, "D_W_ID": w_id, "$comment": "new order did not find district"})
                print((d1, w_id, d_id, c_id, i_ids, i_w_ids, s_dist_col))
            assert d, "Couldn't find district in new order w_id %d d_id %d" % (w_id, d_id)
        else:
            d = self.district.find_one({"D_ID": d_id, "D_W_ID": w_id, "$comment": comment},
                                       district_project, session=s)
            assert d, "Couldn't find district in new order w_id %d d_id %d" % (w_id, d_id)
            # incrementNextOrderId
            d["$comment"] = comment
            self.district.update_one(d, {"$inc": {"D_NEXT_O_ID": 1}}, session=s)
        ## IF
        d_tax = d["D_TAX"]
        d_next_o_id = d["D_NEXT_O_ID"]

        # fetch matching items and see if they are all valid
        if self.shards > 1: i_w_id = w_id
        else: i_w_id = 0
        items = list(self.item.find({"I_ID": {"$in": i_ids}, "I_W_ID": i_w_id, "$comment": comment},
                                    {"_id":0, "I_ID": 1, "I_PRICE": 1, "I_NAME": 1, "I_DATA": 1},
                                    session=s))
        ## TPCC defines 1% of neworder gives a wrong itemid, causing rollback.
        ## Note that this will happen with 1% of transactions on purpose.
        if len(items) != len(i_ids):
            if not self.no_transactions:
                s.abort_transaction()
            logging.debug("1% Abort transaction: " +  constants.INVALID_ITEM_MESSAGE)
            #print constants.INVALID_ITEM_MESSAGE + ", Aborting transaction (ok for 1%)"
            return None
        ## IF
        xxi_ids = tuple([o['I_ID'] for o in items])
        items = sorted(items, key=lambda x: xxi_ids.index(x['I_ID']))

        # getWarehouseTaxRate
        w = self.warehouse.find_one({"W_ID": w_id, "$comment": comment}, {"_id":0, "W_TAX": 1}, session=s)
        assert w, "Couldn't find warehouse in new order w_id %d" % (w_id)
        w_tax = w["W_TAX"]

        # getCustomer
        c = self.customer.find_one({"C_ID": c_id, "C_D_ID": d_id, "C_W_ID": w_id, "$comment": comment},
                                   {"C_DISCOUNT": 1, "C_LAST": 1, "C_CREDIT": 1}, session=s)
        assert c, "Couldn't find customer in new order"
        c_discount = c["C_DISCOUNT"]

        ## ----------------
        ## Insert Order Information
        ## ----------------
        ol_cnt = len(i_ids)
        o_carrier_id = constants.NULL_CARRIER_ID

        # createNewOrder
        try:
            self.new_order.insert_one({"NO_O_ID": d_next_o_id, "NO_D_ID": d_id, "NO_W_ID": w_id}, session=s)
        except Exception as e:
            print(f"Error in insertion: {e}")
            
        all_local = 1 if ([w_id] * len(i_w_ids)) == i_w_ids else 0
        o = {"O_ID": d_next_o_id, "O_ENTRY_D": o_entry_d,
             "O_CARRIER_ID": o_carrier_id, "O_OL_CNT": ol_cnt, "O_ALL_LOCAL": all_local}

        if self.denormalize:
            o[constants.TABLENAME_ORDER_LINE] = []

        o["O_D_ID"] = d_id
        o["O_W_ID"] = w_id
        o["O_C_ID"] = c_id

        ## ----------------
        ## OPTIMIZATION:
        ## If all of the items are at the same warehouse, then we'll issue a single
        ## request to get their information, otherwise we'll still issue a single request
        ## ----------------
        item_w_list = list(zip(i_ids, i_w_ids))
        stock_project = {"_id":0, "S_I_ID": 1, "S_W_ID": 1,
                         "S_QUANTITY": 1, "S_DATA": 1, "S_YTD": 1,
                         "S_ORDER_CNT": 1, "S_REMOTE_CNT": 1, s_dist_col: 1}
        if all_local:
            all_stocks = list(self.stock.find({"S_I_ID": {"$in": i_ids}, "S_W_ID": w_id, "$comment": comment},
                                              stock_project,
                                              session=s))
        else:
            field_list = ["S_I_ID", "S_W_ID"]
            search_list = [dict(list(zip(field_list, ze))) for ze in item_w_list]
            all_stocks = list(self.stock.find({"$or": search_list, "$comment": comment},
                                              stock_project,
                                              session=s))
        ## IF
        assert len(all_stocks) == ol_cnt, "all_stocks len %d != ol_cnt %d" % (len(all_stocks), ol_cnt)
        xxxi_ids = tuple([(o['S_I_ID'], o['S_W_ID']) for o in all_stocks])
        all_stocks = sorted(all_stocks, key=lambda x: xxxi_ids.index((x['S_I_ID'], x["S_W_ID"])))

        ## ----------------
        ## Insert Order Line, Stock Item Information
        ## ----------------
        item_data = []
        total = 0
        # we already fetched all items so we should never need to go to self.item again
        # iterate over every line item
        # if self.batch_writes is set then write once per collection
        if self.batch_writes:
            stock_writes = []
            order_line_writes = []
        ## IF
        for i in range(ol_cnt):
            ol_number = i + 1
            ol_supply_w_id = i_w_ids[i]
            ol_i_id = i_ids[i]
            ol_quantity = i_qtys[i]

            item_info = items[i]
            i_name = item_info["I_NAME"]
            i_data = item_info["I_DATA"]
            i_price = item_info["I_PRICE"]

            si = all_stocks[i]

            assert si, "stock item not found"

            s_quantity = si["S_QUANTITY"]
            s_ytd = si["S_YTD"]
            s_order_cnt = si["S_ORDER_CNT"]
            s_remote_cnt = si["S_REMOTE_CNT"]
            s_data = si["S_DATA"]
            s_dist_xx = si[s_dist_col] # Fetches data from the s_dist_[d_id] column

            ## Update stock
            s_ytd += ol_quantity
            if s_quantity >= ol_quantity + 10:
                s_quantity = s_quantity - ol_quantity
            else:
                s_quantity = s_quantity + 91 - ol_quantity
            ## IF

            s_order_cnt += 1

            if ol_supply_w_id != w_id:
                s_remote_cnt += 1

            # updateStock
            stock_write_update = {"$set": {"S_QUANTITY": s_quantity,
                                           "S_YTD": s_ytd,
                                           "S_ORDER_CNT": s_order_cnt,
                                           "S_REMOTE_CNT": s_remote_cnt}}
            if self.batch_writes:
                si["$comment"] = comment
                stock_writes.append(pymongo.UpdateOne(si, stock_write_update))
            else:
                si["$comment"] = comment
                self.stock.update_one(si, stock_write_update, session=s)

            if i_data.find(constants.ORIGINAL_STRING) != -1 and s_data.find(constants.ORIGINAL_STRING) != -1:
                brand_generic = 'B'
            else:
                brand_generic = 'G'
            ## IF

            ## Transaction profile states to use "ol_quantity * i_price"
            ol_amount = ol_quantity * i_price
            total += ol_amount

            ol = {"OL_O_ID": d_next_o_id, "OL_NUMBER": ol_number, "OL_I_ID": ol_i_id,
                  "OL_SUPPLY_W_ID": ol_supply_w_id, "OL_DELIVERY_D": o_entry_d,
                  "OL_QUANTITY": ol_quantity, "OL_AMOUNT": ol_amount, "OL_DIST_INFO": s_dist_xx}

            if self.denormalize:
                # createOrderLine
                o[constants.TABLENAME_ORDER_LINE].append(ol)
            else:
                ol["OL_D_ID"] = d_id
                ol["OL_W_ID"] = w_id

                # createOrderLine
                if self.batch_writes:
                    order_line_writes.append(ol)
                else:
                    self.order_line.insert_one(ol, session=s)
                ## IF
            ## IF

            ## Add the info to be returned
            item_data.append((i_name, s_quantity, brand_generic, i_price, ol_amount))
        ## FOR

        ## Adjust the total for the discount
        total *= (1 - c_discount) * (1 + w_tax + d_tax)

        if self.batch_writes:
            if not self.denormalize:
                self.order_line.insert_many(order_line_writes, session=s)
            self.stock.bulk_write(stock_writes, session=s)
        ## IF

        # createOrder
        self.orders.insert_one(o, session=s)

        ## Pack up values the client is missing (see TPC-C 2.4.3.5)
        misc = [(w_tax, d_tax, d_next_o_id, total)]

        return [c, misc, item_data]

    ## ----------------------------------------------
    ## doOrderStatus
    ## ----------------------------------------------
    def doOrderStatus(self, params):
        (value, retries) = self.run_transaction_with_retries(self._doOrderStatusTxn, "ORDER_STATUS", params)
        return (self._doOrderStatusTxn(None, params), 0)

    def _doOrderStatusTxn(self, s, params):
        w_id = params["w_id"]
        d_id = params["d_id"]
        c_id = params["c_id"]
        c_last = params["c_last"]
        comment = "ORDER_STATUS"

        assert w_id, pformat(params)
        assert d_id, pformat(params)

        search_fields = {"C_W_ID": w_id, "C_D_ID": d_id, "$comment": comment}
        return_fields = {"_id":0, "C_ID": 1, "C_FIRST": 1, "C_MIDDLE": 1, "C_LAST": 1, "C_BALANCE": 1}

        if c_id != None:
            # getCustomerByCustomerId
            search_fields["C_ID"] = c_id
            c = self.customer.find_one(search_fields, return_fields, session=s)
            assert c, "Couldn't find customer in order status"
        else:
            # getCustomersByLastName
            # Get the midpoint customer's id
            search_fields['C_LAST'] = c_last

            all_customers = list(self.customer.find(search_fields, return_fields, session=s))
            namecnt = len(all_customers)
            assert namecnt > 0, "No matching customer for last name %s!" % c_last
            index = (namecnt-1)//2
            c = all_customers[index]
            c_id = c["C_ID"]
        ## IF

        assert c_id != None, "Couldn't find c_id in order status"

        order_lines = []
        order = None

        # getLastOrder
        if self.denormalize:
            order = self.orders.find({"O_W_ID": w_id, "O_D_ID": d_id, "O_C_ID": c_id, "$comment": comment},
                                     {"O_ID": 1, "O_CARRIER_ID": 1, "O_ENTRY_D": 1, "ORDER_LINE":1},
                                     session=s).sort("O_ID", direction=pymongo.DESCENDING).limit(1)[0]
        else:
            order = self.orders.find({"O_W_ID": w_id, "O_D_ID": d_id, "O_C_ID": c_id, "$comment": comment},
                                     {"O_ID": 1, "O_CARRIER_ID": 1, "O_ENTRY_D": 1},
                                     session=s).sort("O_ID", direction=pymongo.DESCENDING).limit(1)[0]
        assert order, "No order found for customer!"
        o_id = order["O_ID"]

        # getOrderLines
        if self.denormalize:
            assert constants.TABLENAME_ORDER_LINE in order, "No ORDER_LINE, order %s" % repr(order)
            order_lines = order[constants.TABLENAME_ORDER_LINE]
        else:
            order_lines = self.order_line.find({"OL_W_ID": w_id, "OL_D_ID": d_id, "OL_O_ID": o_id,
                                                "$comment": comment},
                                               {"OL_SUPPLY_W_ID": 1,
                                                "OL_I_ID": 1,
                                                "OL_QUANTITY": 1,
                                                "OL_AMOUNT": 1,
                                                "OL_DELIVERY_D": 1}, session=s)
        ## IF

        return [c, order, order_lines]

    ## ----------------------------------------------
    ## doPayment
    ## ----------------------------------------------
    def doPayment(self, params):
        (value, retries) = self.run_transaction_with_retries(self._doPaymentTxn, "PAYMENT", params)
        return (value, retries)

    def _doPaymentTxn(self, s, params):
        w_id = params["w_id"]
        d_id = params["d_id"]
        h_amount = params["h_amount"]
        c_w_id = params["c_w_id"]
        c_d_id = params["c_d_id"]
        c_id = params["c_id"]
        c_last = params["c_last"]
        h_date = params["h_date"]
        comment = "PAYMENT"

        # getDistrict
        district_project = {"D_NAME": 1,
                            "D_STREET_1": 1,
                            "D_STREET_2": 1,
                            "D_CITY": 1,
                            "D_STATE": 1,
                            "D_ZIP": 1}
        if self.find_and_modify:
            # d = self.district.find_one_and_update({"D_ID": d_id, "D_W_ID": w_id,
            #                                        "$comment": comment},
            #                                       {"$inc":{"D_YTD":h_amount}},
            #                                       projection=district_project,
            #                                       session=s)
            d = self.district.find_one_and_update(
                {"D_ID": d_id, "D_W_ID": w_id},  # Query
                {"$inc": {"D_YTD": h_amount}},  # Update
                projection=district_project,
                session=s,
                comment=comment)  # Pass comment separately

            if not d:
                d1 = self.district.find_one({"D_ID": d_id, "D_W_ID": w_id, "$comment": "payment did not find district"})
                print((d1, w_id, d_id, h_amount, c_w_id, c_d_id, c_id, c_last, h_date))
            assert d, "Couldn't find district in payment w_id %d d_id %d" % (w_id, d_id)
        else:
            d = self.district.find_one({"D_W_ID": w_id, "D_ID": d_id, "$comment": comment},
                                       district_project,
                                       session=s)
            assert d, "Couldn't find district in payment w_id %d d_id %d" % (w_id, d_id)
            # updateDistrictBalance
            self.district.update_one({"_id": d["_id"], "$comment": comment},
                                     {"$inc": {"D_YTD": h_amount}}, session=s)
        ## IF

        warehouse_project = {"W_NAME": 1,
                             "W_STREET_1": 1,
                             "W_STREET_2": 1,
                             "W_CITY": 1,
                             "W_STATE": 1,
                             "W_ZIP": 1}
        if self.find_and_modify:
            w = self.warehouse.find_one_and_update({"W_ID": w_id, "$comment": comment},
                                                   {"$inc":{"W_YTD":h_amount}},
                                                   projection=warehouse_project,
                                                   session=s)
            assert w, "Couldn't find warehouse in payment w_id %d" % (w_id)
        else:
            # getWarehouse
            w = self.warehouse.find_one({"W_ID": w_id, "$comment": comment},
                                        warehouse_project,
                                        session=s)
            assert w, "Couldn't find warehouse in payment w_id %d" % (w_id)
            # updateWarehouseBalance
            self.warehouse.update_one({"_id": w["_id"], "$comment": comment},
                                      {"$inc": {"W_YTD": h_amount}},
                                      session=s)
        ## IF

        search_fields = {"C_W_ID": w_id, "C_D_ID": d_id, "$comment": comment}
        return_fields = {"C_BALANCE": 0, "C_YTD_PAYMENT": 0, "C_PAYMENT_CNT": 0}

        if c_id != None:
            # getCustomerByCustomerId
            search_fields["C_ID"] = c_id
            c = self.customer.find_one(search_fields, return_fields, session=s)
            assert c, "No customer in payment w_id %d d_id %d c_id %d" % (w_id, d_id, c_id)
        else:
            # getCustomersByLastName
            # Get the midpoint customer's id
            search_fields['C_LAST'] = c_last
            all_customers = list(self.customer.find(search_fields, return_fields, session=s))
            namecnt = len(all_customers)
            assert namecnt > 0, "No matching customer w %d d %d clast %s" % (w_id, d_id, c_last)
            index = (namecnt-1)//2
            c = all_customers[index]
            c_id = c["C_ID"]
        ## IF

        assert c_id != None, "Didn't find any matching c_id"

        c_data = c["C_DATA"]

        # Build CUSTOMER update command
        customer_update = {"$inc": {"C_BALANCE": h_amount*-1,
                                    "C_YTD_PAYMENT": h_amount,
                                    "C_PAYMENT_CNT": 1}}

        # Customer Credit Information
        if c["C_CREDIT"] == constants.BAD_CREDIT:
            new_data = " ".join(map(str, [c_id, c_d_id, c_w_id, d_id, w_id, h_amount]))
            c_data = (new_data + "|" + c_data)
            if len(c_data) > constants.MAX_C_DATA:
                c_data = c_data[:constants.MAX_C_DATA]
            customer_update["$set"] = {"C_DATA": c_data}
        ## IF

        # Concatenate w_name, four spaces, d_name
        h_data = "%s    %s" % (w["W_NAME"], d["D_NAME"])

        h = {"H_D_ID": d_id,
             "H_C_ID": c_id,
             "H_C_W_ID": c_w_id,
             "H_C_D_ID": c_d_id,
             "H_W_ID": w_id,
             "H_DATE": h_date,
             "H_AMOUNT": h_amount,
             "H_DATA": h_data}

        # updateCustomer
        self.customer.update_one({"_id": c["_id"], "$comment": comment}, customer_update, session=s)

        # insertHistory
        self.history.insert_one(h, session=s)

        # TPC-C 2.5.3.3: Must display the following fields:
        # W_ID, D_ID, C_ID, C_D_ID, C_W_ID, W_STREET_1, W_STREET_2, W_CITY, W_STATE, W_ZIP,
        # D_STREET_1, D_STREET_2, D_CITY, D_STATE, D_ZIP, C_FIRST, C_MIDDLE, C_LAST, C_STREET_1,
        # C_STREET_2, C_CITY, C_STATE, C_ZIP, C_PHONE, C_SINCE, C_CREDIT, C_CREDIT_LIM,
        # C_DISCOUNT, C_BALANCE, the first 200 characters of C_DATA (only if C_CREDIT = "BC"),
        # H_AMOUNT, and H_DATE.

        # Hand back all the warehouse, district, and customer data
        return [w, d, c]

    ## ----------------------------------------------
    ## doStockLevel
    ## never requires transaction
    ## ----------------------------------------------
    def doStockLevel(self, params):
        return (self._doStockLevelTxn(None, params), 0)

    def _doStockLevelTxn(self, s, params):
        w_id = params["w_id"]
        d_id = params["d_id"]
        threshold = params["threshold"]
        comment = "STOCK_LEVEL"

        if self.agg and self.denormalize:
            result = list(self.district.aggregate([
                {"$match":{"D_W_ID":w_id, "D_ID":d_id}},
                {"$limit":1},
                {"$project":{"_id":0,
                             "O_ID": {"$range": [
                                 {"$subtract" : ["$D_NEXT_O_ID", 20]},
                                 "$D_NEXT_O_ID"]}}},
                {"$unwind" : "$O_ID"},
                {"$lookup":{"from":"ORDERS", "as":"o", "let":{"oid":"$O_ID"}, "pipeline":[
                    {"$match":{"O_D_ID":d_id, "O_W_ID":w_id, "$expr":{"$eq":["$O_ID", "$$oid"]}}},
                    {"$project":{"_id":0, "I_IDS":"$ORDER_LINE.OL_I_ID"}}
                ]}},
                {"$unwind" : "$o"},
                {"$unwind" : "$o.I_IDS"},
                {"$lookup":{"from":"STOCK", "as":"o", "let":{"ids":"$o.I_IDS"}, "pipeline":[
                    {"$match":{"S_W_ID":w_id, "S_QUANTITY": {"$lt": threshold},
                               "$expr":{"$eq":["$S_I_ID", "$$ids"]}}},
                    {"$project":{"S_W_ID":1}}
                ]}},
                {"$unwind":"$o"},
                {"$count":"c"}]))
            if not result:
                return 0
            return int(result[0]["c"])

        d = self.district.find_one({"D_W_ID": w_id, "D_ID": d_id, "$comment": comment},
                                   {"_id":0, "D_NEXT_O_ID": 1}, session=s)

        assert d, "Didn't find matching district in stock level w_id %d d_id %d" % (w_id, d_id)
        o_id = d["D_NEXT_O_ID"]

        # getStockCount
        if self.denormalize:
            os = list(self.orders.find({"O_W_ID": w_id,
                                        "O_D_ID": d_id,
                                        "O_ID": {"$lt": o_id, "$gte": o_id-20},
                                        "$comment": comment},
                                       {"ORDER_LINE.OL_I_ID": 1}, session=s))
            if not os:
                logging.warning("Didn't match orders in stock level w_id %d d_id %d o_id %d",
                                w_id, d_id, o_id)
                # sleep one second and try again
                # TODO if self read preference is secondary then try it from primary
                sleep(1)
                os = list(self.orders.find({"O_W_ID": w_id,
                                            "O_D_ID": d_id,
                                            "O_ID": {"$lt": o_id, "$gte": o_id-20},
                                            "$comment": comment},
                                           {"ORDER_LINE.OL_I_ID": 1}, session=s))
                assert os, "didn't find orders in stock level %d %d %d" % (w_id, d_id, o_id)

            order_lines = []
            for o in os:
                assert "ORDER_LINE" in o, "ORDER_LINE not in order %d %d %d" % (w_id, d_id, o_id)
                order_lines.extend(o["ORDER_LINE"])
            ## FOR
        else:
            order_lines = list(self.order_line.find({"OL_W_ID": w_id,
                                                     "OL_D_ID": d_id,
                                                     "OL_O_ID": {"$lt": o_id, "$gte": o_id-20},
                                                     "$comment": comment},
                                                    {"_id":0, "OL_I_ID": 1},
                                                    batch_size=1000, session=s))
        ## IF

        assert order_lines, "order_lines should not be empty/null %d %d %d" % (w_id, d_id, o_id)
        ol_ids = set()
        for ol in order_lines:
            ol_ids.add(ol["OL_I_ID"])
        ## FOR

        result = self.stock.count_documents({"S_W_ID": w_id,
                                  "S_I_ID": {"$in": list(ol_ids)},
                                  "S_QUANTITY": {"$lt": threshold}, "$comment": comment})

        return int(result)


    def run_transaction(self, txn_callback, session, name, params):

        """
        Executes a transaction using the provided callback function and session.

        Args:
            txn_callback (callable): The function to execute within the transaction.
            session (pymongo.client_session.ClientSession): The session to use for the transaction.
            name (str): The name of the transaction (used for logging).
            params (dict): Additional parameters to pass to the transaction callback.

        Returns:
            tuple: (success, result), where success is a boolean indicating whether
                the transaction succeeded, and result is the return value of txn_callback or None.
        """
        if self.no_transactions:
            # If transactions are disabled, execute the callback directly
            return (True, txn_callback(session, params))

        # Start a transaction and execute the callback
        session.start_transaction()
        try:
            logging.debug("Starting transaction for operation: %s", name)
            result = txn_callback(session, params)
            logging.debug("Transaction for operation '%s' completed successfully", name)
            # Commit the transaction if everything is successful
            if session.in_transaction:
                session.commit_transaction()
            return (True, result)
        except Exception as e:
            # Abort the transaction in case of an error            print(f"Error: {e}")
            if session.in_transaction:
                session.abort_transaction()

        except pymongo.errors.OperationFailure as exc:
            # Handle specific transient transaction errors
            if exc.has_error_label("TransientTransactionError"):
                logging.debug(
                    "TransientTransactionError during operation '%s': Code %d, Details: %s",
                    name, exc.code, exc.details
                )
                return (False, None)

            # Log unknown OperationFailure and re-raise
            logging.error(
                "Unknown OperationFailure during operation '%s': Code %d, Details: %s",
                name, exc.code, exc.details
            )
            print(f"OperationFailure during {name}: Code {exc.code}")
            print(exc.details)
            raise

        except pymongo.errors.ConnectionFailure as exc:
            # Handle connection issues gracefully
            logging.warning(
                "ConnectionFailure during operation '%s': %s", name, str(exc)
            )
            print(f"ConnectionFailure during {name}: {exc}")
            return (False, None)

        except Exception as exc:
            # Catch and log unexpected exceptions
            logging.error(
                "Unexpected error during operation '%s': %s", name, str(exc)
            )
            print(f"Unexpected error during {name}: {exc}")
            raise

    def run_transaction_with_retries(self, txn_callback, name, params):
        """
        Runs a transaction with retries in case of transient errors.

        Args:
            txn_callback (callable): The function to execute within the transaction.
            name (str): The name of the transaction (used for logging).
            params (dict): Parameters to pass to the transaction callback.

        Returns:
            tuple: (result, retry_count), where result is the return value of txn_callback
                and retry_count is the number of retries attempted.
        """
        txn_retry_counter = 0

        # Define transaction options
        transaction_options = TransactionOptions(
            read_concern=pymongo.read_concern.ReadConcern("snapshot"),
            write_concern=self.write_concern,
            read_preference=pymongo.read_preferences.Primary()
        )

        # Start a session with the transaction options
        with self.client.start_session(
            default_transaction_options=transaction_options,
            causal_consistency=self.causal_consistency
        ) as session:
            while True:
                try:
                    # Attempt to run the transaction
                    try:
                        ok, value = self.run_transaction(txn_callback, session, name, params)
                    except Exception as e:
                        print(f"Error: {e}")
                        
                    if ok:
                        if txn_retry_counter > 0:
                            logging.debug(
                                "Transaction '%s' committed successfully after %d retries.",
                                name,
                                txn_retry_counter
                            )
                        return value, txn_retry_counter

                    # If the transaction fails, log and retry
                    txn_retry_counter += 1
                    logging.debug(
                        "Retrying transaction '%s'. Retry count: %d",
                        name,
                        txn_retry_counter
                    )
                    sleep(txn_retry_counter * 0.1)  # Exponential backoff

                except pymongo.errors.OperationFailure as exc:
                    # Handle retryable transaction errors
                    if exc.has_error_label("TransientTransactionError"):
                        txn_retry_counter += 1
                        logging.debug(
                            "TransientTransactionError during '%s'. Retry count: %d. Details: %s",
                            name,
                            txn_retry_counter,
                            exc.details
                        )
                        sleep(txn_retry_counter * 0.1)  # Exponential backoff
                        continue

                    # Log and re-raise non-retryable OperationFailure
                    logging.error(
                        "Non-retryable OperationFailure during '%s': Code %d, Details: %s",
                        name,
                        exc.code,
                        exc.details
                    )
                    raise

                except pymongo.errors.ConnectionFailure as exc:
                    # Handle connection failures gracefully
                    txn_retry_counter += 1
                    logging.warning(
                        "ConnectionFailure during '%s'. Retry count: %d. Details: %s",
                        name,
                        txn_retry_counter,
                        str(exc)
                    )
                    sleep(txn_retry_counter * 0.1)  # Exponential backoff
                    continue

                except Exception as exc:
                    # Log unexpected errors and re-raise
                    logging.error(
                        "Unexpected error during '%s'. Details: %s",
                        name,
                        str(exc)
                    )
                    raise

    def get_server_status(self):
        ss=self.client.admin.command('serverStatus')
        if "$configServerState" in ss:
           del ss["$configServerState"]
        if "$gleStats" in ss:
           del ss["$gleStats"]
        if "$clusterTime" in ss:
           del ss["$clusterTime"]
        if "transportSecurity" in ss:
           del ss["transportSecurity"]
        if "metrics" in ss and "aggStageCounters" in ss["metrics"]:
           del ss["metrics"]["aggStageCounters"]
        if "metrics" in ss and "operatorCounters" in ss["metrics"] and "expressions" in ss["metrics"]["operatorCounters"]:
           del ss["metrics"]["operatorCounters"]["expressions"]
        if "metrics" in ss and "operatorCounters" in ss["metrics"] and "match" in ss["metrics"]["operatorCounters"]:
           del ss["metrics"]["operatorCounters"]["match"]
        return ss

    def save_result(self, result_doc):
        self.result_doc.update(result_doc)
        self.result_doc['after']=self.get_server_status()
        # saving test results and server statuses ('before' and 'after') into MongoDB as a single document
        self.client.test.results.insert_one(self.result_doc)

## CLASS
