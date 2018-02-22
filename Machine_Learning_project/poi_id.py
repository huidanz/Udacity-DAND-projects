#!/usr/bin/python
# coding=utf-8

import sys
import pickle
sys.path.append("../tools/")

from feature_format import featureFormat, targetFeatureSplit
from tester import dump_classifier_and_data

### Load the dictionary containing the dataset
with open("final_project_dataset.pkl", "r") as data_file:
    data_dict = pickle.load(data_file)

### 查看数据集基本情况
def describe_dataset(data_dict):
    print "num of records:", len(data_dict)
    print "num of features:", len(data_dict.values()[0])-1
    
    poi_records = []
    for record in data_dict:
        if data_dict[record]["poi"] == True:
            poi_records.append(record)
            
    print "num of poi:", len(poi_records) 
    print "num of non_poi", len(data_dict)-len(poi_records) 
    print 

#describe_dataset(data_dict) 



### 统计缺失值
def count_nans(data_dict):
    from collections import defaultdict
    nans_in_features = defaultdict(int)
    for record in data_dict.values():
        for key in record.keys():
            if record[key] == "NaN":
                nans_in_features[key] += 1
    print "number of nans in each features:"
    print nans_in_features
    print

#count_nans(data_dict)  
 


### Task 1: Select what features you'll use.
### features_list is a list of strings, each of which is a feature name.
### The first feature must be "poi".

## 保留缺失值比例低于66.7%的特征
features_list = ['poi', 'salary', 'total_payments', 'long_term_incentive', \
                'exercised_stock_options', 'bonus', 'restricted_stock',\
                'shared_receipt_with_poi', 'total_stock_value', 'expenses',\
                'to_messages', 'from_messages', 'from_this_person_to_poi',\
                'from_poi_to_this_person'] 


             
### Task 2: Remove outliers
## 作图查看是否有明显异常值
def draw(data_dict, xlab, ylab):
    import matplotlib.pyplot
    for point in data_dict.values():
        x = point[xlab]
        y = point[ylab]
        matplotlib.pyplot.scatter(x, y)
    matplotlib.pyplot.xlabel(xlab)
    matplotlib.pyplot.ylabel(ylab)
    matplotlib.pyplot.show()

#draw(data_dict,"total_payments", "total_stock_value")

## 查找异常值
#i = 0
#for point in data_dict.values():
#   if point["total_payments"] != "NaN" and point["total_payments"] > 100000000 :
#        print i
#    i += 1
    
#print data_dict.keys()[65]
#print data_dict.keys()[104]    
data_dict.pop("TOTAL", 0)



### Task 3: Create new feature(s) about emails with poi
### Store to my_dataset for easy export below.
my_dataset = data_dict

def computeFraction(poi_messages, all_messages):
    """ 
        传入与poi之间收/发邮件数poi_messages，收/发邮件总数all_messages
        返回poi相关邮件占邮件总数的比例fraction
        如果邮件数缺失，返回0.
    """
    fraction = 0.
    if poi_messages != "NaN" and all_messages != "NaN":
        fraction = round((float(poi_messages) / all_messages),5)

    return fraction
## 增加新特征："fraction_from_poi"，"fraction_to_poi"
for point in my_dataset.values():
    from_poi_to_this_person = point["from_poi_to_this_person"]
    to_messages = point["to_messages"]
    point["fraction_from_poi"] = computeFraction(from_poi_to_this_person, to_messages)

    from_this_person_to_poi = point["from_this_person_to_poi"]
    from_messages = point["from_messages"]
    point["fraction_to_poi"] = computeFraction(from_this_person_to_poi, from_messages)

all_features = features_list
all_features.append("fraction_from_poi")
all_features.append("fraction_to_poi")




### Extract features and labels from dataset for local testing

data = featureFormat(my_dataset, features_list, sort_keys = True)
labels, features = targetFeatureSplit(data)

# Example starting point. Try investigating other evaluation techniques!

#from sklearn.cross_validation import train_test_split
#from sklearn.model_selection import train_test_split
#features_train, features_test, labels_train, labels_test = \
#    train_test_split(features, labels, test_size=0.3, random_state=42)


### Task 4: Try a varity of classifiers
### Please name your classifier clf for easy export below.
### Note that if you want to do PCA or other multi-stage operations,
### you'll need to use Pipelines. For more info:
### http://scikit-learn.org/stable/modules/pipeline.html

### Task 5: Tune your classifier to achieve better than .3 precision and recall 
### using our testing script. Check the tester.py script in the final project
### folder for details on the evaluation method, especially the test_classifier
### function. Because of the small size of the dataset, the script uses
### stratified shuffle split cross validation. For more info: 
### http://scikit-learn.org/stable/modules/generated/sklearn.cross_validation.StratifiedShuffleSplit.html

# Provided to give you a starting point. Try a variety of classifiers.
from tester import test_classifier


## 使用朴素贝叶斯并调整参数
from sklearn.naive_bayes import GaussianNB
from sklearn.feature_selection import SelectKBest
from sklearn.feature_selection import f_classif
from sklearn.pipeline import Pipeline

select_feature = SelectKBest(f_classif, k=5)
nb_clf = GaussianNB()
nb_pipe_clf = Pipeline([('select_feature', select_feature), ('nb', nb_clf)])

nb_feature = ['poi','salary', 'exercised_stock_options', 'bonus', \
               'total_stock_value', 'fraction_to_poi']

#test_classifier(nb_pipe_clf, my_dataset, all_features)
#test_classifier(nb_clf, my_dataset, nb_feature)

## 使用决策树并调整参数
from sklearn.tree import DecisionTreeClassifier
dt_clf = DecisionTreeClassifier(random_state=0, min_samples_split = 2)
dt_feature = ['poi', 'salary', 'exercised_stock_options', 'bonus', 'fraction_to_poi']

#test_classifier(dt_clf, my_dataset, dt_feature)


## 使用支持向量机并调整参数

from sklearn.preprocessing import MinMaxScaler
from sklearn.svm import SVC
from sklearn.model_selection import GridSearchCV
#from sklearn.feature_selection import f_regression

## 特征缩放

scaler = MinMaxScaler()
#anova = SelectKBest(f_regression, k=5)
svc = SVC()
pipeline = Pipeline([('scaler',scaler), ('svc',svc)])
params = dict(svc__kernel=['linear','rbf'],svc__C=[1,5,10,20])
svm_clf = GridSearchCV(pipeline, param_grid=params)

#test_classifier(svm_clf, my_dataset, nb_feature)

### Task 6: Dump your classifier, dataset, and features_list so anyone can
### check your results. You do not need to change anything below, but make sure
### that the version of poi_id.py that you submit can be run on its own and
### generates the necessary .pkl files for validating your results.


#dump_classifier_and_data(clf, my_dataset, features_list)
dump_classifier_and_data(nb_clf, my_dataset, nb_feature)