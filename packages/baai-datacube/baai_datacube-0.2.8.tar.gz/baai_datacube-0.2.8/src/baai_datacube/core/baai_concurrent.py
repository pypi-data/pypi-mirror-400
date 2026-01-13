from concurrent.futures import ThreadPoolExecutor as BaseThreadPoolExecutor, _base
import threading
import weakref
import queue


_threads_queues = weakref.WeakKeyDictionary()
_shutdown = False


def _worker(executor_reference, work_queue, initializer, initargs):
    if initializer is not None:
        try:
            initializer(*initargs)
        except BaseException:
            _base.LOGGER.critical('Exception in initializer:', exc_info=True)
            executor = executor_reference()
            if executor is not None:
                executor._initializer_failed()
            return
    try:
        while True:
            try:
                work_item = work_queue.get_nowait()
            except queue.Empty:
                # attempt to increment idle count if queue is empty
                executor = executor_reference()
                if executor is not None:
                    executor._idle_semaphore.release()
                del executor
                work_item = work_queue.get(block=True)

            if work_item is not None:
                work_item.run()
                # Delete references to object. See GH-60488
                del work_item
                continue

            executor = executor_reference()
            # Exit if:
            #   - The interpreter is shutting down OR
            #   - The executor that owns the worker has been collected OR
            #   - The executor that owns the worker has been shutdown.
            if _shutdown or executor is None or executor._shutdown:
                # Flag the executor as shutting down as early as possible if it
                # is not gc-ed yet.
                if executor is not None:
                    executor._shutdown = True
                # Notice other workers
                work_queue.put(None)
                return
            del executor
    except BaseException: # noqa
        _base.LOGGER.critical('Exception in worker', exc_info=True)


class ThreadPoolExecutor(BaseThreadPoolExecutor):

    def _adjust_thread_count(self):
        # if idle threads are available, don't spin new threads
        if self._idle_semaphore.acquire(timeout=0):
            return

        # When the executor gets lost, the weakref callback will wake up
        # the worker threads.
        def weakref_cb(_, q=self._work_queue):
            q.put(None) # noqa

        num_threads = len(self._threads)
        if num_threads < self._max_workers:
            thread_name = '%s_%d' % (self._thread_name_prefix or self,
                                     num_threads)
            t = threading.Thread(name=thread_name, target=_worker, daemon=True,
                                 args=(weakref.ref(self, weakref_cb),
                                       self._work_queue,
                                       self._initializer,
                                       self._initargs))
            t.start()
            self._threads.add(t) # noqa
            _threads_queues[t] = self._work_queue
