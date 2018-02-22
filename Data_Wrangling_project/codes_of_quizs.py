# -*- coding: utf-8 -*-


### 14-3 迭代解析
import xml.etree.cElementTree as ET
import pprint

def count_tags(filename):
        # YOUR CODE HERE
    tag_data = {}  # 使用字典来存储各个tag计数结果 
    for event, elem in ET.iterparse(filename, events=('start',)):
        
        if elem.tag in tag_data:  # 字典中已有该字段
            tag_data[elem.tag] += 1   
        else:
            tag_data[elem.tag] = 1
        
        elem.clear()
    return tag_data

def test():

    tags = count_tags('example.osm')
    pprint.pprint(tags)
    assert tags == {'bounds': 1,
                     'member': 3,
                     'nd': 4,
                     'node': 20,
                     'osm': 1,
                     'relation': 1,
                     'tag': 7,
                     'way': 1}


        
### 14-6 标签类型
import re

lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')


def key_type(element, keys):
    if element.tag == "tag":
        # YOUR CODE HERE
        for tag in element.iter("tag"):   # 匹配‘tag’元素
            
            if lower.search(tag.attrib['k']):  # 匹配‘tag’的‘k’属性
                keys['lower'] += 1
            elif lower_colon.search(tag.attrib['k']):
                keys['lower_colon'] += 1
            elif problemchars.search(tag.attrib['k']):
                keys['problemchars'] += 1
            else:
                keys['other'] += 1
        
    return keys

def process_map(filename):
    keys = {"lower": 0, "lower_colon": 0, "problemchars": 0, "other": 0}
    for _, element in ET.iterparse(filename):
        keys = key_type(element, keys)

    return keys

def test():
    # You can use another testfile 'map.osm' to look at your solution
    # Note that the assertion below will be incorrect then.
    # Note as well that the test function here is only used in the Test Run;
    # when you submit, your code will be checked against a different dataset.
    keys = process_map('example.osm')
    pprint.pprint(keys)
    assert keys == {'lower': 5, 'lower_colon': 0, 'other': 1, 'problemchars': 1}
    

### 14-7 探索用户

def get_user(element):
    if 'uid' in element.attrib:
        return element.attrib['uid']  # 返回uid值


def process_map(filename):
    users = set()
    for _, element in ET.iterparse(filename):
         
        if get_user(element):
            users.add(get_user(element))

    return users


def test():

    users = process_map('example.osm')
    pprint.pprint(users)
    assert len(users) == 6


### 14-10 完善街道名
from collections import defaultdict

OSMFILE = "example.osm"
street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)


expected = ["Street", "Avenue", "Boulevard", "Drive", "Court", "Place", "Square", "Lane", "Road", "Trail", "Parkway", "Commons"]

# UPDATE THIS VARIABLE
mapping = { "St": "Street",
            "St.": "Street",
            "Rd.": "Road",
            "Ave": "Avenue"
            }


def audit_street_type(street_types, street_name):
    m = street_type_re.search(street_name)  # 使用正则表达式匹配street_type
    if m:
        street_type = m.group()  # group(),匹配正则表达式的整体结果
        if street_type not in expected:
            street_types[street_type].add(street_name)  # 增加街道的表示形式


def is_street_name(elem):
    return (elem.attrib['k'] == "addr:street")  # 返回判断结果， 布尔值
 

def audit(osmfile):
    osm_file = open(osmfile, "r")
    street_types = defaultdict(set)  # 设置字典默认值
    for event, elem in ET.iterparse(osm_file, events=("start",)):

        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_street_name(tag):
                    audit_street_type(street_types, tag.attrib['v'])
    osm_file.close()
    return street_types


def update_name(name, mapping):

    # YOUR CODE HERE
    abbr = name.split(" ")[-1]  # 分离出‘街道’缩写
    if abbr in mapping.keys():   # 匹配mapping中的缩写
        name = name.replace(abbr, mapping[abbr])
    return name


def test():
    st_types = audit(OSMFILE)
    assert len(st_types) == 3
    pprint.pprint(dict(st_types))

    for st_type, ways in st_types.iteritems():
        for name in ways:
            better_name = update_name(name, mapping)
            print name, "=>", better_name
            if name == "West Lexington St.":
                assert better_name == "West Lexington Street"
            if name == "Baldwin Rd.":
                assert better_name == "Baldwin Road"


## 14-11 为数据集做准备-SQL

import csv
import codecs
import cerberus
import schema

OSM_PATH = "example.osm"

NODES_PATH = "nodes.csv"
NODE_TAGS_PATH = "nodes_tags.csv"
WAYS_PATH = "ways.csv"
WAY_NODES_PATH = "ways_nodes.csv"
WAY_TAGS_PATH = "ways_tags.csv"

LOWER_COLON = re.compile(r'^([a-z]|_)+:([a-z]|_)+')
PROBLEMCHARS = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

SCHEMA = schema.schema

# Make sure the fields order in the csvs matches the column order in the sql table schema
NODE_FIELDS = ['id', 'lat', 'lon', 'user', 'uid', 'version', 'changeset', 'timestamp']
NODE_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_FIELDS = ['id', 'user', 'uid', 'version', 'changeset', 'timestamp']
WAY_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_NODES_FIELDS = ['id', 'node_id', 'position']


def shape_element(element, node_attr_fields=NODE_FIELDS, way_attr_fields=WAY_FIELDS,problem_chars=PROBLEMCHARS, default_tag_type='regular'):
    """Clean and shape node or way XML element to Python dict"""

    node_attribs = {}
    way_attribs = {}
    way_nodes = []
    tags = []  # Handle secondary tags the same way for both node and way elements

    # YOUR CODE HERE
    if element.tag == 'node':
        
        # "node"
        for tag in node_attr_fields:  # 存入属性值
            node_attribs[tag] = element.attrib[tag]   
        
        # "node_tags"
        for subelem in element:
            if subelem.tag == 'tag':
                
                k_attr = subelem.attrib['k']
                entry = {}
                if problem_chars.search(k_attr):
                    continue
                elif LOWER_COLON.search(k_attr):
                    colon_pos = k_attr.index(":")
                    entry['key'] = k_attr[colon_pos+1 :]
                    entry['type'] = k_attr[: colon_pos]
                else:
                    entry['key'] = k_attr
                    entry['type'] = default_tag_type
                 
                entry['id'] = element.attrib['id']
                entry['value'] = subelem.attrib['v']
                tags.append(entry)
       
        return {'node': node_attribs, 'node_tags': tags}
    
    elif element.tag == 'way':
        
        # "way"
        for tag in way_attr_fields:
            way_attribs[tag] = element.attrib[tag] 
            
        count = 0    
        for subelem in element:
            
            # "way_tags"
            if subelem.tag == 'tag':
              
                entry = {}
                if problem_chars.search(subelem.attrib['k']):
                    continue
                elif LOWER_COLON.search(subelem.attrib['k']):
                    colon_pos = subelem.attrib['k'].index(":")
                    entry['key'] = subelem.attrib['k'][colon_pos + 1 :]
                    entry['type'] = subelem.attrib['k'][ : colon_pos]
                else:
                    entry['key'] = subelem.attrib['k']
                    entry['type'] = default_tag_type
                 
                entry['id'] = element.attrib['id']
                entry['value'] = subelem.attrib['v']
                
                tags.append(entry)
            
            # "way_nodes"
            if subelem.tag == 'nd':
                entry = {}
                entry['id'] = element.attrib['id']
                entry['node_id'] = subelem.attrib['ref']
                entry['position'] = count
                count += 1 
                way_nodes.append(entry)           
        
        return {'way': way_attribs, 'way_nodes': way_nodes, 'way_tags': tags}
    


# ================================================== #
#               Helper Functions                     #
# ================================================== #
def get_element(osm_file, tags=('node', 'way', 'relation')):
    """Yield element if it is the right type of tag"""

    context = ET.iterparse(osm_file, events=('start', 'end'))
    _, root = next(context)  # 依次提取根元素
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()


def validate_element(element, validator, schema=SCHEMA):
    """Raise ValidationError if element does not match schema"""
    if validator.validate(element, schema) is not True:
        field, errors = next(validator.errors.iteritems())
        message_string = "\nElement of type '{0}' has the following errors:\n{1}"
        error_string = pprint.pformat(errors)
        
        raise Exception(message_string.format(field, error_string))


class UnicodeDictWriter(csv.DictWriter, object):
    """Extend csv.DictWriter to handle Unicode input"""

    def writerow(self, row):
        super(UnicodeDictWriter, self).writerow({
            k: (v.encode('utf-8') if isinstance(v, unicode) else v) for k, v in row.iteritems()
        })

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)
       

 # ================================================== #
#               Main Function                        #
# ================================================== #
def process_map(file_in, validate):
    """Iteratively process each XML element and write to csv(s)"""

    with codecs.open(NODES_PATH, 'w') as nodes_file, \
         codecs.open(NODE_TAGS_PATH, 'w') as nodes_tags_file, \
         codecs.open(WAYS_PATH, 'w') as ways_file, \
         codecs.open(WAY_NODES_PATH, 'w') as way_nodes_file, \
         codecs.open(WAY_TAGS_PATH, 'w') as way_tags_file:

        nodes_writer = UnicodeDictWriter(nodes_file, NODE_FIELDS)
        node_tags_writer = UnicodeDictWriter(nodes_tags_file, NODE_TAGS_FIELDS)
        ways_writer = UnicodeDictWriter(ways_file, WAY_FIELDS)
        way_nodes_writer = UnicodeDictWriter(way_nodes_file, WAY_NODES_FIELDS)
        way_tags_writer = UnicodeDictWriter(way_tags_file, WAY_TAGS_FIELDS)

        nodes_writer.writeheader()
        node_tags_writer.writeheader()
        ways_writer.writeheader()
        way_nodes_writer.writeheader()
        way_tags_writer.writeheader()

        validator = cerberus.Validator()

        for element in get_element(file_in, tags=('node', 'way')):
            el = shape_element(element)
            if el:
                if validate is True:
                    validate_element(el, validator)

                if element.tag == 'node':
                    nodes_writer.writerow(el['node'])
                    node_tags_writer.writerows(el['node_tags'])
                elif element.tag == 'way':
                    ways_writer.writerow(el['way'])
                    way_nodes_writer.writerows(el['way_nodes'])
                    way_tags_writer.writerows(el['way_tags'])


if __name__ == '__main__':
    # Note: Validation is ~ 10X slower. For the project consider using a small
    # sample of the map when validating.
    process_map(OSM_PATH, validate=True)