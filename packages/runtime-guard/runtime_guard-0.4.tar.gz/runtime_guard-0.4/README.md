# Runtime-Guard
The RuntimeGuard provides functionality to make sure your algorithm runs fine. it got developed to counter memory exhaustion during training deep learning models. Does not need any dependencies!

It supports RAM, CPU, GPU, mean-loop time, watchdog timer, and memory leak checks.

[\> Documentation <](https://xXAI-botXx.github.io/Runtime-Guard/)

---
### Installation

Just install it over PyPI, no dependencies needed:
```bash
pip install runtime_guard
```

---
### Usage

Three ways to use it:

**Standard**:
```python
import runtime_guard as run

guard = run.RuntimeGuard()

for epoch in epochs:
    for idx, x, y in data:
        guard.start_loop()

        # do work

        guard.update()

    if validate:
        guard.pause()
        # validation
```

**Iterator**-Method:
```python
import runtime_guard as run

guard = run.RuntimeGuard()

for epoch in epochs:
    for idx, x, y in guard(data):
        # do work

    with run.Pause(guard):
        if validate:
            # or just: guard.pause()
            # validation
```

**Context**-Method:
```python
import runtime_guard as run

guard = run.RuntimeGuard()

for epoch in epochs:
    for idx, x, y in data:
        with run.Run(guard):
            # do work

    with run.Pause(guard):
        if validate:
            # or just: guard.pause()
            # validation
```


**Notice** that you can also wrap it around the outer loop but keep in mind that the calls will need much more time. For example if you set `update_every_x_calls` to 50 the guard will check only every 50 epochs.


Real example are in the example notebook at [example.ipynb](https://github.com/xXAI-botXx/Runtime-Guard/blob/main/example.ipynb) which can be runned on Google Coolab.


---
### Argument Parsing (Usage Part II)

```python
import argparse

# Create a parser
parser = argparse.ArgumentParser()

#   example arguments from your application
parser.add_argument('--n_epochs', type=int, default=100, help='number of epochs with the initial learning rate')
parser.add_argument('--lr', type=float, default=0.0002, help='initial learning rate for adam')
parser.add_argument('--use_val_dataset', action='store_true', help='if true, creates a val dataset and evaluates at the end of each epoch')
parser.add_argument('--save_only_best_model', action='store_true', help='decides whether to save latest and best or only best model according to val loss (validation have to be used).')
#   arguments from RuntimeGuard
parser = runtime_guard.add_custom_args(parser)

# Get passed arguments
opt = parser.parse_args()

# Process arguments
if opt.use_runtime_guard:
    guard = run.RuntimeGuard(
        make_ram_check=opt.runtime_guard_make_ram_check,
        max_ram_usage_percentage=opt.runtime_guard_max_ram_usage_percentage,
        make_cpu_check=opt.runtime_guard_make_cpu_check,
        max_cpu_usage=opt.runtime_guard_max_cpu_usage,
        make_gpu_check=opt.runtime_guard_make_gpu_check,
        max_gpu_usage=opt.runtime_guard_max_gpu_usage,
        make_mean_loop_time_check=opt.runtime_guard_make_mean_loop_time_check,
        max_duration_factor_percentage=opt.runtime_guard_max_duration_factor_percentage,
        goal_mean_loop_time=opt.runtime_guard_goal_mean_loop_time,
        mean_loop_time_window_size=opt.runtime_guard_mean_loop_time_window_size,
        make_watchdog_timer_check=opt.runtime_guard_make_watchdog_timer_check,
        max_watchdog_seconds_timeout=opt.runtime_guard_max_watchdog_seconds_timeout,
        watchdog_seconds_waittime=opt.runtime_guard_watchdog_seconds_waittime,
        make_leak_check=opt.runtime_guard_make_leak_check,
        max_leak_mb=opt.runtime_guard_max_leak_mb,
        max_leak_ratio=opt.runtime_guard_max_leak_ratio,
        should_print=opt.runtime_guard_should_print,
        print_every_x_calls=opt.runtime_guard_print_every_x_calls,
        should_log=opt.runtime_guard_should_log,
        log_every_x_calls=opt.runtime_guard_log_every_x_calls,
        warm_up_iter=opt.runtime_guard_warm_up_iter,
        update_every_x_calls=opt.runtime_guard_update_every_x_calls,
        hard_exit=opt.runtime_guard_hard_exit
    )
else:
    guard = run.getDummyGuard()
```


---
### Example Output

```text
Runtime Guard Configuration
- RAM Check: True (max 56.29 GB)
- CPU Check: True (max usage 90.0%)
- GPU Check: True (max usage 90.0%)
- Mean Loop Time Check: True
    -> max_duration_factor_percentage = 3.0
    -> goal_mean_loop_time = 0.0
    -> mean_loop_time_window_size = 50
- Watchdog Timer Check: True
    -> max_watchdog_seconds_timeout = 300
    -> watchdog_seconds_waittime = 30
- Memory Leak Check: True
    -> max_leak_mb = 200.0
    -> max_leak_ratio = 0.2
- Print enabled: False
- Logging enabled: True (every 5000 calls, path='./runtime_guard.log')
- Warm-up iterations: 50
- Update every 50 calls
- Hard exit on failure: False


--------------------------------
Date: 18.12.2025
Time: 23:38
Loops: 5000
    - RAM checked
        -> usage = 13.23 GB / 56.29 GB (23.50%)
    - CPU checked
        -> usage = 6.00%
    - GPU checked (PyTorch)
        -> usage = 0.86 GB / 23.51 GB (3.65%)
    - Mean Loop Time checked
        -> mean time trend = 102.14% compared to the goal loop time
        -> current mean loop duration 0.01 / base mean loop duration 0.01
    - Watchdog is still fine!
    - Leak checked
        -> Growth = 0.03 MB
        -> Ratio  = 0.77%
        -> Top leak sources:
            /home/tippolit/anaconda3/envs/gan/lib/python3.8/site-packages/img_phy_sim/ray_tracing.py:1452: size=26.6 KiB (+8736 B), count=486 (+156), average=56 B
            /home/tippolit/anaconda3/envs/gan/lib/python3.8/tracemalloc.py:532: size=142 KiB (+6016 B), count=2656 (+118), average=55 B
            /home/tippolit/anaconda3/envs/gan/lib/python3.8/site-packages/torch/autograd/function.py:574: size=22.9 KiB (+3920 B), count=309 (+55), average=76 B
            /home/tippolit/anaconda3/envs/gan/lib/python3.8/site-packages/torch/nn/modules/module.py:1553: size=21.2 KiB (+1728 B), count=234 (+36), average=93 B
            /home/tippolit/anaconda3/envs/gan/lib/python3.8/site-packages/torch/nn/modules/container.py:219: size=14.0 KiB (+1728 B), count=212 (+36), average=68 B
            /home/tippolit/anaconda3/envs/gan/lib/python3.8/site-packages/torch/nn/parallel/comm.py:235: size=7872 B (+1472 B), count=123 (+23), average=64 B
            /home/tippolit/src/paired_image-to-image_translation/models/networks.py:536: size=9232 B (+864 B), count=106 (+18), average=87 B
--------------------------------
```


