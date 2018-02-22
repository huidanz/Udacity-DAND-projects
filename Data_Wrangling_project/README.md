
# 波士顿OpenStreetMap数据研究报告


## 1.研究区域
本项目选择的是美国马赛诸塞州**波士顿**的地图数据集，**下载地址**http://www.openstreetmap.org/relation/2315704#map=10/42.3134/-70.9985 。   
选择理由：波士顿拥有悠久的历史，而且是美国著名高校云集的地方，希望能有机会去旅行。通过研究波士顿的OpenStreetMap数据，能够对波士顿的道路、建筑等有进一步了解，并且实践数据清洗过程。    




## 2.在审查数据时发现的问题


### 2.1.标签类型问题
使用正则表达式审查标签类型时，发现有异常"tag"标签(problemchars)，以及含有冒号进行补充说明属性值的"tag"标签(lower_colon)。


```python
osm_keys {'problemchars': 3, 'lower': 796417, 'other': 478, 'lower_colon': 114559}
```

### 2.2.标签属性问题

审查标签标签类型为"problemchars"以及"lower_colon"的属性，发现部分可以修正的问题：
1. 3个异常标签中含有特殊字符。
2. "addr:state"州的书写不规范，马赛诸塞州出现"MASSACHUSETTS", "Ma"， "MA- MASSACHUSETTS", "MA"等多种写法。
3. "addr:street"街道的书写不规范，"Street","Road","Avenue"等出现多种形式的缩写。

## 3.问题处理
对于审查数据过程中发现的问题，我分别进行了修正。

### 3.1.修正标签"tag"异常key值
通过函数```correct_key()```修正异常key值。


```python
key_mapping = {"(new tag)": "new_tag",
               "service area": "service_area",
               "addr:street_1": "addr:street"}
```


```python
# 修正key值
def correct_key(key):
    if key in key_mapping.keys():
        key = key_mapping[key]
    return key 
```

### 3.2.修正标签"tag"不规范的value值
通过函数```correct_value()```分别修正书写不规范的街道以及州的value值。


```python
state_mapping = {'ma': 'MA',
                 'MA- MASSACHUSETTS' : 'MA',
                 'Ma' : 'MA',
                 'Massachusetts' : 'MA'}

street_mapping = { "St": "Street",
                    "St.": "Street",
                    "ST" : "Street",
                    "St" : "Street",
                    "St," : "Street",
                    "st" : "Street",
                    "street": "Street",
                    "Street." : "Street",
                    "Rd" : "Road",
                    "Rd.": "Road",
                    "rd.": "Road",
                    "Ave": "Avenue",
                    "Ave.":"Avenue",
                    "HIghway": "Highway",
                    "Pkwy" : "Parkway",
                    "Sq." : "Square",
                    "Winsor": "Winsor",
                     }
```


```python
# 修正value值
def correct_value(key, value):
    
    if key == 'addr:state':
        if value in state_mapping.keys():
            value = state_mapping[value]
            
    if key == 'addr:street':
        abbr = value.split(" ")[-1] 
        if abbr in street_mapping.keys():
            value = value.replace(abbr, street_mapping[abbr]) 
            
    return value
```

### 3.3.修正标签"tag"的种类（type)
"tag"标签含有冒号的key值可以进一步拆分用于表明该标签表示的种类（type）。


```python
# 修正type值    
def shape_tag(key):
    if LOWER_COLON.search(key):
        colon_pos = key.index(":")
        k = key[colon_pos+1 :]
        t = key[: colon_pos]
    else:
        k = key
        t = 'regular'
    return k, t   
```

## 3.数据概览

### 3.1.文件大小


```python
boston_massachusetts.osm ...... 418 MB    
BostonOSM.db .................. 244 MB   
nodes.csv ..................... 153 MB   
nodes_tags.csv ............... 16.7 MB   
ways.csv ..................... 20.0 MB   
ways_tags.csv ................ 21.6 MB   
ways_nodes.cv ................ 53.0 MB     
```

### 3.2.节点(Nodes)数


```python
import sqlite3
db = sqlite3.connect("BostonOSM.db")
cur = db.cursor()
```


```python
cur.execute("SELECT count(*) FROM nodes;")
nodes_num = cur.fetchall()
print "Numbers of Nodes:"
print nodes_num
```

    Numbers of Nodes:
    [(1952868,)]
    

### 3.3.途径(Ways)数


```python
cur.execute("SELECT count(*) FROM ways;")
ways_num = cur.fetchall()
print "Numbers of Ways:"
print ways_num
```

    Numbers of Ways:
    [(311064,)]
    

### 3.4.街道（street）数


```python
cur.execute("SELECT key, count(*) \
            FROM (SELECT key FROM nodes_tags WHERE key = 'street' \
            UNION ALL \
            SELECT key FROM ways_tags WHERE key = 'street') AS all_streets;")

street_num = cur.fetchall()
print "Number of streets:"
print "  ", street_num
```

    Number of streets:
       [(u'street', 6491)]
    

### 3.5.唯一用户标识（uid）数
由字段```uid```表示，```nodes```，```ways```表中均有用户记录，进行联合查询。


```python
cur.execute("SELECT count(DISTINCT(users.uid)) \
            FROM (SELECT uid FROM nodes \
            UNION ALL \
            SELECT uid FROM ways) AS users;")
unique_users = cur.fetchall()
print "Unique Users:"
print "  ", unique_users
```

    Unique Users:
       [(1417,)]
    

### 3.6.贡献条目前10的用户


```python
cur.execute("SELECT users.user, users.uid, count(users.uid) as num \
            FROM (SELECT uid, user FROM nodes \
            UNION ALL \
            SELECT uid, user FROM ways) AS users \
            GROUP BY users.uid \
            ORDER BY num DESC \
            LIMIT 10;")
top10_users = cur.fetchall()
print "TOP 10 Users:"
for row in top10_users:
    print "  ", row

db.close()
```

    TOP 10 Users:
       (u'crschmidt', 1034, 1195031)
       (u'jremillard-massgis', 1137433, 428670)
       (u'wambag', 326503, 111183)
       (u'OceanVortex', 354704, 90952)
       (u'morganwahl', 221294, 67051)
       (u'ryebread', 3216582, 65964)
       (u'MassGIS Import', 15750, 58561)
       (u'ingalls_imports', 1137518, 32453)
       (u'Ahlzen', 81285, 28321)
       (u'mapper999', 165061, 14697)
    

## 4.关于数据集的其他想法

OpenStreetMap是一个可供自由编辑的世界地图，通过世界各地用户的贡献，
带来非常便利的地图资源，但充分的自由度也很容易导致编辑内容不规范的情况，此次清洗数据过程中发现存在多种书写不规范的情况。另外，我查看了国内地区的数据集，甚至存在中文和英文混杂，中文简体和繁体混杂的情况，整体比较杂乱。这非常不利于后续对数据的维护，以及利用数据开展相关项目。 

改进建议：在系统中增加一些常用的规范的描述字段，在用户编辑地图时进行提示，引导用户规范输入。    
执行该建议的可能带来的益处：可以引导不同用户均按照统一规范编辑地图，降低后续对数据运营和维护的难度。    
执行该建议的可能带来的风险：增加一定成本，可能设置约束条件后会影响用户活跃度。

## 5.关于项目的小结
通过完成此次OpenStreetMap数据集研究，我对数据清洗流程，以及使用SQL语言查询数据库进行数据探索的方法更加熟悉。数据清洗是一个繁复而细致的过程，需要经过多次“发现问题——解决问题”，不断把原始数据整理得更加简洁、齐整，便于后续调用数据进行进一步分析，这是后续进行数据探索分析的基础。目前我还只能进行最简单的数据清理以及查询，今后需要通过不断进行项目实践来提高自己的技能水平。

### 参考资料
+ Python yield： https://www.ibm.com/developerworks/cn/opensource/os-cn-python-yield/   
+ Python enumerate()：http://www.runoob.com/python/python-func-enumerate.html  
+ sqlite3导入csv：https://discussions.youdaxue.com/t/p3-csv-sqlite-datatype-mismatch/43246/5
