import os
import pydot
from fnmatch import fnmatch


IDENTIFIER="_"


class Tree(object):

    highlight_color = "turquoise3"

    def __init__(self, path, focus, ignore):

        self.path = path
        self.focus = focus
        self.ignore = ignore


    def parse(self):

        self.jobs = {}
        self.output = {}

        # Discover the jobs and their output
        job = None
        for root, dirs, files in os.walk(self.path):
            isjob = root.endswith(IDENTIFIER)
            if isjob:
                # Job
                job = Job(self, root)
                self.jobs[job.relpath] = job

            if isjob or root.find(IDENTIFIER) != -1:
                for f in files:
                    # Output
                    output = Output(self, job, os.path.join(root, f))
                    self.output[os.path.join(job.relpath, output.relpath)] = output
                    job.output.append(output)

        # Read and resolve the dependencies of each piece of output
        for output in self.output.itervalues():
            output.read_dependencies()
            try:
                output.dependencies = [self.output[d] for d in output.dependencies]
            except KeyError:
                raise ValueError(output.path, d)

        # Apply the focus
        for f in self.focus:
            for path, job in self.jobs.iteritems():
                if fnmatch(path, f):
                    job.focus = True
            for path, output in self.output.iteritems():
                if fnmatch(path, f):
                    output.focus = True


    def print_text(self):

        for job in self.jobs.itervalues():
            print "%s (%d)" % (job.name, len(job.output))
            for output in job.output:
                print "\t%s (%d)" % (output.relpath, len(output.dependencies))
                for dependency in output.dependencies:
                    print "\t\t%s/%s" % (dependency.job.relpath, dependency.relpath)


    def write(self, path, format='dot'):

        # Prepare the graph
        graph = pydot.Dot('flow', graph_type='digraph')
        graph.set_graph_defaults(rankdir="LR", nodesep="+1,1", ranksep="4")
        graph.set_node_defaults(shape="plaintext")
        graph.set_edge_defaults(color="#00000033")

        # Add in the jobs
        for job in self.jobs.itervalues():

            # Construct the HTML for the output rows
            if job.output:
                output_html = "<TR>" + "</TR><TR>".join(['<TD PORT="%s"%s>%s</TD>' % (o.node_port, (' COLOR="%s"' % self.highlight_color) * o.focus, o.relpath) for o in job.output]) + "</TR>"
            else:
                output_html = ""

            # Construct the job node
            job_node = pydot.Node(job.node_name, label=(u'<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0"><TR><TD><FONT FACE="monospace">%s</FONT></TD></TR>%s</TABLE>>' % (job.name, output_html)).encode('UTF-8'))
            if job.focus:
                job_node.set('color', self.highlight_color)
            graph.add_node(job_node)

            # Add in the relationships
            for output in job.output:
                for dep in output.dependencies:
                    edge = pydot.Edge(dep.node_name, output.node_name)
                    if dep.focus or output.focus or dep.job.focus or output.job.focus:
                        edge.set('color', self.highlight_color)
                    elif self.ignore:
                        continue
                    graph.add_edge(edge)

        graph.write(path, format=format)



class Job(object):

    def __init__(self, tree, path):

        self.tree = tree
        self.path = path
        self.relpath = path[len(tree.path)+1:]
        self.name = self.relpath[:-1].replace("/", ".")
        self.node_name = self.name.replace('.', '_')

        self.output = []
        self.focus = False



class Output(object):

    def __init__(self, tree, job, path):

        self.tree = tree
        self.job = job
        self.path = path
        self.relpath = path[len(job.path)+1:]
        self.dependencies = []

        self.node_port = 'o'+self.relpath.replace('/', '')
        self.node_name = self.job.node_name +':'+ self.node_port

        self.focus = False


    def read_dependencies(self):

        self.dependencies = map(str.rstrip, list(iter(file(self.path))))
