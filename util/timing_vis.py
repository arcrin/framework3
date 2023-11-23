import matplotlib.pyplot as plt
import datetime
from util.async_timing import task_timing

# fig, ax = plt.subplots()

# for i, task in enumerate(task_timing):
#     start_time_seconds = task["start_time"].minute * 60 + task["start_time"].second
#     end_time_seconds = task["end_time"].minute * 60 + task["end_time"].second
#     execution_time_seconds = end_time_seconds - start_time_seconds
#     ax.barh(i, execution_time_seconds, left=start_time_seconds)

# ax.set_yticks(range(len(tasks)))
# ax.set_yticklabels([task["task"] for task in tasks])
# ax.set_xlabel("Seconds")
# ax.set_title("Function Execution Timeline")

# plt.savefig('function_execution_timeline.pdf')

# plt.show()

def plot_task_timing():
    fig, ax = plt.subplots()

    for i, task in enumerate(task_timing):
        start_time_seconds = task["start_time"] - task_timing[0]["start_time"]
        end_time_seconds = task["end_time"] - task_timing[0]["start_time"]
        execution_time_seconds = end_time_seconds - start_time_seconds
        ax.barh(i, execution_time_seconds, left=start_time_seconds)

    ax.set_yticks(range(len(task_timing)))
    ax.set_yticklabels([task["task"] for task in task_timing])
    ax.set_xlabel("Seconds")
    ax.set_title("Function Execution Timeline")

    plt.savefig('function_execution_timeline.pdf')
    # plt.show()
    