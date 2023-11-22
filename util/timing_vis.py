import matplotlib.pyplot as plt
import datetime

# Define the tasks and their start/end times
tasks = [
    {"task": "Task 1", "start_time": datetime.time(0, 0, 0), "end_time": datetime.time(0, 0, 2)},
    {"task": "Task 2", "start_time": datetime.time(0, 0, 2), "end_time": datetime.time(0, 0, 5)},
    {"task": "Task 3", "start_time": datetime.time(0, 0, 5), "end_time": datetime.time(0, 0, 6)},
]

# Create a Matplotlib figure
fig, ax = plt.subplots()

# Plot the tasks as horizontal bars
for i, task in enumerate(tasks):
    start_time_seconds = task["start_time"].minute * 60 + task["start_time"].second
    end_time_seconds = task["end_time"].minute * 60 + task["end_time"].second
    execution_time_seconds = end_time_seconds - start_time_seconds
    ax.barh(i, execution_time_seconds, left=start_time_seconds)

# Customize the plot
ax.set_yticks(range(len(tasks)))
ax.set_yticklabels([task["task"] for task in tasks])
ax.set_xlabel("Seconds")
ax.set_title("Function Execution Timeline")

# Save the plot as a PDF file
plt.savefig('function_execution_timeline.pdf')

# Show the plot
plt.show()