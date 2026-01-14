import logging
import time

logger = logging.getLogger(__name__)


def limit_job_speed(max_job_speed, job_step=1):
    """
    ``limit_job_speed`` is a worker that limits the speed at which jobs are processed.
    It falls into sleep if the job throughput exceeds the specified value::

        k3jobq.run(range(1000), [
                (k3jobq.limit_job_speed(100, 1), 1), # execute 100 job per second
                (empty, 10),
        ])

    Args:
        max_job_speed(float): is a float or function, represents the maximum
            execution job speed. If it is a function, use the return value of the
            function.

        job_step(int): represents the step length of a job, the default is 1.

    Returns:
        the ``args`` passed in.
    """

    speed_stat = {
        "start_time": time.time(),
        "job_num": 0,
        "tick_time": 5,
    }

    def _limit(job_args):
        try:
            max_speed = max_job_speed
            if callable(max_job_speed):
                max_speed = max_job_speed()

            speed_stat["job_num"] += job_step

            min_ts = speed_stat["job_num"] * 1.0 / max_speed
            itv_ts = time.time() - speed_stat["start_time"]
            if itv_ts < min_ts:
                time.sleep(min_ts - itv_ts)

            now = time.time()
            if now - speed_stat["start_time"] >= speed_stat["tick_time"]:
                speed = speed_stat["job_num"] * 1.0 / (now - speed_stat["start_time"])

                logger.info(
                    "current speed: {speed}/s max_speed:{max_speed}/s job_num:{job_num} start_time:{start_time}".format(
                        speed=round(speed, 3),
                        max_speed=max_speed,
                        job_num=speed_stat["job_num"],
                        start_time=speed_stat["start_time"],
                    )
                )

                speed_stat["start_time"] = now
                speed_stat["job_num"] = 0

        except Exception as e:
            logger.exception("error occurred limit job speed: " + repr(e))

        return job_args

    return _limit
