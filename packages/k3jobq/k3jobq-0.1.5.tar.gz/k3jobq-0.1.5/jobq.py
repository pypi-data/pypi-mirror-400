import logging
import threading
import time
import types
import queue

import k3thread


logger = logging.getLogger(__name__)


class EmptyRst(object):
    """
    A worker function return this value to cancel a task.
    By returning ``EmptyRst``, nothing is passed to next worker group::

        def worker_back_hole(args):
            return k3jobq.EmptyRst

    If ``None`` is returned by a worker, ``None`` is passed to next worker.
    """


class Finish(object):
    pass


class JobWorkerError(Exception):
    pass


class JobWorkerNotFound(JobWorkerError):
    pass


class WorkerGroup(object):
    def __init__(self, index, worker, n_thread, input_queue, dispatcher, probe, keep_order):
        self.index = index
        self.worker = worker
        self.n_thread = n_thread
        self.input_queue = input_queue
        self.output_queue = _make_q()
        self.dispatcher = dispatcher
        self.probe = probe
        self.keep_order = keep_order

        self.threads = {}

        # When exiting, it is not allowed to change thread number.
        # Because we need to send a `Finish` to each thread.
        self.exiting = False

        self.running = True

        # left close, right open: 0 running, n not.
        # Indicate what thread should have been running.
        self.running_index_range = [0, self.n_thread]

        # protect reading/writing worker_group info
        self.worker_group_lock = threading.RLock()

        # dispatcher mode implies keep_order
        if self.dispatcher is not None or self.keep_order:
            need_coordinator = True
        else:
            need_coordinator = False

        # Coordinator guarantees worker-group level first-in first-out, by put
        # output-queue into a queue-of-output-queue.
        if need_coordinator:
            # to maximize concurrency
            self.queue_of_output_q = _make_q(n=1024 * 1024)

            # Protect input.get() and ouput.put(), only used by non-dispatcher
            # mode
            self.keep_order_lock = threading.RLock()

            self.coordinator_thread = start_thread(self._coordinate)
        else:
            self.queue_of_output_q = None

        # `dispatcher` is a user-defined function to distribute args to workers.
        # It accepts the same args passed to worker and returns a number to
        # indicate which worker to used.
        if self.dispatcher is not None:
            self.dispatch_queues = []
            for i in range(self.n_thread):
                self.dispatch_queues.append(
                    {
                        "input": _make_q(),
                        "output": _make_q(),
                    }
                )
            self.dispatcher_thread = start_thread(self._dispatch)

        self.add_worker_thread()

    def add_worker_thread(self):
        with self.worker_group_lock:
            if self.exiting:
                logger.info("worker_group exiting. Thread number change not allowed")
                return

            s, e = self.running_index_range

            for i in range(s, e):
                if i not in self.threads:
                    if self.keep_order:
                        th = start_thread(self._exec_in_order, self.input_queue, _make_q(), i)
                    elif self.dispatcher is not None:
                        # for worker group with dispatcher, threads are added for the first time
                        assert s == 0
                        assert e == self.n_thread
                        th = start_thread(
                            self._exec, self.dispatch_queues[i]["input"], self.dispatch_queues[i]["output"], i
                        )
                    else:
                        th = start_thread(self._exec, self.input_queue, self.output_queue, i)

                    self.threads[i] = th

    def _exec(self, input_q, output_q, thread_index):
        while self.running:
            # If this thread is not in the running thread range, exit.
            if thread_index < self.running_index_range[0]:
                with self.worker_group_lock:
                    del self.threads[thread_index]

                logger.info("worker-thread {i} quit".format(i=thread_index))
                return

            args = input_q.get()
            if args is Finish:
                return

            with self.probe["probe_lock"]:
                self.probe["in"] += 1

            try:
                rst = self.worker(args)
            except Exception as e:
                logger.exception(repr(e))
                continue

            finally:
                with self.probe["probe_lock"]:
                    self.probe["out"] += 1

            # If rst is an iterator, it procures more than one args to next job.
            # In order to be accurate, we only count an iterator as one.

            _put_rst(output_q, rst)

    def _exec_in_order(self, input_q, output_q, thread_index):
        while self.running:
            if thread_index < self.running_index_range[0]:
                with self.worker_group_lock:
                    del self.threads[thread_index]

                logger.info("in-order worker-thread {i} quit".format(i=thread_index))
                return

            with self.keep_order_lock:
                args = input_q.get()
                if args is Finish:
                    return
                self.queue_of_output_q.put(output_q)

            with self.probe["probe_lock"]:
                self.probe["in"] += 1

            try:
                rst = self.worker(args)

            except Exception as e:
                logger.exception(repr(e))
                output_q.put(EmptyRst)
                continue

            finally:
                with self.probe["probe_lock"]:
                    self.probe["out"] += 1

            output_q.put(rst)

    def _coordinate(self):
        while self.running:
            outq = self.queue_of_output_q.get()
            if outq is Finish:
                return

            _put_rst(self.output_queue, outq.get())

    def _dispatch(self):
        while self.running:
            args = self.input_queue.get()
            if args is Finish:
                return

            n = self.dispatcher(args)
            n = n % self.n_thread

            queues = self.dispatch_queues[n]
            inq, outq = queues["input"], queues["output"]

            self.queue_of_output_q.put(outq)
            inq.put(args)


class JobManager(object):
    """
    JobManager is the internal impl of ``run`` and let user separate worker
    management and input management. E.g., ``run(range(3), [_echo])`` is same as::

        def _echo(args):
            print args
            return args

        jm = k3jobq.JobManager([_echo])
        for i in range(3):
            jm.put(i)

        jm.join()

    ``JobManager`` creates threads for worker functions, and wait for input to
    be fed with ``JobManager.put()``.

    The arguments are the same as `k3jobq.run`.
    """

    def __init__(self, workers, queue_size=1024, probe=None, keep_order=False):
        if probe is None:
            probe = {}

        self.workers = workers
        self.head_queue = _make_q(queue_size)
        self.probe = probe
        self.keep_order = keep_order

        self.worker_groups = []

        self.probe.update(
            {
                "worker_groups": self.worker_groups,
                "probe_lock": threading.RLock(),
                "in": 0,
                "out": 0,
            }
        )

        self.make_worker_groups()

    def make_worker_groups(self):
        inq = self.head_queue

        workers = self.workers + [_blackhole]
        for i, worker in enumerate(workers):
            if callable(worker):
                worker = (worker, 1)

            # worker callable, n_thread, dispatcher
            worker = (worker + (None,))[:3]

            worker, n, dispatcher = worker

            wg = WorkerGroup(i, worker, n, inq, dispatcher, self.probe, self.keep_order)

            self.worker_groups.append(wg)
            inq = wg.output_queue

    def set_thread_num(self, worker, n):
        """
        Change number of threads for a worker on the fly.

        If job manager has called ``JobManager.join()``.
        ``set_thread_num`` does nothing and just returns silently.

        When thread number is increased, new threads are created.
        If thread number is reduced, we do not stop worker thread in this
        function.
        Because we do not have a steady way to shutdown a running thread in
        python.
        Worker thread checks if it should continue running in _exec() and
        _exec_in_order(), by checking its thread_index against running thread
        index range ``running_index_range``.

        Args:

            worker:
                is the callable passed in when creating JobManager.
                It searches in job manager for the worker.
                If there is not such a worker ``is`` the one passed in, it raise a
                ``JobWorkerNotFound`` error.

            n(int): specifies the expected number of threads for this ``worker``.
                New threads are created and started before this function returns.
                The threads that will be removed are removed after they finishes
                the job they are doing.

        Returns:
            None
        """

        assert n > 0
        assert isinstance(n, int)

        for wg in self.worker_groups:
            """
            In python2, `x = X(); x.meth is x.meth` results in a `False`.
            Every time to retrieve a method, python creates a new **bound** function.

            We must use == to test function equality.

            See https://stackoverflow.com/questions/15977808/why-dont-methods-have-reference-equality
            """

            if wg.worker != worker:
                continue

            if wg.dispatcher is not None:
                raise JobWorkerError("worker-group with dispatcher does not allow to change thread number")

            with wg.worker_group_lock:
                if wg.exiting:
                    logger.info("worker group exiting. Thread number change not allowed")
                    break

                s, e = wg.running_index_range
                oldn = e - s

                if n < oldn:
                    s += oldn - n
                elif n > oldn:
                    e += n - oldn
                else:
                    break

                wg.running_index_range = [s, e]
                wg.add_worker_thread()

                logger.info(
                    "thread number is set to {n}, thread index: {idx}, running threads: {ths}".format(
                        n=n,
                        idx=list(range(wg.running_index_range[0], wg.running_index_range[1])),
                        ths=sorted(wg.threads.keys()),
                    )
                )
                break

        else:
            raise JobWorkerNotFound(worker)

    def put(self, elt):
        """
        Put anything as an input element.
        """
        self.head_queue.put(elt)

    def join(self, timeout=None):
        """
        Wait for all worker to finish.

        Args:
            timeout(float): is the same as `k3jobq.run`

        Returns:
            None
        """

        endtime = time.time() + (timeout or 86400 * 365)

        for wg in self.worker_groups:
            with wg.worker_group_lock:
                # prevent adding or removing thread
                wg.exiting = True
                ths = list(wg.threads.values())

            if wg.dispatcher is None:
                # put nr = len(threads) Finish
                for th in ths:
                    wg.input_queue.put(Finish)
            else:
                wg.input_queue.put(Finish)
                # wait for dispatcher to finish or jobs might be lost
                wg.dispatcher_thread.join(endtime - time.time())

                for qs in wg.dispatch_queues:
                    qs["input"].put(Finish)

            for th in ths:
                th.join(endtime - time.time())

            if wg.queue_of_output_q is not None:
                wg.queue_of_output_q.put(Finish)
                wg.coordinator_thread.join(endtime - time.time())

            # if join timeout, let threads quit at next loop
            wg.running = False

    def stat(self):
        return stat(self.probe)


def run(input_it, workers, keep_order=False, timeout=None, probe=None):
    """
    Process element in ``input`` one by one with functions in ``workers``.

    Args:

        input(iterable): input elts to process.

        workers: list of functions, or ``tuple`` of ``(function, nr_of_thread)``,
            or ``tuple`` of ``(function, nr_of_thread, dispatcher_func)``.

            A worker function accepts exactly one argument and return one value.
            The argument is one elt from input(the first worker) or a result
            from the previous worker.
            A typical worker would be defined like::

                def worker_foo(args):
                    result = foo(args)
                    return result

            A worker function can also be an iterator, in which case, k3jobq
            iterates all elements from returned iterator and pass it to next
            worker::

                def worker_iter(args):
                    for elt in args:
                        yield elt

            A ``dispatcher`` is specified by user to control how to dispatch args to
            different workers.
            It accepts one argument ``args``, same as the ``args`` passed to a worker
            function,  and return a ``int`` indicating which of next workers to used.
            A ``dispatcher`` is used to balance related work load to workers.

            A dispatcher function may be defined like::

                def dispatch(args):
                    return hash(args) % 5

            A user-defined dipatcher is used when **concurrency** and **partial-order**
            are both required:

            -   The ``args`` passed to a same worker is guaranteed to be
                executed in order.

            -   While different workers runs in parallel.

            If a ``dispatcher`` specified, it implies ``keep_order=True``.

            Thus a worker group with dispatcher also put result into the input
            queue of next worker group with order kept.

        keep_order(bool): specifies whether elements must be processed in order.
            Keeping them in order affects performance. By default it is ``False``.

        timeout(float): specifies the max time to run. ``None`` means to wait
            until all jobs are done. By default it is ``None``.

            If k3jobq exceeds ``timeout`` before finishing, it returns after all workers
            finishing their current job.

        probe: is a dictionary to collect stats. By defaul it is ``None``.
            If it is a valid dictionary, ``k3jobq`` writes stats of running jobs to it.
            ``k3jobq.stat()`` can be used to obtain stat data.

    Returns:
        None
    """

    mgr = JobManager(workers, probe=probe, keep_order=keep_order)

    try:
        for args in input_it:
            mgr.put(args)

    finally:
        mgr.join(timeout=timeout)


def stat(probe):
    """
    Get stat about a running or finished k3jobq session.
    stat returned is in a dictionary like::

        {
            'in': 10,       # number of elements all workers started processing.
            'out': 8,       # number of elements all workers finished processing.
            'doing': 2,     # number of elements all workers is processing.
            'workers': [
                {
                    'name': 'example.worker_foo',
                    'input': {'size': 3, 'capa': 1024}, # input queue
                    'nr_worker': 2,                     # number of worker thread
                    'coordinator': {'size': 3, 'capa': 1024}, # presents only when keep_order=True
                },
                ...
            ]
        }

    Args:
        probe(dict): is the dictionary passed into ``k3jobq.run``.

    Returns:
        dict of stat.
    """

    with probe["probe_lock"]:
        rst = {
            "in": probe["in"],
            "out": probe["out"],
            "doing": probe["in"] - probe["out"],
            "workers": [],
        }

    # exclude the _start and _end
    for wg in probe["worker_groups"][:-1]:
        o = {}
        wk = wg.worker
        o["name"] = (wk.__module__ or "builtin") + ":" + wk.__name__
        o["input"] = _q_stat(wg.input_queue)
        if wg.dispatcher is not None:
            o["dispatcher"] = [
                {
                    "input": _q_stat(qs["input"]),
                    "output": _q_stat(qs["output"]),
                }
                for qs in wg.dispatch_queues
            ]

        if wg.queue_of_output_q is not None:
            o["coordinator"] = _q_stat(wg.queue_of_output_q)

        s, e = wg.running_index_range
        o["nr_worker"] = e - s

        rst["workers"].append(o)

    return rst


def _q_stat(q):
    return {"size": q.qsize(), "capa": q.maxsize}


def _put_rst(output_q, rst):
    if isinstance(rst, types.GeneratorType):
        for rr in rst:
            _put_non_empty(output_q, rr)
    else:
        _put_non_empty(output_q, rst)


def _blackhole(args):
    return EmptyRst


def _put_non_empty(q, val):
    if val is not EmptyRst:
        q.put(val)


def _make_q(n=1024):
    return queue.Queue(n)


def start_thread(exec_func, *args):
    # `thread_index` identifying a thread in worker_group.threads.
    # It is used to decide which thread to remove.
    return k3thread.daemon(exec_func, args=args)
