from django_bootstrap import bootstrap
bootstrap()

import sys
import os

from submissions.models import Submission

output_base_dir = ''

def process_line(line):
    items = line.split(',')
    try:
        score = float(items[2])
        if score < 0:
            score = -1
        items[2] = ('%.6f' % score)
        return (items[0],(items[1],items[2]))
    except:
        return None

def readdata(filename):
    lines = sorted([l.strip() for l in open(filename).readlines()])
    data = {}
    for l in lines:
        lout = process_line(l)
        if lout:
            if lout[0] not in data:
                data[lout[0]] = []
            data[lout[0]].append(lout[1])
    return data

def output_path(job_id):
    return '{0}/{1}'.format(output_base_dir, job_id)

def create_out_dir(job_id):
    try:
        os.mkdir(output_path(job_id))
    except:
        pass

def output_header(f, usernames):
    items = []
    items.append(' ' * 15)
    for u in usernames:
        items.append('{0:14}'.format(u))
    f.write(''.join(items) + '\n')
    
def output_line(f, res):
    items = []
    items.append('{0:15}'.format(res[0]))
    for r in res[1]:
        items.append('{0:14}'.format(r))
    f.write(''.join(items) + '\n')
    
    
def output_compare_result(job_id, major, usernames, results):
    f = open('{0}/major-{1}.txt'.format(output_path(job_id),
                                        major),'w')
    output_header(f, usernames)
    for r in results:
        output_line(f, r)
    f.close()
    
def compare(usernames, results):
    #print(results)
    ids = dict([(u,0) for u in usernames])
    compare_results = []
    while True:
        this_result = []
        min_nat_id = None
        for u in usernames:
            if len(results[u]) > ids[u]:
                nat_id = results[u][ids[u]][0]
                if (not min_nat_id) or (nat_id < min_nat_id):
                    min_nat_id = nat_id
        if not min_nat_id:
            break

        #print(min_nat_id)
        
        same = True
        score_set = set()
        for u in usernames:
            if len(results[u]) <= ids[u]:
                this_result.append('-')
                same = False
                continue

            if results[u][ids[u]][0] != min_nat_id:
                this_result.append('-')
                same = False
                continue

            this_result.append(results[u][ids[u]][1])
            score_set.add(results[u][ids[u]][1])
            ids[u] += 1

        #print(ids)
        if not same:
            if (len(score_set) == 1) and ('-1.000000' in score_set):
                continue
            compare_results.append((min_nat_id, this_result))
        elif len(score_set) > 1:
            compare_results.append((min_nat_id, this_result))

    return compare_results


def work(job_id):
    lines = {}
    usernames = []
    submissions = Submission.latest_from_each_user()
    major_set = set()
    for username in submissions.keys():
        sub = submissions[username]
        lines[username] = readdata(sub.uploaded_file.path)
        for m in list(lines[username].keys()):
            major_set.add(m)
        usernames.append(username)

    majors = sorted(list(major_set))

    create_out_dir(job_id)
    for m in majors:
        user_results = {}
        for u in usernames:
            if m in lines[u]:
                user_results[u] = lines[u][m]
            else:
                user_results[u] = []
            
        res = compare(usernames, user_results)
        if len(res) != 0:
            output_compare_result(job_id, m, usernames, res)


def main():
    submissions = Submission.objects.filter(is_inqueue=True).all()
    has_inqueue = (len(submissions) != 0)

    if len(sys.argv) > 1:
        global output_base_dir
        
        output_base_dir = sys.argv[1]
    else:
        print('ERROR')
        quit()
    
    if has_inqueue:
        work(submissions[0].id)

        for s in submissions:
            s.is_inqueue = False
            s.save()

if __name__ == '__main__':
    main()

