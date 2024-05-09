from pyvis.network import Network
import networkx
from IPython.core.display import display, HTML
from collections import Counter


def make_kg(data_graph, data_graph_resume, num_res, link):
    job_net = Network(height='1000px', width='100%', bgcolor='#222222', font_color='white')

    job_net.barnes_hut()

    sources = data_graph['JOBID']
    targets = data_graph[link]
    values = data_graph['experience_year']
    sources_resume = data_graph_resume['document']
    targets_resume = data_graph_resume['link']


    edge_data = zip(sources, targets, values)
    resume_edge = zip(sources_resume, targets_resume)
    for j, e in enumerate(edge_data):

        src = e[0]
        dst = e[1]
        w = e[2]

        job_net.add_node(src, src, color='#dd4b39', title=src)
        try:
            for d in dst:
                job_net.add_node(d, d, title=d)
        except:
            continue
        for num in w:
            if '1' <= num and num <= '3':
                for d in dst:
                    job_net.add_edge(src, d, value=int(num), color='#b39c92', label=int(num))
            if num > '3' and num < ':':
                for d in dst:
                    job_net.add_edge(src, d, value=int(num), color='#0000FF', label=int(num))
        for num in w:
            flag = num.isdigit()
            if flag == False:
                for d in dst:
                    job_net.add_edge(src, d, value=0, color='#FF00FF', label=0)

    for j, e in enumerate(resume_edge):
        src = e[0]
        dst = e[1]

        job_net.add_node(src, src, color='#ffffff', title=src)
        for d in dst:
            job_net.add_node(d, d, title=d)
            job_net.add_edge(src, d, color='#00ff1e')
        '''
      job_net.add_node(dst, dst, title=dst)
      job_net.add_edge(src, dst, color='#00ff1e')
      '''
    neighbor_map = job_net.get_adj_list()
    for node in job_net.nodes:
        node['title'] += ' Neighbors:<br>' + '<br>'.join(neighbor_map[node['id']])
        node['value'] = len(neighbor_map[node['id']])

    # add neighbor data to node hover data
    job_net.show_buttons(filter_=['physics'])
    job_net.prep_notebook()  # DO NOT OMIT
    job_net.show('job_net1.html')
    display(HTML('job_net1.html'))
    resume_name_list = []
    skills_list = []
    for i in range(len(job_net.nodes)):
        temp = job_net.neighbors(job_net.nodes[i]['id'])
        # print(temp)
        # print(data_graph['JOBID'])
        if data_graph['JOBID'][0] in temp:
            # print(temp)
            for j in range(len(data_graph_resume['document'])):
                # print(data_graph_resume['document'][j])
                # print(temp)
                if data_graph_resume['document'][j] in temp:
                    print(data_graph['JOBID'])
                    print(data_graph_resume['document'][j])
                    print(job_net.nodes[i]['id'])
                    skills_list.append(job_net.nodes[i]['id'])
                    resume_name_list.append(data_graph_resume['document'][j])
    word_counts = Counter(resume_name_list)
    sk_list = Counter(skills_list)


    return word_counts.most_common(len(resume_name_list)), sk_list.most_common(len(skills_list))
