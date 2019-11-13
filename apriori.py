import itertools
import csv
import para
import timeit

def readCVSfile(f_name, max_attr=100):
    
    with open(f_name, 'r') as f:
        list_val = list(csv.reader(f, delimiter=','))
    final_output= []
    for i in xrange(len(list_val)):
        list_attr = []
        for val in list_val[i][1:]:
            val = val.strip()
            if int(val) <= max_attr:
                list_attr.append(val)
        if len(list_attr) > 0:
            final_output.append(list_attr)
    return final_output


def runApriori(data, support, confidence):
    transactions = len(data)
    hashmap = {}
    for row in data:
        for word in row:
            if word not in hashmap.keys():
                hashmap[word] = 1
            else:
                hashmap[word] += 1

    level = []
    for key in hashmap:
        if (100 * hashmap[key] / transactions) >= float(support):
            level.append([key])

    return findMaximal(level, support, confidence)


def subsets(S, m):
    return set(itertools.combinations(S, m))


def frequentItemsets(dataset, prev_l, k):
    list = subsets(dataset, k)
    for item in list:
        s = []
        for l in item:
            s.append(l)
        s.sort()
        if s not in prev_l:
            return True
    return False


def apply_support(singles, support):
    k = 2
    prev_l = []
    L = []
    for item in singles:
        prev_l.append(item)
    while prev_l:
        current = []
        sets = apriori_simple_imp(prev_l, k - 1)
        for c in sets:
            cnt = 0
            trans = len(data)
            s = set(c)
            for T in data:
                t = set(T)
                if s.issubset(t):
                    cnt += 1
            if (100 * cnt / trans) >= float(support):
                c.sort()
                current.append(c)
        prev_l = []
        for l in current:
            prev_l.append(l)
        k += 1
        if current:
            L.append(current)
    # for item in L:
    #     for x in item:
    #         print x
    return L


def findMaximal(singles, support, confidence):
    
    num = 1
    L = apply_support(singles, support)
    result = 0
    for list in L:
        for l in list:
            length = len(l)
            count = 1
            while count < length:
                r = subsets(l, count)
                count += 1
                for item in r:
                    inc1 = 0
                    inc2 = 0
                    s = []
                    m = []
                    for i in item:
                        s.append(i)
                    for T in data:
                        if set(s).issubset(set(T)):
                            inc1 += 1
                        if set(l).issubset(set(T)):
                            inc2 += 1
                    if 100 * inc2 / inc1 >= float(confidence):
                        for index in l:
                            if index not in s:
                                m.append(index)
                        #print(s, " ==> ", set(l) - set(s))
                        left = ','.join(s)
                        right = ','.join(set(l) - set(s))
                        print (' ==> '.join([left, right]))
                        result += 1
                        num += 1

    print('Total rules generated:', result)
    elapsed_time_secs = timeit.default_timer() - start_time
    print("Program Executed in "+str(elapsed_time_secs))
    return result


def apriori_simple_imp(prev_l, k):
    list_len = k
    l_previous=prev_l
    result = []
    for data_list_one in l_previous:
        for data_list_two in l_previous:
            count_list = 0
            item_list_a= []
            if data_list_one != data_list_two:
                while count_list < list_len - 1:
                    if data_list_one[count_list] != data_list_two[count_list]:
                        break
                    else:
                        count_list += 1
                else:
                    if data_list_one[list_len - 1] < data_list_two[list_len - 1]:
                        for item in data_list_one:
                            item_list_a.append(item)
                        item_list_a.append(data_list_two[list_len - 1])
                        if not frequentItemsets(item_list_a, prev_l, k):
                            result.append(item_list_a)
    return result


start_time = timeit.default_timer()
data = readCVSfile('out1.csv')
runApriori(data, para.SUPPORT, para.CONFIDENCE)
