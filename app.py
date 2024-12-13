from flask import Flask, render_template
import sqlite3
import matplotlib.pyplot as plt
import io
import base64
import matplotlib.dates as mdates
from datetime import datetime

app = Flask(__name__)

def get_topics():
    conn = sqlite3.connect('historian_data.db') #connect to the SQLite3 DataBase file
    cursor = conn.cursor()  #create a cursor to execute commands and get data back
    SQL = "SELECT DISTINCT topic FROM historian_data" #define the SQL to get the topics list
    cursor.execute(SQL) #run the SQL command
    topics = [row[0] for row in cursor.fetchall()] #returned results are always placed in an array, extract the first item (topic)
    conn.close() #close the connection
    return topics

def get_data_for_topic(topic):
    conn = sqlite3.connect('historian_data.db') #connect to the SQLite3 DataBase file
    cursor = conn.cursor() #create a cursor to execute commands and get data back
    SQL = "SELECT timestamp, message FROM historian_data WHERE topic = ? ORDER BY timestamp" #SQL to get messages and timestamnps for this topic
    #run the SQL with the topic to complete the SQL command
    #(topic,) ensures that the list provides all the extra useless data needed by the execute function while passing only our topic
    cursor.execute(SQL, (topic,))
    #Store all the records and close the "connection" to the file
    data = cursor.fetchall()
    conn.close() #close the connection
    # empty arrays will hold data
    timestamps = []
    values = []
    text_annotations = []
    #for each record
    for timestamp, message in data:
        timestamps.append(datetime.fromisoformat(timestamp))
        try: #if the data is numeric...
            value = float(message)
            values.append(value)
            text_annotations.append(None)
        except ValueError: # If it's text, store it as an annotation
            values.append(None)  # Use None for text points
            text_annotations.append(f"{topic}: {message}")
    return timestamps, values, text_annotations # return the parallel arrays

@app.route('/')
def plot_data():
    #we will create an image to represent the data plot
    #This creates a new figure (window or page) for plotting.
    # figsize sets the width, height of the figure in inches. Here we set 12 inches wide by 6 inches tall.
    plt.figure(figsize=(12, 6))
    #Get current axes and assign them to axes
    axes = plt.gca()
    axes.clear()

    #get topics from DB
    topics = get_topics()
    #for each topic
    for i, topic in enumerate(topics):
        #get the data
        timestamps, values, text_annotations = get_data_for_topic(topic)
        if not timestamps:
            continue
        # Create arrays for numeric data points
        num_timestamps = []
        num_values = []
        # Create arrays for text annotation points
        text_timestamps = []
        annotations = []
        # Separate numeric and text data
        for ts, val, text in zip(timestamps, values, text_annotations):
            if val is not None:
                num_timestamps.append(ts)
                num_values.append(val)
            if text is not None:
                text_timestamps.append(ts)
                annotations.append(text)
        # Plot numeric data
        if num_timestamps:
            axes.plot(num_timestamps, num_values, label=topic, color=f'C{i}', linewidth=1, marker='.')
        # Add text annotations
        for ts, text in zip(text_timestamps, annotations):
            axes.annotate(text,
                       xy=(ts, axes.get_ylim()[1]),  # Place at top of chart, above the correct timestamp
                       xytext=(0, 10),  # 10 points above
                       textcoords='offset points',
                       ha='center', #horizontal and vertical alignment properties
                       va='bottom',
                       bbox=dict(boxstyle='round,pad=0.2', fc=f'C{i}', alpha=0.5), #box around the annotation
                       rotation=45)
            plt.axvline(x=ts,ymin=0.1, ymax=0.9, color=f'C{i}') #draw a vertical line denoting where the command in the label happened

    #autoformat x axis to be non-overlaping dates
    plt.gcf().autofmt_xdate()
    #Set the date format
    axes.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M:%S'))
    #Add a grid of dashes lines with 70% opacity (alpha)
    plt.grid(True, linestyle='--', alpha=0.7)
    #place the legend upper left a bit outside the plot
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    #Add a title
    plt.title('Historian Data Visualization')
    #add a label to the x axis
    plt.xlabel('Timestamp')
    #add a label to the y axis
    plt.ylabel('Value')
    # Add 20% margins to make room for annotations
    plt.margins(y=0.2)
    #auto-adjust layout to avoid overlapping
    plt.tight_layout()

    #create a space in memory to store the image
    buf = io.BytesIO()
    #save the image to the buffer memory
    plt.savefig(buf, format='png', bbox_inches='tight')
    #close the current plot to free up resources
    plt.close()

    #rewind the buffer to the beginning (to play it again later)
    buf.seek(0)
    #read the image and encode it to base64 for direct output in the web page
    image = base64.b64encode(buf.getvalue()).decode('utf-8')

    #Render the plot.html template with the image in it for the web browser to see
    return render_template('plot.html', image=image)

#make the app run if this is the file Python3 runs
if __name__ == '__main__':
    app.run(debug=True)
