import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics import f1_score, normalized_mutual_info_score
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.metrics import f1_score
from sklearn.metrics import accuracy_score
import math

class DBLP_evaluation():
    def __init__(self):
        self.author2id = {}
        self.author_num = 0
        with open('../data/dblp_author_map_id.dat') as infile: #id, author 唯一
            for line in infile.readlines():
                id, author = line.strip().split('\t')[:2]
                id = int(id) - 1
                author = int(author)

                self.author2id[author] = id
                self.author_num += 1

        #load author label
        #id - label
        self.author_label = {}
        self.sample_num = 0
        with open('../data/dblp_author_label.dat') as infile:
            for line in infile.readlines():
                author, label = line.strip().split('\t')[:2]
                author = int(author)
                label = int(label) - 1

                self.author_label[self.author2id[author]] = label # id(emb) -> author <- label //匹配
                self.sample_num += 1

        #self.link_label = list()
        #with open('../data/dblp_lp/dblp_ap.test_0.8_new') as infile:
        #    for line in infile.readlines():
        #        u, b, label = [int(item) for item in line.strip().split()]
        #        self.link_label.append([u, b, label])

        self.train_link_label = []
        with open('../data/dblp_lp/dblp_ap.train_0.8') as infile:
            for line in infile.readlines():
                u, b, label = [int(item) for item in line.strip().split()]
                self.train_link_label.append([u, b, label])

        self.test_link_label = []
        with open('../data/dblp_lp/dblp_ap.test_0.2') as infile:
            for line in infile.readlines():
                u, b, label = [int(item) for item in line.strip().split()]
                self.test_link_label.append([u, b, label])

    def evaluate_author_cluster(self, embedding_matrix):
        embedding_list = embedding_matrix.tolist()

        X = []
        Y = []
        for author in self.author_label:
            X.append(embedding_list[author])
            Y.append(self.author_label[author])

        pred_Y = KMeans(4).fit(np.array(X)).predict(X)
        score = normalized_mutual_info_score(np.array(Y), pred_Y) #NMI

        return score

    def evaluate_author_classification(self, embedding_matrix):
        embedding_list = embedding_matrix.tolist()

        X = []
        Y = []
        for author in self.author_label:
            X.append(embedding_list[author])
            Y.append(self.author_label[author])

        X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.2, random_state=0)
        lr = LogisticRegression()
        lr.fit(X_train, Y_train)

        Y_pred = lr.predict(X_test)
        micro_f1 = f1_score(Y_test, Y_pred, average='micro')
        macro_f1 = f1_score(Y_test, Y_pred, average='macro')
        return micro_f1, macro_f1

    def evaluation_link_prediction(self, embedding_matrix):
        embedding_list = embedding_matrix.tolist()
        train_x = []
        train_y = []
        for a, p, label in self.train_link_label:
            train_x.append(embedding_list[a] + embedding_list[p])
            train_y.append(label)

        test_x = []
        test_y = []
        for a, p, label in self.test_link_label:
            test_x.append(embedding_list[a] + embedding_list[p])
            test_y.append(label)

        lr = LogisticRegression()
        lr.fit(train_x, train_y)

        pred_y = lr.predict_proba(test_x)[:,1]
        pred_label = lr.predict(test_x)

        '''
        test_y = []
        pred_y = []
        pred_label = []
        for u, b, label in self.link_label:
            test_y.append(label)
            pred_y.append(embedding_matrix[u].dot(relation_matrix[1]).dot(embedding_matrix[b]))

            if pred_y[-1] >= 0.5:
                pred_label.append(1)
            else:
                pred_label.append(0)
        '''
        auc = roc_auc_score(test_y, pred_y)
        f1 = f1_score(test_y, pred_label)
        acc = accuracy_score(test_y, pred_label)

        return auc, f1, acc

def str_list_to_float(self, str_list):
    return [float(item) for item in str_list]

if __name__ == '__main__':
    dblp_evaluation = DBLP_evaluation()
