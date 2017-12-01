#!/usr/bin/env python
import argparse
import json
import os
import sys

from twisted.web import server, resource
from twisted.internet import reactor, endpoints, task, utils
from twisted.python import log


def logmsg(msg):
    log.msg(msg.encode('UTF-8'))


class StateException(Exception):
    pass


class QueuedItem(object):
    domain = None
    mode = None

    def __init__(self, domain, mode):
        self.domain = domain
        self.mode = mode

    def __unicode__(self):
        return u'<%s %s>' % (self.domain, self.mode)

    def __eq__(self, other):
        return self.domain == other.domain and self.mode == other.mode


class State(object):
    busy_rejects = 0
    dupes = 0
    finished = 0
    running_max = 30
    queued_max = 30

    def __init__(self,
                 db_host=None,
                 db_port=None,
                 db_password=None,
                 version_jid=None,
                 version_password=None):
        self.argv = {
            "--db_host": db_host,
            "--db_port": db_port,
            "--db_password": db_password,
            "--version_jid": version_jid,
            "--version_password": version_password,
        }
        self.queue = []
        self.running = []

    def enqueue(self, domain, mode):
        item = QueuedItem(domain, mode)
        if len(self.queue) > self.queued_max:
            logmsg(u"*** too busy, rejecting request for %s" % (item,))
            self.busy_rejects += 1
            raise StateException("It's too busy, try again later.")

        if any(x == item for x in (self.queue + self.running)):
            logmsg(u"*** duplicate request for %s" % (item,))
            self.dupes += 1
            raise StateException(
                "Already processing a request for this domain and type."
            )

        self.queue.append(item)
        logmsg(u"enqueued %s" % (item,))
        self.schedule()

    def child_done(self, exit_code, item):
        logmsg(u"finished %s" % (item,))
        self.finished += 1
        self.running.remove(item)
        self.schedule()

    def report(self):
        return {
            'dupes': self.dupes,
            'busy_rejects': self.busy_rejects,
            'finished': self.finished,
            'queued': len(self.queue),
            'running': len(self.running),
        }

    def run(self, item):
        if len(self.running) >= self.running_max:
            return False

        env = {
            'LD_LIBRARY_PATH': '/usr/local/lib',
        }
        args = [
            '/opt/xmppoke/xmppoke.lua',
            '--cafile=/etc/ssl/certs/ca-certificates.crt',
            '--mode=' + item.mode,
            '-d=15',
            '-v',
            item.domain,
        ]

        for arg, value in self.argv.items():
            if not value:
                continue
            args.append(arg + "=" + value)

        logmsg(u"starting %s" % (item))
        self.running.append(item)
        utils.getProcessValue(
            'luajit',
            args,
            env,
            path="/opt/xmppoke"
        ).addCallback(
            self.child_done,
            item
        )
        return True

    def display_report(self):
        logmsg(repr(self.report()))

    def schedule(self):
        while self.queue and len(self.running) < self.running_max:
            if self.run(self.queue[0]):
                del(self.queue[0])


class QueueRequest(resource.Resource):
    isLeaf = True

    def __init__(self, state):
        self.state = state
        resource.Resource.__init__(self)

    def render_GET(self, request):
        request.setHeader(b"content-type", b"application/json")
        return json.dumps(self.state.report())

    def render_POST(self, request):
        if 'mode' in request.args and 'domain' in request.args:
            mode = request.args['mode'][0].decode('utf-8')
            domain = request.args['domain'][0].decode('utf-8')
            try:
                self.state.enqueue(domain, mode)
                request.setHeader(b"content-type", b"application/json")
                content = {"success": True}
                return json.dumps(content)
            except StateException as e:
                return json.dumps({"success": False, "error": str(e)})
        else:
            request.setHeader(b"content-type", b"application/json")
            content = {"success": False, "error": "Incomplete request."}
            return json.dumps(content)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    args = parser.parse_args()

    port = int(os.environ.get("XMPPOKE_QUEUE_PORT", 1337))
    addr = os.environ.get("XMPPOKE_QUEUE_LISTEN", "127.0.0.1")

    db_host = os.environ.get("XMPPOKE_DB_HOST", None)
    db_port = os.environ.get("XMPPOKE_DB_PORT", None)
    db_password = os.environ.get("XMPPOKE_DB_PASSWORD", None)

    version_jid = os.environ.get("XMPPOKE_VERSION_JID", None)
    version_password = os.environ.get("XMPPOKE_VERSION_PASSWORD", None)

    log.startLogging(sys.stdout)
    state = State(
        db_host=db_host,
        db_port=db_port,
        db_password=db_password,
        version_jid=version_jid,
        version_password=version_password,
    )
    endpoints.serverFromString(
        reactor,
        "tcp:{}:interface={}".format(port, addr)
    ).listen(server.Site(QueueRequest(state)))
    check = task.LoopingCall(state.schedule)
    check.start(5.0)
    check = task.LoopingCall(state.display_report)
    check.start(300.0)
    reactor.run()
