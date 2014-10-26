from unittest import TestCase, main

from seas.zutil import mdp


class TestMajorDomo(TestCase):

    def setUp(self):
        self.uri = 'inproc://mdp-test'
        self.broker = mdp.MajorDomoBroker(
            self.uri,
            poll_interval=0.1)
        self.broker_reactor = self.broker.reactor()
        self.broker_reactor.next()

    def tearDown(self):
        self.broker.stop()
        list(self.broker_reactor)
        self.broker.destroy()

    def test_setup(self):
        pass

class TestMajorDomoClient(TestMajorDomo):

    def test_client_queued(self):
        cli = mdp.MajorDomoClient(self.uri)
        cli.send_async('echo', 'hello')
        self.broker_reactor.next()
        service = self.broker.require_service('echo')
        self.assertEqual(len(service.requests), 1)
        cli.destroy()

    def test_client_retries(self):
        cli = mdp.MajorDomoClient(self.uri, timeout=0, retries=1)
        self.assertRaises(mdp.err.MaxRetryError, cli.send, 'echo', 'hello')
        self.broker_reactor.next()
        self.broker_reactor.next()
        service = self.broker.require_service('echo')
        self.assertEqual(len(service.requests), 2)
        cli.destroy()

class TestMajorDomoWorker(TestMajorDomo):

    def setUp(self):
        super(TestMajorDomoWorker, self).setUp()
        self.worker = mdp.MajorDomoWorker(self.uri, 'echo', _echo)
        self.worker_reactor = self.worker.reactor()
        self.worker_reactor.next()

    def tearDown(self):
        self.worker.stop()
        list(self.worker_reactor)
        self.worker.destroy()
        super(TestMajorDomoWorker, self).tearDown()

    def test_setup(self):
        pass

    def test_service_registered(self):
        self.broker_reactor.next()  # handle registration
        service = self.broker.require_service('echo')
        self.assertEqual(len(service.workers), 1)


class TestRoundTrip(TestMajorDomoWorker):

    def setUp(self):
        super(TestRoundTrip, self).setUp()
        self.client = mdp.MajorDomoClient(self.uri)

    def test_echo(self):
        req = self.client.send_async('echo', 'hello')
        self.broker_reactor.next()
        self.worker_reactor.next()
        self.assertEqual(req.recv(), ['hello'])


def _echo(message):
    return [message]

if __name__ == '__main__':
    main()
