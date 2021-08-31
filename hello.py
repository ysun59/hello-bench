#!/usr/bin/env python

# The MIT License (MIT)
# 
# Copyright (c) 2015 Tintri
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import os, sys, subprocess, select, random, urllib2, time, json, tempfile, shutil, datetime

NGINX_PORT = 20000
IOJS_PORT = 20001
NODE_PORT = 20002
REGISTRY_PORT = 20003
TMP_DIR = tempfile.mkdtemp()

def exit(status):
    # cleanup
    shutil.rmtree(TMP_DIR)
    sys.exit(status)

def tmp_dir():
    tmp_dir.nxt += 1
    return os.path.join(TMP_DIR, str(tmp_dir.nxt))
tmp_dir.nxt = 0

def tmp_copy(src):
    dst = tmp_dir()
    shutil.copytree(src, dst)
    return dst

class RunArgs:
    def __init__(self, env={}, arg='', stdin='', stdin_sh='sh', waitline='', mount=[]):
        self.env = env
        self.arg = arg
        self.stdin = stdin
        self.stdin_sh = stdin_sh
        self.waitline = waitline
        self.mount = mount

class Bench:
    def __init__(self, name, category='other'):
        self.name = name
        self.repo = name # TODO: maybe we'll eventually have multiple benches per repo
        self.category = category

    def __str__(self):
        return json.dumps(self.__dict__)

class BenchRunner:
    ECHO_HELLO = set(['alpine',
                      'busybox',
                      'crux',
                      'cirros',
                      'debian',
                      'ubuntu',
                      'ubuntu-upstart',
                      'ubuntu-debootstrap',
                      'centos',
                      'fedora',
                      'opensuse',
                      'oraclelinux',
		      'mageia',
                      'alpine1',
                      'busybox1',
                      'crux1',
                      'cirros1',
                      'debian1',
                      'ubuntu1',
                      'ubuntu-upstart1',
                      'ubuntu-debootstrap1',
                      'centos1',
                      'fedora1',
                      'opensuse1',
                      'oraclelinux1',
                      'mageia1',])

    CMD_ARG_WAIT = {'mysql': RunArgs(env={'MYSQL_ROOT_PASSWORD': 'abc'},
                                     waitline='mysqld: ready for connections'),
                    'mysql:sy': RunArgs(env={'MYSQL_ROOT_PASSWORD': 'abc'},
                                     waitline='mysqld: ready for connections'),
                    'percona': RunArgs(env={'MYSQL_ROOT_PASSWORD': 'abc'},
                                     waitline='mysqld: ready for connections'),
                    'mariadb': RunArgs(env={'MYSQL_ROOT_PASSWORD': 'abc'},
                                     waitline='mysqld: ready for connections'),
                    'postgres': RunArgs(waitline='database system is ready to accept connections'),
#                    'redis': RunArgs(waitline='server is now ready to accept connections'),
                    'redis': RunArgs(waitline='Ready to accept connections'),
                    'crate': RunArgs(waitline='started'),
                    'rethinkdb': RunArgs(waitline='Server ready'),
#                    'ghost': RunArgs(waitline='Listening on'),
                    'ghost': RunArgs(waitline='Ghost boot'),
                    'glassfish': RunArgs(waitline='Running GlassFish'),
                    'drupal': RunArgs(waitline='apache2 -D FOREGROUND'),
                    'elasticsearch': RunArgs(waitline='] started'),
#                    'cassandra': RunArgs(waitline='Listening for thrift clients'),
                    'cassandra': RunArgs(waitline='Created default superuser role'),
                    'httpd': RunArgs(waitline='httpd -D FOREGROUND'),
                    'jenkins': RunArgs(waitline='Jenkins is fully up and running'),
                    'jetty': RunArgs(waitline='main: Started'),
#                    'mongo': RunArgs(waitline='waiting for connections'),
                    'mongo': RunArgs(waitline='"config.system.sessions","index":'),
                    'php-zendserver': RunArgs(waitline='Zend Server started'),
                    'rabbitmq': RunArgs(waitline='Server startup complete'),
                    'sonarqube': RunArgs(waitline='Process[web] is up'),
                    'tomcat': RunArgs(waitline='Server startup'),

                    'mysql1': RunArgs(env={'MYSQL_ROOT_PASSWORD': 'abc'},
                                     waitline='mysqld: ready for connections'),
                    'mysql:sy': RunArgs(env={'MYSQL_ROOT_PASSWORD': 'abc'},
                                     waitline='mysqld: ready for connections'),
                    'percona1': RunArgs(env={'MYSQL_ROOT_PASSWORD': 'abc'},
                                     waitline='mysqld: ready for connections'),
                    'mariadb1': RunArgs(env={'MYSQL_ROOT_PASSWORD': 'abc'},
                                     waitline='mysqld: ready for connections'),
                    'postgres1': RunArgs(waitline='database system is ready to accept connections'),
#                    'redis': RunArgs(waitline='server is now ready to accept connections'),
                    'redis1': RunArgs(waitline='Ready to accept connections'),
                    'crate1': RunArgs(waitline='started'),
                    'rethinkdb1': RunArgs(waitline='Server ready'),
#                    'ghost': RunArgs(waitline='Listening on'),
                    'ghost1': RunArgs(waitline='Ghost boot'),
                    'glassfish1': RunArgs(waitline='Running GlassFish'),
                    'drupal1': RunArgs(waitline='apache2 -D FOREGROUND'),
                    'elasticsearch1': RunArgs(waitline='] started'),
#                    'cassandra': RunArgs(waitline='Listening for thrift clients'),
                    'cassandra1': RunArgs(waitline='Created default superuser role'),
                    'httpd1': RunArgs(waitline='httpd -D FOREGROUND'),
                    'jenkins1': RunArgs(waitline='Jenkins is fully up and running'),
                    'jetty1': RunArgs(waitline='main: Started'),
#                    'mongo': RunArgs(waitline='waiting for connections'),
                    'mongo1': RunArgs(waitline='"config.system.sessions","index":'),
                    'php-zendserver1': RunArgs(waitline='Zend Server started'),
                    'rabbitmq1': RunArgs(waitline='Server startup complete'),
                    'sonarqube1': RunArgs(waitline='Process[web] is up'),
                    'tomcat1': RunArgs(waitline='Server startup'),
    }

    CMD_STDIN = {'php':  RunArgs(stdin='php -r "echo \\\"hello\\n\\\";"'),
                 'ruby': RunArgs(stdin='ruby -e "puts \\\"hello\\\""'),
                 'jruby': RunArgs(stdin='jruby -e "puts \\\"hello\\\""'),
                 'julia': RunArgs(stdin='julia -e \'println("hello")\''),
                 'gcc': RunArgs(stdin='cd /src; gcc main.c; ./a.out',
                                mount=[('gcc', '/src')]),
                 'golang': RunArgs(stdin='cd /go/src; go run main.go',
                                   mount=[('go', '/go/src')]),
                 'clojure': RunArgs(stdin='cd /hello/hello; lein run',
                                    mount=[('clojure', '/hello')]),
                 'django': RunArgs(stdin='django-admin startproject hello'),
                 'rails': RunArgs(stdin='rails new hello'),
                 'haskell': RunArgs(stdin='"hello"', stdin_sh=None),
                 'hylang': RunArgs(stdin='(print "hello")', stdin_sh=None),
                 'java': RunArgs(stdin='cd /src; javac Main.java; java Main',
                                   mount=[('java', '/src')]),
                 'mono': RunArgs(stdin='cd /src; mcs main.cs; mono main.exe',
                                   mount=[('mono', '/src')]),
                 'r-base': RunArgs(stdin='sprintf("hello")', stdin_sh='R --no-save'),
                 'thrift': RunArgs(stdin='cd /src; thrift --gen py hello.idl',
                                   mount=[('thrift', '/src')]),
		 'php1':  RunArgs(stdin='php -r "echo \\\"hello\\n\\\";"'),
                 'ruby1': RunArgs(stdin='ruby -e "puts \\\"hello\\\""'),
                 'jruby1': RunArgs(stdin='jruby -e "puts \\\"hello\\\""'),
                 'julia1': RunArgs(stdin='julia -e \'println("hello")\''),
                 'gcc1': RunArgs(stdin='cd /src; gcc main.c; ./a.out',
                                mount=[('gcc', '/src')]),
                 'golang1': RunArgs(stdin='cd /go/src; go run main.go',
                                   mount=[('go', '/go/src')]),
                 'clojure1': RunArgs(stdin='cd /hello/hello; lein run',
                                    mount=[('clojure', '/hello')]),
                 'django1': RunArgs(stdin='django-admin startproject hello'),
                 'rails1': RunArgs(stdin='rails new hello'),
                 'haskell1': RunArgs(stdin='"hello"', stdin_sh=None),
                 'hylang1': RunArgs(stdin='(print "hello")', stdin_sh=None),
                 'java1': RunArgs(stdin='cd /src; javac Main.java; java Main',
                                   mount=[('java', '/src')]),
                 'mono1': RunArgs(stdin='cd /src; mcs main.cs; mono main.exe',
                                   mount=[('mono', '/src')]),
                 'r-base1': RunArgs(stdin='sprintf("hello")', stdin_sh='R --no-save'),
                 'thrift1': RunArgs(stdin='cd /src; thrift --gen py hello.idl',
                                   mount=[('thrift', '/src')]),
             }

    CMD_ARG = {'perl': RunArgs(arg='perl -e \'print("hello\\n")\''),
               'rakudo-star': RunArgs(arg='perl6 -e \'print("hello\\n")\''),
               'pypy': RunArgs(arg='pypy3 -c \'print("hello")\''),
               'python': RunArgs(arg='python -c \'print("hello")\''),
               'hello-world': RunArgs(),
	       'perl1': RunArgs(arg='perl -e \'print("hello\\n")\''),
               'rakudo-star1': RunArgs(arg='perl6 -e \'print("hello\\n")\''),
               'pypy1': RunArgs(arg='pypy3 -c \'print("hello")\''),
               'python1': RunArgs(arg='python -c \'print("hello")\''),
               'hello-world1': RunArgs()}



    # values are function names
    CUSTOM = {'nginx': 'run_nginx',
              'iojs': 'run_iojs',
              'node': 'run_node',
              'registry': 'run_registry',
	      'nginx1': 'run_nginx1',
              'iojs1': 'run_iojs1',
              'node1': 'run_node1',
              'registry1': 'run_registry1'}


    # complete listing
    ALL = dict([(b.name, b) for b in
                [Bench('alpine', 'distro'),
                 Bench('busybox', 'distro'),
                 Bench('crux', 'distro'),
                 Bench('cirros', 'distro'),
                 Bench('debian', 'distro'),
                 Bench('ubuntu', 'distro'),
                 Bench('ubuntu-upstart', 'distro'),
                 Bench('ubuntu-debootstrap', 'distro'),
                 Bench('centos', 'distro'),
                 Bench('fedora', 'distro'),
                 Bench('opensuse', 'distro'),
                 Bench('oraclelinux', 'distro'),
                 Bench('mageia', 'distro'),
                 Bench('mysql', 'database'),
                 Bench('mysql1', 'database'),
		 Bench('mysql:sy', 'database'),
                 Bench('percona', 'database'),
                 Bench('mariadb', 'database'),
                 Bench('postgres', 'database'),
                 Bench('redis', 'database'),
                 Bench('crate', 'database'),
                 Bench('rethinkdb', 'database'),
                 Bench('php', 'language'),
                 Bench('ruby', 'language'),
                 Bench('jruby', 'language'),
                 Bench('julia', 'language'),
                 Bench('perl', 'language'),
                 Bench('rakudo-star', 'language'),
                 Bench('pypy', 'language'),
                 Bench('python', 'language'),
                 Bench('golang', 'language'),
                 Bench('clojure', 'language'),
                 Bench('haskell', 'language'),
                 Bench('hylang', 'language'),
                 Bench('java', 'language'),
                 Bench('mono', 'language'),
                 Bench('r-base', 'language'),
                 Bench('gcc', 'language'),
                 Bench('thrift', 'language'),
                 Bench('cassandra', 'database'),
                 Bench('mongo', 'database'),
                 Bench('elasticsearch', 'database'),
                 Bench('hello-world'),
                 Bench('ghost'),
                 Bench('drupal'),
                 Bench('jenkins'),
                 Bench('sonarqube'),
                 Bench('rabbitmq'),
                 Bench('registry'),
                 Bench('httpd', 'web-server'),
                 Bench('nginx', 'web-server'),
                 Bench('glassfish', 'web-server'),
                 Bench('jetty', 'web-server'),
                 Bench('php-zendserver', 'web-server'),
                 Bench('tomcat', 'web-server'),
                 Bench('django', 'web-framework'),
                 Bench('rails', 'web-framework'),
                 Bench('node', 'web-framework'),
                 Bench('iojs', 'web-framework'),
                 Bench('alpine1', 'distro'),
                 Bench('busybox1', 'distro'),
                 Bench('crux1', 'distro'),
                 Bench('cirros1', 'distro'),
                 Bench('debian1', 'distro'),
                 Bench('ubuntu1', 'distro'),
                 Bench('ubuntu-upstart1', 'distro'),
                 Bench('ubuntu-debootstrap1', 'distro'),
                 Bench('centos1', 'distro'),
                 Bench('fedora1', 'distro'),
                 Bench('opensuse1', 'distro'),
                 Bench('oraclelinux1', 'distro'),
                 Bench('mageia1', 'distro'),
                 Bench('mysql1', 'database'),
                 Bench('percona1', 'database'),
                 Bench('mariadb1', 'database'),
                 Bench('postgres1', 'database'),
                 Bench('redis1', 'database'),
                 Bench('crate1', 'database'),
                 Bench('rethinkdb1', 'database'),
                 Bench('php1', 'language'),
                 Bench('ruby1', 'language'),
                 Bench('jruby1', 'language'),
                 Bench('julia1', 'language'),
                 Bench('perl1', 'language'),
                 Bench('rakudo-star1', 'language'),
                 Bench('pypy1', 'language'),
                 Bench('python1', 'language'),
                 Bench('golang1', 'language'),
                 Bench('clojure1', 'language'),
                 Bench('haskell1', 'language'),
                 Bench('hylang1', 'language'),
                 Bench('java1', 'language'),
                 Bench('mono1', 'language'),
                 Bench('r-base1', 'language'),
                 Bench('gcc1', 'language'),
                 Bench('thrift1', 'language'),
                 Bench('cassandra1', 'database'),
                 Bench('mongo1', 'database'),
                 Bench('elasticsearch1', 'database'),
                 Bench('hello-world1'),
                 Bench('ghost1'),
                 Bench('drupal1'),
                 Bench('jenkins1'),
                 Bench('sonarqube1'),
                 Bench('rabbitmq1'),
                 Bench('registry1'),
                 Bench('httpd1', 'web-server'),
                 Bench('nginx1', 'web-server'),
                 Bench('glassfish1', 'web-server'),
                 Bench('jetty1', 'web-server'),
                 Bench('php-zendserver1', 'web-server'),
                 Bench('tomcat1', 'web-server'),
                 Bench('django1', 'web-framework'),
                 Bench('rails1', 'web-framework'),
                 Bench('node1', 'web-framework'),
                 Bench('iojs1', 'web-framework'),
             ]])

    def __init__(self, docker='docker', registry='localhost:5000', registry2='localhost:5000'):
        self.docker = docker
        self.registry = registry
        if self.registry != '':
            self.registry += '/'
        self.registry2 = registry2
        if self.registry2 != '':
            self.registry2 += '/'
        
    def run_echo_hello(self, repo):
	cmd = './%s run %s%s echo hello' % (self.docker, self.registry, repo)
#       cmd = '%s run %s%s echo hello' % (self.docker, self.registry, repo)
#	cmd = '%s run %s%s echo $(($(date +%%s%%N)/1000000))' % (self.docker, self.registry, repo)
	print cmd
        rc = os.system(cmd)
        assert(rc == 0)

    def run_cmd_arg(self, repo, runargs):
        assert(len(runargs.mount) == 0)
        cmd = './%s run ' % self.docker
#       cmd = '%s run ' % self.docker
        cmd += '%s%s ' % (self.registry, repo)
        cmd += runargs.arg
        print cmd
        rc = os.system(cmd)
        assert(rc == 0)

    def run_cmd_arg_wait(self, repo, runargs):
        name = '%s_bench_%d' % (repo, random.randint(1,1000000))
        env = ' '.join(['-e %s=%s' % (k,v) for k,v in runargs.env.iteritems()])
        cmd = ('./%s run --name=%s %s %s%s %s' %
#       cmd = ('%s run --name=%s %s %s%s %s' %
               (self.docker, name, env, self.registry, repo, runargs.arg))
        print cmd
        # line buffer output
        p = subprocess.Popen(cmd, shell=True, bufsize=1,
                             stderr=subprocess.STDOUT,
                             stdout=subprocess.PIPE)
        while True:
            l = p.stdout.readline()
            if l == '':
                continue
            print 'out: ' + l.strip()
            # are we done?
            if l.find(runargs.waitline) >= 0:
                # cleanup
                print 'DONE'
                cmd = '%s kill %s' % (self.docker, name)
                rc = os.system(cmd)
                assert(rc == 0)
                break
        p.wait()

    def run_cmd_stdin(self, repo, runargs):
        cmd = './%s run ' % self.docker
#       cmd = '%s run ' % self.docker
        for a,b in runargs.mount:
            a = os.path.join(os.path.dirname(os.path.abspath(__file__)), a)
            a = tmp_copy(a)
            cmd += '-v %s:%s ' % (a,b)
        cmd += '-i %s%s ' % (self.registry, repo)
        if runargs.stdin_sh:
            cmd += runargs.stdin_sh # e.g., sh -c

        print cmd
        p = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        print runargs.stdin
        out,_ = p.communicate(runargs.stdin)
        print out
        p.wait()
        assert(p.returncode == 0)

    def run_nginx(self):
        name = 'nginx_bench_%d' % (random.randint(1,1000000))
        cmd = '%s run --name=%s -p %d:%d %snginx' % (self.docker, name, NGINX_PORT, 80, self.registry)
        print cmd
        p = subprocess.Popen(cmd, shell=True)
        while True:
            try:
                req = urllib2.urlopen('http://localhost:%d'%NGINX_PORT)
                req.close()
                break
            except:
                time.sleep(0.01) # wait 10ms
                pass # retry
        cmd = '%s kill %s' % (self.docker, name)
        rc = os.system(cmd)
        assert(rc == 0)
        p.wait()

    def run_nginx1(self):
        name = 'nginx_bench_%d' % (random.randint(1,1000000))
        cmd = './%s run --name=%s -p %d:%d %snginx1' % (self.docker, name, NGINX_PORT, 80, self.registry)
#       cmd = '%s run --name=%s -p %d:%d %snginx1' % (self.docker, name, NGINX_PORT, 80, self.registry)
        print cmd
        p = subprocess.Popen(cmd, shell=True)
        while True:
            try:
                req = urllib2.urlopen('http://localhost:%d'%NGINX_PORT)
                req.close()
                break
            except:
                time.sleep(0.01) # wait 10ms
                pass # retry
        cmd = '%s kill %s' % (self.docker, name)
        rc = os.system(cmd)
        assert(rc == 0)
        p.wait()

    def run_iojs(self):
        name = 'iojs_bench_%d' % (random.randint(1,1000000))
        cmd = '%s run --name=%s -p %d:%d ' % (self.docker, name, IOJS_PORT, 80)
        a = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'iojs')
        a = tmp_copy(a)
        b = '/src'
        cmd += '-v %s:%s ' % (a, b)
        cmd += '%siojs iojs /src/index.js' % self.registry
        print cmd
        p = subprocess.Popen(cmd, shell=True)
        while True:
            try:
                req = urllib2.urlopen('http://localhost:%d'%IOJS_PORT)
                print req.read().strip()
                req.close()
                break
            except:
                time.sleep(0.01) # wait 10ms
                pass # retry
        cmd = '%s kill %s' % (self.docker, name)
        rc = os.system(cmd)
        assert(rc == 0)
        p.wait()

    def run_iojs1(self):
        name = 'iojs_bench_%d' % (random.randint(1,1000000))
        cmd = './%s run --name=%s -p %d:%d ' % (self.docker, name, IOJS_PORT, 80)
#       cmd = '%s run --name=%s -p %d:%d ' % (self.docker, name, IOJS_PORT, 80)
        a = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'iojs')
        a = tmp_copy(a)
        b = '/src'
        cmd += '-v %s:%s ' % (a, b)
        cmd += '%siojs1 iojs /src/index.js' % self.registry
        print cmd
        p = subprocess.Popen(cmd, shell=True)
        while True:
            try:
                req = urllib2.urlopen('http://localhost:%d'%IOJS_PORT)
                print req.read().strip()
                req.close()
                break
            except:
                time.sleep(0.01) # wait 10ms
                pass # retry
        cmd = '%s kill %s' % (self.docker, name)
        rc = os.system(cmd)
        assert(rc == 0)
        p.wait()


    def run_node(self):
        name = 'node_bench_%d' % (random.randint(1,1000000))
        cmd = '%s run --name=%s -p %d:%d ' % (self.docker, name, NODE_PORT, 80)
        a = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'node')
        a = tmp_copy(a)
        b = '/src'
        cmd += '-v %s:%s ' % (a, b)
        cmd += '%snode node /src/index.js' % self.registry
        print cmd
        p = subprocess.Popen(cmd, shell=True)
        while True:
            try:
                req = urllib2.urlopen('http://localhost:%d'%NODE_PORT)
                print req.read().strip()
                req.close()
                break
            except:
                time.sleep(0.01) # wait 10ms
                pass # retry
        cmd = '%s kill %s' % (self.docker, name)
        rc = os.system(cmd)
        assert(rc == 0)
        p.wait()

    def run_node1(self):
        name = 'node_bench_%d' % (random.randint(1,1000000))
        cmd = './%s run --name=%s -p %d:%d ' % (self.docker, name, NODE_PORT, 80)
#       cmd = '%s run --name=%s -p %d:%d ' % (self.docker, name, NODE_PORT, 80)
        a = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'node')
        a = tmp_copy(a)
        b = '/src'
        cmd += '-v %s:%s ' % (a, b)
        cmd += '%snode1 node /src/index.js' % self.registry
        print cmd
        p = subprocess.Popen(cmd, shell=True)
        while True:
            try:
                req = urllib2.urlopen('http://localhost:%d'%NODE_PORT)
                print req.read().strip()
                req.close()
                break
            except:
                time.sleep(0.01) # wait 10ms
                pass # retry
        cmd = '%s kill %s' % (self.docker, name)
        rc = os.system(cmd)
        assert(rc == 0)
        p.wait()

    def run_registry(self):
        name = 'registry_bench_%d' % (random.randint(1,1000000))
        cmd = '%s run --name=%s -p %d:%d ' % (self.docker, name, REGISTRY_PORT, 5000)
        cmd += '-e GUNICORN_OPTS=["--preload"] '
        cmd += '%sregistry' % self.registry
        print cmd
        p = subprocess.Popen(cmd, shell=True)
        while True:
            try:
                req = urllib2.urlopen('http://localhost:%d'%REGISTRY_PORT)
                print req.read().strip()
                req.close()
                break
            except:
                time.sleep(0.01) # wait 10ms
                pass # retry
        cmd = '%s kill %s' % (self.docker, name)
        rc = os.system(cmd)
        assert(rc == 0)
        p.wait()

    def run_registry1(self):
        name = 'registry_bench_%d' % (random.randint(1,1000000))
        cmd = './%s run --name=%s -p %d:%d ' % (self.docker, name, REGISTRY_PORT, 5000)
#       cmd = '%s run --name=%s -p %d:%d ' % (self.docker, name, REGISTRY_PORT, 5000)
        cmd += '-e GUNICORN_OPTS=["--preload"] '
        cmd += '%sregistry1' % self.registry
        print cmd
        p = subprocess.Popen(cmd, shell=True)
        while True:
            try:
                req = urllib2.urlopen('http://localhost:%d'%REGISTRY_PORT)
                print req.read().strip()
                req.close()
                break
            except:
                time.sleep(0.01) # wait 10ms
                pass # retry
        cmd = '%s kill %s' % (self.docker, name)
        rc = os.system(cmd)
        assert(rc == 0)
        p.wait()


    def run(self, bench):
        name = bench.name
        if name in BenchRunner.ECHO_HELLO:
            self.run_echo_hello(repo=name)
        elif name in BenchRunner.CMD_ARG:
            self.run_cmd_arg(repo=name, runargs=BenchRunner.CMD_ARG[name])
        elif name in BenchRunner.CMD_ARG_WAIT:
            self.run_cmd_arg_wait(repo=name, runargs=BenchRunner.CMD_ARG_WAIT[name])
        elif name in BenchRunner.CMD_STDIN:
            self.run_cmd_stdin(repo=name, runargs=BenchRunner.CMD_STDIN[name])
        elif name in BenchRunner.CUSTOM:
            fn = BenchRunner.__dict__[BenchRunner.CUSTOM[name]]
            fn(self)
        else:
            print 'Unknown bench: '+name
            exit(1)

    def pull(self, bench):
        cmd = '%s pull %s%s' % (self.docker, self.registry, bench.name)
        rc = os.system(cmd)
        assert(rc == 0)

    def push(self, bench):
        cmd = '%s push %s%s' % (self.docker, self.registry, bench.name)
        rc = os.system(cmd)
        assert(rc == 0)

    def tag(self, bench):
        cmd = '%s tag %s%s %s%s' % (self.docker,
                                    self.registry, bench.name,
                                    self.registry2, bench.name)
        rc = os.system(cmd)
        assert(rc == 0)

    def operation(self, op, bench):
        if op == 'run':
            self.run(bench)
        elif op == 'pull':
            self.pull(bench)
        elif op == 'push':
            self.push(bench)
        elif op == 'tag':
            self.tag(bench)
        else:
            print 'Unknown operation: '+op
            exit(1)

def main():
    if len(sys.argv) == 1:
        print 'Usage: bench.py [OPTIONS] [BENCHMARKS]'
        print 'OPTIONS:'
        print '--docker=<binary>'
        print '--registry=<registry>'
        print '--registry2=<registry2>'
        print '--all'
        print '--list'
        print '--list-json'
        print '--op=(run|push|pull|tag)'
        exit(1)

    benches = []
    kvargs = {'out': 'bench.out'}
    # parse args
    for arg in sys.argv[1:]:
        if arg.startswith('--'):
            parts = arg[2:].split('=')
            if len(parts) == 2:
                kvargs[parts[0]] = parts[1]
            elif parts[0] == 'all':
                benches.extend(BenchRunner.ALL.values())
            elif parts[0] == 'list':
                template = '%-16s\t%-20s'
                print template % ('CATEGORY', 'NAME')
                for b in sorted(BenchRunner.ALL.values(), key=lambda b:(b.category, b.name)):
                    print template % (b.category, b.name)
            elif parts[0] == 'list-json':
                print json.dumps([b.__dict__ for b in BenchRunner.ALL.values()])
        else:
            benches.append(BenchRunner.ALL[arg])

    outpath = kvargs.pop('out')
    op = kvargs.pop('op', 'run')
    f = open(outpath, 'w')

    # run benchmarks
    runner = BenchRunner(**kvargs)
    for bench in benches:
        start = time.time()
	print 'elapsed start is ', int(round(start * 1000000))
#	print time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
#	print datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        runner.operation(op, bench)
	end = time.time()
	print 'elapsed end is ',int(round(end * 1000000))
#	print time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
#       print datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        elapsed = end - start

        row = {'repo':bench.repo, 'bench':bench.name, 'elapsed':elapsed}
        js = json.dumps(row)
        print js
        f.write(js+'\n')
        f.flush()
    f.close()

if __name__ == '__main__':
    main()
    exit(0)
