import csv, itertools, para
import timeit


def readCVSfile(filename):
   
    reader = csv.reader(open(filename, 'r'), delimiter=',')
    trans = [map(int, row[1:]) for row in reader]
    return trans


def frequentItem(data_set, support):
    
    candidate_one = {}
    total = len(data_set)
    for row in data_set:
        for val in row:
            if val in candidate_one:
                candidate_one[val] += 1
            else:
                candidate_one[val] = 1

    frequent_1 = []
    for key, cnt in candidate_one.items():
        # check if given item has sufficient count.
        if cnt >= (support * total / 100):
            frequent_1.append(([key], cnt))
    return frequent_1


class HashNode:
   
    def __init__(self):
        self.children = {}
        self.isLeaf = True
        self.bucket = {}


class HashTree:
    
    def __init__(self, max_leaf_cnt, max_child_cnt):
        self.root = HashNode()
        self.max_leaf_cnt = max_leaf_cnt
        self.max_child_cnt = max_child_cnt
        self.frequent_itemsets = []

    def recur_insert(self, node, itemset, index, cnt):
        
        if index == len(itemset):
            # last bucket so just insert
            if itemset in node.bucket:
                node.bucket[itemset] += cnt
            else:
                node.bucket[itemset] = cnt
            return

        if node.isLeaf:

            if itemset in node.bucket:
                node.bucket[itemset] += cnt
            else:
                node.bucket[itemset] = cnt
            if len(node.bucket) == self.max_leaf_cnt:
               
                for old_itemset, old_cnt in node.bucket.iteritems():

                    hash_key = self.hash(old_itemset[index])
                    if hash_key not in node.children:
                        node.children[hash_key] = HashNode()
                    self.recur_insert(node.children[hash_key], old_itemset, index + 1, old_cnt)
              
                del node.bucket
                node.isLeaf = False
        else:
            hash_key = self.hash(itemset[index])
            if hash_key not in node.children:
                node.children[hash_key] = HashNode()
            self.recur_insert(node.children[hash_key], itemset, index + 1, cnt)

    def insert(self, itemset):
        
        itemset = tuple(itemset)
        self.recur_insert(self.root, itemset, 0, 0)

    def add_support(self, itemset):
        runner = self.root
        itemset = tuple(itemset)
        index = 0
        while True:
            if runner.isLeaf:
                if itemset in runner.bucket:
                    runner.bucket[itemset] += 1
                break
            hash_key = self.hash(itemset[index])
            if hash_key in runner.children:
                runner = runner.children[hash_key]
            else:
                break
            index += 1

    def dfs(self, node, support_cnt):
        if node.isLeaf:
            for key, value in node.bucket.iteritems():
                if value >= support_cnt:
                    self.frequent_itemsets.append((list(key), value))
                    # print key, value, support_cnt
            return

        for child in node.children.values():
            self.dfs(child, support_cnt)

    def get_frequent_itemsets(self, support_cnt):
       
        self.frequent_itemsets = []
        self.dfs(self.root, support_cnt)
        return self.frequent_itemsets

    def hash(self, val):
        return val % self.max_child_cnt


def hashTree(candidate_itemsets, length, max_leaf_cnt=4, max_child_cnt=5):
  
    htree = HashTree(max_child_cnt, max_leaf_cnt)
    for itemset in candidate_itemsets:
       
        htree.insert(itemset)
    return htree


def generateKSubsets(dataset, length):
    subsets = []
    for itemset in dataset:
        subsets.extend(map(list, itertools.combinations(itemset, length)))
    return subsets


def checkPrefix(list_1, list_2):
    for i in range(len(list_1) - 1):
        if list_1[i] != list_2[i]:
            return False
    return True


def aprioriFrequentItemsets(dataset, support):
    
    support_cnt = int(support / 100.0 * len(dataset))
    all_frequent_itemsets = frequentItem(dataset, support)
    prev_frequent = [x[0] for x in all_frequent_itemsets]
    length = 2
    while len(prev_frequent) > 1:
        new_candidates = []
        for i in range(len(prev_frequent)):
            j = i + 1
            while j < len(prev_frequent) and checkPrefix(prev_frequent[i], prev_frequent[j]):
               #sorting
                new_candidates.append(prev_frequent[i][:-1] +
                                      [prev_frequent[i][-1]] +
                                      [prev_frequent[j][-1]]
                                      )
                j += 1

        #  find frequent itemsets
        h_tree = hashTree(new_candidates, length)
       
        k_subsets = generateKSubsets(dataset, length)

     
        for subset in k_subsets:
            h_tree.add_support(subset)

       
        new_frequent = h_tree.get_frequent_itemsets(support_cnt)
        all_frequent_itemsets.extend(new_frequent)
        prev_frequent = [tup[0] for tup in new_frequent]
        prev_frequent.sort()
        length += 1

    return all_frequent_itemsets


def generateRules(f_itemsets, confidence):
  

    hash_map = {}
    for itemset in f_itemsets:
        hash_map[tuple(itemset[0])] = itemset[1]

    a_rules = []
    for itemset in f_itemsets:
        length = len(itemset[0])
        if length == 1:
            continue

        union_support = hash_map[tuple(itemset[0])]
        for i in range(1, length):

            lefts = map(list, itertools.combinations(itemset[0], i))
            for left in lefts:
                conf = 100.0 * union_support / hash_map[tuple(left)]
                if conf >= confidence:
                    a_rules.append([left,list(set(itemset[0]) - set(left)), conf])
    return a_rules


def print_final_value(rules):

    for item in rules:
        left = ','.join(map(str, item[0]))
        right = ','.join(map(str, item[1]))
        print (' ==> '.join([left, right]))
        
    elapsed_time_secs = timeit.default_timer() - start_time
    print("Program Executed in "+str(elapsed_time_secs))
    print('Total Rules Generated: ', len(rules))

if __name__ == '__main__':
    start_time = timeit.default_timer()
    transactions = readCVSfile('out1.csv')
  
    frequent = aprioriFrequentItemsets(transactions, para.SUPPORT)

    a_rules = generateRules(frequent, para.CONFIDENCE)
    print_final_value(a_rules)