"""
Visualize data from the all fog experiment.

"""

import matplotlib.pyplot as pyplot

# Helper indexes
cloud_n_index = 0
cloud_error_index = 1
cloud_upload_time_index = 2
cloud_bluetooth_time_index = 3
cloud_pi_compute_time_index = 4
cloud_lambda_compute_time_index = 5

def extract_all_cloud_data():
    with open('all_cloud_stats.txt', 'r') as data_file:
        labels = data_file.readline().split()

        n_data = []
        error_data = []
        upload_time_data = []
        bluetooth_time_data = []
        pi_compute_time_data = []
        lambda_compute_time_data = []
        
        for next_line in data_file:
            items = next_line.split()
            n_data.append(items[cloud_n_index])
            error_data.append(items[cloud_error_index])
            upload_time_data.append(items[cloud_upload_time_index])
            bluetooth_time_data.append(items[cloud_bluetooth_time_index])
            pi_compute_time_data.append(items[cloud_pi_compute_time_index])
            lambda_compute_time_data.append(items[cloud_lambda_compute_time_index])

        return n_data, error_data, upload_time_data, bluetooth_time_data, pi_compute_time_data, lambda_compute_time_data

    

def plot_data(list_of_double_lists, title, labels, xlabel="N used for Prediction", 
                ylabel="Duration (s)", scatter_plots=True):
    pyplot.figure()
    pyplot.rcParams.update({'figure.figsize': [0.6, 1.4]})
    pyplot.rcParams.update({'font.size': 22})
    pyplot.xlabel(xlabel, fontsize = 25)
    pyplot.ylabel(ylabel, fontsize = 25)
    pyplot.title(title, fontsize = 25)
    pyplot.grid(True)

    for i in range(len(list_of_double_lists)):
        if scatter_plots:
            pyplot.scatter(list_of_double_lists[i][0], list_of_double_lists[i][1], label=labels[i])
        else:
            pyplot.plot(list_of_double_lists[i][0], list_of_double_lists[i][1], label=labels[i])

    pyplot.legend(loc="best")
    pyplot.show()

def visualize_all_cloud():
    all_cloud_stats = extract_all_cloud_data()
    data_to_plot = [
        [all_cloud_stats[cloud_n_index], all_cloud_stats[cloud_pi_compute_time_index]],
        [all_cloud_stats[cloud_n_index], all_cloud_stats[cloud_lambda_compute_time_index]]
    ]
    labels = ["Local", "Cloud"]
    plot_data(
        data_to_plot, 
        "Computation Time Spent on Local vs on the Cloud", 
        labels
    )

if __name__ == "__main__":
    visualize_all_cloud()